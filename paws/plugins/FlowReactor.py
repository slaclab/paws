import copy
import time
from threading import Thread, Condition

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
        super(FlowReactor,self).__init__(verbose=verbose,log_file=log_file)
        self.timer = timer
        self.ppumps_setup = ppumps_setup 
        self.ppumps = dict.fromkeys(self.ppumps_setup.keys())
        self.volume_limits = dict.fromkeys(self.ppumps_setup.keys())
        self.cryocon_setup = cryocon_setup 
        self.cryo = None
        self.bad_flow_tol = bad_flow_tol
        self.state_lock = Condition()
        self.state = {}
        self.controller_thread = None

    def start(self):
        # set up internal PPumpController plugins
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
        for nm,ppc in self.ppumps.items():
            if self.verbose: self.message_callback('starting pump controller: {}'.format(nm))
            ppc.start()
            ppc.set_flowrate(0.)
        # set up internal CryoConController plugin
        if self.cryocon_setup:
            self.cryo = CryoConController(
                timer=self.timer,
                host=self.cryocon_setup['host'],
                port=self.cryocon_setup['port'],
                channels=self.cryocon_setup['channels'],
                verbose=False,log_file=None
                )
            if self.verbose: self.message_callback('starting cryocon controller')
            self.cryo.start()
            for chan in self.cryo.channels.keys():
                self.cryo.set_units(chan,'C')
                self.cryo.loop_setup(chan,'RAMPP')
                self.cryo.set_temperature(chan,25.)
            if self.verbose: self.message_callback('startup complete: running flow reactor')
        super(FlowReactor,self).start()

    def _run(self):
        self.controller_thread = Thread(target=self.run_reactor)
        self.controller_thread.start()
        # block until device control is established: 
        #if self.verbose: self.message_callback('waiting for worker thread run notification...')
        with self.running_lock:
            self.running_lock.wait()
        #if self.verbose: self.message_callback('worker thread run notification received!')

    def run_reactor(self):
        v_delivered = dict.fromkeys(self.volume_limits.keys())
        for k in v_delivered.keys(): v_delivered[k] = 0.
        keep_going = True
        stop_flag = False
        timer_dt_minutes = float(self.timer.dt)/60.
        # start temperature control loop now
        self.cryo.start_control()
        # main thread should be waiting for run_notify()...
        self.run_notify()
        bad_flow_count = 0
        while keep_going: 
            with self.timer.dt_lock:
                self.timer.dt_lock.wait()
            # log the flow rates and temperature,
            # check for anomalies in flow rates,
            # stop the reactor if bad flow 
            ok_flag,statstr,statdict = self.check_status()
            if ok_flag:
                bad_flow_count = 0
            else:
                bad_flow_count += 1
                if bad_flow_count >= self.bad_flow_tol:
                    if self.verbose: self.message_callback('Bad flow detected: stopping FlowReactor')
                    stop_flag = True
            # check delivered volume for each pump, if limits are specified       
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
                self.stop()
            with self.timer.running_lock:
                if not self.timer.running:
                    self.stop()
            with self.running_lock:
                keep_going = bool(self.running)

        if self.verbose: self.message_callback('Stopping FlowReactor')
        # stop cryocon loop
        if self.cryo:
            if self.verbose: self.message_callback('Stopping CryoCon control loop')
            self.cryo.stop_control() 
        self.add_to_history('STOP')
        self.dump_history()

    def get_state(self):
        with self.state_lock:
            st = copy.deepcopy(self.state)
        return st

    def vent_pumps(self):
        for nm,ppc in self.ppumps.items():
            if self.verbose: self.message_callback('Setting pump {} to idle'.format(nm))
            ppc.set_idle()

    def stop_pumps(self):
        for nm,ppc in self.ppumps.items():
            if self.verbose: self.message_callback('Setting pump {} to zero flow'.format(nm))
            ppc.set_flowrate(0.)

    def set_temperature(self,T_set,T_ramp=100.):
        for chan,loop_idx in self.cryo.channels.items():
            self.cryo.set_ramp_rate(chan,T_ramp)
            self.cryo.set_temperature(chan,T_set)

    def set_recipe(self,recipe):
        for chan,loop_idx in self.cryo.channels.items():
            if loop_idx is not None:
                if 'T_ramp' in recipe:
                    self.cryo.set_ramp_rate(chan,recipe['T_ramp'])
                if 'T_set' in recipe:
                    # NOTE: this does a little dance, 
                    # to circumvent a problem with the CryoCon,
                    # where it sometimes ignores the ramp rate 
                    with self.cryo.state_lock:
                        T_current = float(self.cryo.state['T_read_{}'.format(chan)])
                    self.cryo.set_temperature(chan,T_current)
                    T_inter = T_current + (recipe['T_set']-T_current)*0.1
                    self.cryo.set_temperature(chan,T_inter)
                    time.sleep(1)
                    self.cryo.set_temperature(chan,recipe['T_set'])
        for itm_nm, val in recipe.items():
            if '_flowrate' in itm_nm:
                pump_nm = itm_nm[:itm_nm.find('_flowrate')]
                if self.verbose: self.message_callback('setting {} to {}/min'.format(pump_nm,val))
                self.ppumps[pump_nm].set_flowrate(val)
        rcp_str = self.prettyprint_recipe(recipe)
        if self.verbose: self.message_callback(rcp_str)
        self.add_to_history(rcp_str)

    @staticmethod
    def prettyprint_recipe(rcp):
        rcp_str = ''
        if 'T_set' in rcp:
            rcp_str += '\nT_set: {}'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += '\nT_ramp: {}/min'.format(rcp['T_ramp'])
        for itm_nm, val in rcp.items():
            if '_flowrate' in itm_nm:
                pump_nm = itm_nm[:itm_nm.find('_flowrate')]
                rcp_str += '\n{} flow rate: {}'.format(pump_nm,val) 
        return rcp_str

    def check_status(self):
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
            ok_flag = True
            with ppc.state_lock:
                setpt_pls = float(ppc.state['target_flow_rate'])
                frt_pls = float(ppc.state['flow_rate'])
            if frt_pls is not None:
                frt_ulm = frt_pls*60/1.E6
                truefrt_ulm = ppc.get_true_flowrate(frt_ulm)
                setpt_ulm = setpt_pls*60/1.E6
                truesetpt_ulm = ppc.get_true_flowrate(setpt_ulm)
                stat_dict['{}_flowrate'.format(nm)] = float(truefrt_ulm)
                stat_dict['{}_setpoint'.format(nm)] = float(truesetpt_ulm)
                stat_str += ' {}: {} (setpt {}), '.format(nm,truefrt_ulm,truesetpt_ulm)
                # TODO: these limits should be MitosPPumpController attributes
                if truesetpt_ulm > 1.:
                    # substantially high setpoint: make sure the true rate is within 50%
                    if abs(truefrt_ulm-truesetpt_ulm)/truesetpt_ulm > 0.2:
                        ok_flag = False
                else:
                    # low setpt: make sure the true rate is not too far off 
                    if abs(truefrt_ulm-truesetpt_ulm) > 0.5:
                        ok_flag = False
                if self.verbose and not ok_flag:
                    self.message_callback(
                    'ppump {} flowrate {} is far from setpoint {}'
                    .format(nm,truefrt_ulm,truesetpt_ulm))
        self.add_to_history(stat_str)
        with self.state_lock:
            self.state = copy.deepcopy(stat_dict)
        return ok_flag,stat_str,stat_dict

