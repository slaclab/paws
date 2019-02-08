from __future__ import print_function
from collections import OrderedDict
import os
import copy
import time
from threading import Condition

import numpy as np

from .PawsPlugin import PawsPlugin
from .MitosPPumpController import MitosPPumpController
from .CryoConController import CryoConController

class FlowReactor(PawsPlugin):

    def __init__(self,timer,ppumps_setup,cryocon_setup={},bad_flow_tol=100,verbose=False,log_file=None):
        """Create a FlowReactor control plugin.

        Parameters
        ----------
        timer : paws.plugins.Timer.Timer
        ppumps_setup : dict
        cryocon_setup : dict
        bad_flow_tol : int
        verbose : bool
        log_file : str
        """
        super(FlowReactor,self).__init__(thread_blocking=True,verbose=verbose,log_file=log_file)
        self.timer = timer
        self.ppumps_setup = ppumps_setup 
        self.cryocon_setup = cryocon_setup 
        self.bad_flow_tol = bad_flow_tol
        self.state_lock = Condition()
        self.state = {}

    def start(self):
        super(FlowReactor,self).start()
        with self.thread_clone.running_lock:
            self.thread_clone.running_lock.wait()
        self.add_to_history('Started FlowReactor')

    @classmethod
    def clone(cls,timer,ppumps_setup,cryocon_setup={},bad_flow_tol=100,verbose=False,log_file=None):
        return cls(timer,ppumps_setup,cryocon_setup,bad_flow_tol,verbose,log_file)

    def build_clone(self):
        cln = self.clone(self.timer,self.ppumps_setup,self.cryocon_setup,self.bad_flow_tol,self.verbose)
        return cln 

    def run(self):
        # set up internal PPumpController plugins
        self.ppumps = dict.fromkeys(self.ppumps_setup.keys())
        self.volume_limits = dict.fromkeys(self.ppumps_setup.keys())
        for pump_nm, pump_cfg in self.ppumps_setup.items():
            flow_tbl = np.loadtxt(pump_cfg['calibration_file'])
            self.ppumps[pump_nm] = MitosPPumpController(
                timer=self.timer,
                serial_device=pump_cfg['device'],
                flowrate_table=flow_tbl,
                verbose=False,log_file=None
                )
            if 'volume_limit' in pump_cfg: 
                self.volume_limits[pump_nm] = pump_cfg['volume_limit']
        # set up internal CryoConController plugin
        self.cryo=None
        if self.cryocon_setup:
            self.cryo = CryoConController(
                timer=self.timer,
                host=self.cryocon_setup['host'],
                port=self.cryocon_setup['port'],
                channels=self.cryocon_setup['channels'],
                verbose=False,log_file=None
                )
            self.cryo.start()
            for chan in self.cryo.channels.keys():
                self.cryo.set_units(chan,'C')
                self.cryo.loop_setup(chan,'RAMPP')
                self.cryo.set_temperature(chan,25.)
        # to be executed by thread_clone
        v_delivered = dict.fromkeys(self.volume_limits.keys())
        for k in v_delivered.keys(): v_delivered[k] = 0.
        keep_going = True
        stop_flag = False
        timer_dt_minutes = float(self.timer.dt)/60.
        for nm,ppc in self.ppumps.items():
            ppc.start()
            #ppc.set_flowrate(0.)
            ppc.set_idle()
        # self.proxy will be waiting for run_notify()...
        self.run_notify()
        # start temperature control loop now
        self.cryo.start_control()
        bad_flow_count = 0
        while keep_going: 
            with self.timer.dt_lock:
                self.timer.dt_lock.wait()
            # log the flow rates and temperature,
            # check for anomalies in flow rates,
            # stop the reactor if bad flow 
            ok_flag,statstr,statdict = self._clone_check_status()
            if ok_flag:
                bad_flow_count = 0
            else:
                bad_flow_count += 1
                if bad_flow_count >= self.bad_flow_tol:
                    if self.verbose: self.message_callback('Bad flow detected: stopping FlowReactor')
                    stop_flag = True

            # checked delivered volume for each pump, if limits are specified       
            for pump_nm, lmt in self.volume_limits.items():
                if lmt: 
                    # get the true ul/m flowrate from statdict
                    fr = statdict['{}_flowrate'.format(pump_nm)]
                    # add flowrate * dt in minutes to delivered volume 
                    v_delivered[pump_nm] += fr*timer_dt_minutes
                    # check if v_delivered[pump_nm] >= lmt: if so, throw the stop.
                    if v_delivered[pump_nm] >= lmt:
                        stop_flag = True
                        if self.verbose: self.message_callback(
                            '{} volume limit reached ({}/{}): stopping FlowReactor'.format(
                            pump_nm,v_delivered[pump_nm],lmt))

            if stop_flag:
                with self.proxy.running_lock:
                    self.proxy.stop()
             
            with self.timer.running_lock:
                if not self.timer.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        if self.verbose: self.message_callback('Stopping FlowReactor')
        # stop cryocon loop
        if self.cryo:
            if self.verbose: self.message_callback('Stopping CryoCon control loop')
            self.cryo.stop_control() 
            #self.cryo.stop()
        # set pumps to idle
        self.vent_pumps()
        #ppc.stop()
        #with self.proxy.history_lock:
        self.proxy.add_to_history('STOP')
        self.proxy.dump_history()

    def vent_pumps(self):
        for nm,ppc in self.thread_clone.ppumps.items():
            if self.verbose: self.message_callback('Setting pump {} to idle'.format(nm))
            try:
                ppc.set_idle()
            except:
                pass

    def set_recipe(self,recipe):
        self.thread_clone._clone_set_recipe(recipe)
        if self.verbose: self.message_callback(self.prettyprint_recipe(recipe))
        self.add_to_history(self.prettyprint_recipe(recipe))

    def _clone_set_recipe(self,recipe):
        for chan,loop_idx in self.cryo.channels.items():
            if loop_idx is not None:
                if 'T_ramp' in recipe:
                    self.cryo.set_ramp_rate(chan,recipe['T_ramp'])
                if 'T_set' in recipe:
                    # NOTE: this is a little dance to circumvent a problem with the CryoCon,
                    # where it sometimes ignores the ramp rate 
                    with self.cryo.state_lock:
                        T_current = self.cryo.state['T_read_{}'.format(chan)]
                    self.cryo.set_temperature(chan,T_current)
                    T_inter = T_current + (recipe['T_set']-T_current)*0.1
                    self.cryo.set_temperature(chan,T_inter)
                    time.sleep(5)
                    self.cryo.set_temperature(chan,recipe['T_set'])
        for itm_nm, val in recipe.items():
            if '_flowrate' in itm_nm:
                pump_nm = itm_nm[:itm_nm.find('_flowrate')]
                if self.verbose: self.message_callback('setting {} to {}/min'.format(pump_nm,val))
                self.ppumps[pump_nm].set_flowrate(val)
        rcp_str = self.prettyprint_recipe(recipe)
        if self.verbose: self.message_callback(rcp_str)

    @staticmethod
    def prettyprint_recipe(rcp):
        rcp_str = ''
        if 'T_set' in rcp:
            rcp_str += os.linesep+'T_set: {}'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += os.linesep+'T_ramp: {}/min'.format(rcp['T_ramp'])
        for itm_nm, val in rcp.items():
            if '_flowrate' in itm_nm:
                pump_nm = itm_nm[:itm_nm.find('_flowrate')]
                rcp_str += os.linesep+'{} flow rate: {}'.format(pump_nm,val) 
        return rcp_str

    def _clone_check_status(self):
        # to be executed by thread_clone
        ok_flag = True
        stat_str = ''
        stat_dict = {}
        if self.cryo:
            with self.cryo.state_lock:
                for chan,idx in self.cryo.channels.items():
                    T_read_key = 'T_read_{}'.format(chan)
                    T_read = copy.copy(self.cryo.state[T_read_key])
                    stat_dict[T_read_key] = float(T_read)
                    stat_str += 'T_{}: {}, '.format(chan,T_read)
        for nm, ppc in self.ppumps.items():
            with ppc.state_lock:
                setpt_pls = copy.copy(ppc.state['target_flow_rate'])
                frt_pls = copy.copy(ppc.state['flow_rate'])
            if frt_pls is not None:
                frt_ulm = frt_pls*60/1.E6
                truefrt_ulm = ppc.get_true_flowrate(frt_ulm)
                setpt_ulm = setpt_pls*60/1.E6
                truesetpt_ulm = ppc.get_true_flowrate(setpt_ulm)
                stat_dict['{}_flowrate'.format(nm)] = float(truefrt_ulm)
                stat_dict['{}_setpoint'.format(nm)] = float(truesetpt_ulm)
                stat_str += ' {}: {} (setpt {}), '.format(nm,truefrt_ulm,truesetpt_ulm)
                if setpt_pls:
                    ok_flag = True
                    if setpt_pls == 0:
                        if abs(truefrt_ulm-truesetpt_ulm) > 1.0:
                            ok_flag = False
                    elif abs(truefrt_ulm-truesetpt_ulm)/truesetpt_ulm > 0.5 and abs(truefrt_ulm-truesetpt_ulm) > 5.0:
                        ok_flag = False
                    if self.verbose and not ok_flag: 
                        self.message_callback(
                        'ppump {} flowrate {} is far from setpoint {}'
                        .format(nm,truefrt_ulm,truesetpt_ulm))
        #stat_dict['time'] = self.get_date_time() 
        self.proxy.add_to_history(copy.copy(stat_str))
        with self.proxy.state_lock:
            self.proxy.state = copy.deepcopy(stat_dict)
        return ok_flag,stat_str,stat_dict
