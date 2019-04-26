import copy
import time
from threading import Thread, Condition

import numpy as np

from .PawsPlugin import PawsPlugin
from .MitosPPumpController import MitosPPumpController
from .CryoConController import CryoConController

class FlowReactor(PawsPlugin):

    def __init__(self,timer,ppumps_setup,cryocon_setup={},verbose=False,log_file=None):
        """Create a FlowReactor control plugin.

        Parameters
        ----------
        timer : paws.plugins.Timer.Timer
        ppumps_setup : dict
        cryocon_setup : dict
        verbose : bool
        log_file : str
        """
        super(FlowReactor,self).__init__(verbose=verbose,log_file=log_file)
        self.timer = timer
        self.ppumps_setup = ppumps_setup 
        self.ppumps = dict.fromkeys(self.ppumps_setup.keys())
        self.cryocon_setup = cryocon_setup 
        self.cryo = None
        self.cryo_lock = Condition()
        self.pumps_lock = Condition()
        self.state_lock = Condition()
        self.state = {}
        self.recipe = {}
        self.controller_thread = None

    def start(self):
        # set up internal PPumpController plugins
        with self.pumps_lock:
            for pump_nm, pump_cfg in self.ppumps_setup.items():
                self.ppumps[pump_nm] = MitosPPumpController(
                    timer=self.timer,
                    serial_device=pump_cfg['device'],
                    flowrate_sensitivity=pump_cfg['flowrate_sensitivity'],
                    bad_flow_tol=pump_cfg['bad_flow_tol'],
                    volume_limit=pump_cfg['volume_limit'],
                    flowrate_table=pump_cfg['flowrate_table'],
                    verbose=False,log_file=None
                    )
            for nm,ppc in self.ppumps.items():
                if self.verbose: self.message_callback('starting pump controller: {}'.format(nm))
                ppc.start()
                ppc.set_flowrate(0.)
        # set up internal CryoConController plugin
        with self.cryo_lock:
            if self.cryocon_setup:
                self.cryo = self.build_cryo()
                if self.verbose: self.message_callback('starting cryocon controller')
                self.cryo.start()
                self.initialize_cryo()
                if self.verbose: self.message_callback('startup complete: running flow reactor')
        super(FlowReactor,self).start()

    def build_cryo(self):
        return CryoConController(
                timer=self.timer,
                host=self.cryocon_setup['host'],
                port=self.cryocon_setup['port'],
                channels=self.cryocon_setup['channels'],
                verbose=False,log_file=None
                )

    def initialize_cryo(self):
        with self.cryo_lock:
            for chan in self.cryo.channels.keys():
                self.cryo.set_units(chan,'C')
                self.cryo.loop_setup(chan,'RAMPP')
                self.cryo.set_temperature(chan,25.)

    def _run(self):
        self.controller_thread = Thread(target=self.run_reactor)
        # start control and block until control is established 
        with self.running_lock:
            self.controller_thread.start()
            self.running_lock.wait()

    def run_reactor(self):
        keep_going = True
        stop_flag = False
        # main thread should be waiting for run_notify()...
        self.run_notify()
        # start temperature control loop now
        with self.cryo_lock:
            self.cryo.start_control()
        while keep_going: 
            with self.timer.dt_lock:
                self.timer.dt_lock.wait()
            # check status, stop reactor if faults present 
            ok_flag,statdict = self.check_status()
            if not ok_flag:
                if self.verbose:
                    self.message_callback('detected a fault- status: \n{}'.format(statdict))
                self.stop()
            with self.timer.running_lock:
                if not self.timer.running:
                    self.stop()
            with self.running_lock:
                keep_going = bool(self.running)
        if self.verbose: self.message_callback('Stopping FlowReactor')
        # try to stop cryocon
        with self.cryo_lock:
            if self.cryo:
                try:
                    self.cryo.stop_control() 
                except:
                    pass
        # try to stop pumps
        with self.pumps_lock:
            for nm,ppc in self.ppumps.items():
                try:
                    ppc.set_idle()
                except:
                    pass    
        self.add_to_history('STOP')
        self.dump_history()

    def get_state(self):
        with self.state_lock:
            st = copy.deepcopy(self.state)
        return st

    def vent_pumps(self):
        with self.pumps_lock:
            for nm,ppc in self.ppumps.items():
                if self.verbose: self.message_callback('Setting pump {} to idle'.format(nm))
                ppc.set_idle()

    def stop_pumps(self):
        with self.pumps_lock:
            for nm,ppc in self.ppumps.items():
                if self.verbose: self.message_callback('Setting pump {} to zero flow'.format(nm))
                ppc.set_flowrate(0.)

    def set_temperature(self,T_set,T_ramp=None):
        with self.cryo_lock:
            for chan,loop_idx in self.cryo.channels.items():
                if T_ramp: self.cryo.set_ramp_rate(chan,T_ramp)
                self.cryo.set_temperature(chan,T_set)

    def set_recipe(self,recipe):
        with self.cryo_lock:
            self._set_cryocon(recipe)
        with self.pumps_lock:
            for itm_nm, val in recipe.items():
                if '_flowrate' in itm_nm:
                    pump_nm = itm_nm[:itm_nm.find('_flowrate')]
                    if self.verbose: self.message_callback('setting {} to {}/min'.format(pump_nm,val))
                    self.ppumps[pump_nm].set_flowrate(val)
        rcp_str = self.prettyprint_recipe(recipe)
        if self.verbose: self.message_callback(rcp_str)
        self.add_to_history(rcp_str)
        self.recipe = recipe

    def _set_cryocon(self,recipe):
        keep_trying = True
        n_tries = 0
        while keep_trying:
            try:
                for chan,loop_idx in self.cryo.channels.items():
                    if loop_idx is not None:
                        if 'T_ramp' in recipe:
                            self.cryo.set_ramp_rate(chan,recipe['T_ramp'])
                        if 'T_set' in recipe:
                            self.cryo.hack_set_temp(chan,recipe['T_set'])
                keep_trying = False
            except Exception as ex:
                # if repeated failures, raise the exception
                if n_tries > 4:
                    raise
                else:
                    # try resetting the cryocon a few times
                    if self.verbose: 
                        msg = 'cryocon error --> attempting cryocon controller restart'
                        msg += '\nerror message: {}'.format(ex)
                        self.message_callback(msg)
                    self.cryo = self.build_cryo()
                    self.cryo.start()
                    self.initialize_cryo()
                    self.cryo.start_control()
                    n_tries += 1

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
        ok_flag = True
        stat_str = ''
        stat_dict = {}
        with self.cryo_lock:
            if self.cryo:
                with self.cryo.state_lock:
                    for chan,idx in self.cryo.channels.items():
                        T_read_key = 'T_read_{}'.format(chan)
                        T_read = float(self.cryo.state[T_read_key])
                        stat_dict[T_read_key] = T_read
                        stat_str += 'T_{}: {:.3f}, '.format(chan,T_read)
        flowrate_alert_msg = ''
        with self.pumps_lock:
            for nm,ppc in self.ppumps.items():
                pstate = ppc.get_state()
                stat_str += '{}: {:.2f} (setpt {:.2f}), '.format(
                    nm,pstate['flow_rate'],pstate['target_flow_rate'])
                stat_dict['{}_flowrate'.format(nm)] = pstate['flow_rate']
                stat_dict['{}_setpoint'.format(nm)] = pstate['target_flow_rate']
                stat_dict['{}_volume_limit_ok'.format(nm)] = pstate['volume_limit_ok']
                stat_dict['{}_flowrate_ok'.format(nm)] = pstate['flow_rate_ok']
                stat_dict['{}_bad_flow_detected'.format(nm)] = pstate['bad_flow_detected']
                if not pstate['flow_rate_ok']:
                    flowrate_alert_msg += '{} flowrate alert: {}/{}\n'.format(
                        nm,pstate['flow_rate'],pstate['target_flow_rate'])
                    if self.recipe:
                        frt_val = self.recipe[nm+'_flowrate']
                        if self.verbose: self.message_callback('re-trying to set {} to {}/min'.format(nm,frt_val))
                        self.ppumps[nm].set_flowrate(frt_val)
                if pstate['bad_flow_detected']:
                    if self.verbose: self.message_callback(
                        '{} flowrate fault- requesting stop'.format(nm))
                    ok_flag = False
                if not pstate['volume_limit_ok']:
                    if self.verbose: self.message_callback(
                        '{} volume limit reached- requesting stop'.format(nm))
                    ok_flag = False
        if flowrate_alert_msg and self.verbose: self.message_callback(flowrate_alert_msg.strip())
        self.add_to_history(stat_str)
        with self.state_lock:
            self.state = copy.deepcopy(stat_dict)
        return ok_flag,stat_dict

