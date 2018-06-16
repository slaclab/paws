from __future__ import print_function
from collections import OrderedDict
import os
import copy

from .PawsPlugin import PawsPlugin

inputs = OrderedDict(
    timer=None,
    cryocon=None,
    ppumps={},
    verbose=False)

class FlowReactor(PawsPlugin):

    def __init__(self):
        super(FlowReactor,self).__init__(inputs)
        self.thread_blocking = True
        self.input_doc['timer'] = 'A Timer plugin for triggering plugin activities'
        self.input_doc['cryocon'] = 'CryoConController plugin for temperature control' 
        self.input_doc['ppumps'] = 'Dict of named MitosPPumpControllers' 
        self.input_doc['verbose'] = 'If True, plugin uses its message_callback' 
        self.anomaly_count = 0

    def description(self):
        desc = 'FlowReactor Plugin: '\
            'Coordinates a CryoConController '\
            'and a set of MitosPPumpControllers '\
            'to set recipes for a flow reactor.'
        return desc

    def start(self):
        self.run_clone() 

    def run(self):
        tmr = self.inputs['timer'] 
        ppc_map = self.inputs['ppumps']
        cryo = self.inputs['cryocon'] 
        vb = self.inputs['verbose'] 
        with tmr.dt_lock:
            t_now = tmr.dt_utc()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'START')
        keep_going = True
        for nm,ppc in ppc_map.items():
            ppc.set_flowrate(0.)
        if cryo:
            cryo.set_units('C')
            cryo.loop_setup('RAMPP')
            with cryo.state_lock:
                T_now = cryo.state['T_read']
            cryo.set_temperature(T_now)
            cryo.set_ramp_rate(20)
            cryo.start_control()
        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            while self.commands.qsize() > 0:
                with tmr.dt_lock:
                    t_now = float(tmr.dt_utc())
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                if 'T_set' in cmd:
                    cryo.set_temperature(cmd['T_set'])
                if 'T_ramp' in cmd: 
                    cryo.set_ramp_rate(cmd['T_ramp'])
                if 'flow_rates' in cmd:
                    frts = cmd['flow_rates']
                    for nm,frt in frts.items():
                        ppc_map[nm].set_flowrate(frt)
                if vb: self.message_callback(self.prettyprint_recipe(cmd))
                with self.proxy.history_lock:
                    self.proxy.add_to_history(t_now,self.print_recipe(cmd))
            # log the flow rates and temperature,
            # check for anomalies in flow rates,
            # stop the reactor if anomalies found
            with self.proxy.history_lock:
                ok_flag,stat = self.check_status()
                self.proxy.add_to_history(t_now,stat)
            if ok_flag:
                self.anomaly_count = 0
            else:
                self.anomaly_count += 1
            if self.anomaly_count >= 10:
                if vb: self.message_callback('Anomalous flow detected: stopping FlowReactor')
                with self.proxy.running_lock:
                    self.proxy.stop()
             
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        with tmr.dt_lock:
            t_now = tmr.dt_utc()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'STOP')
            self.proxy.dump_history()
        # set pumps to idle, stop cryocon loop
        for nm,ppc in ppc_map.items():
            ppc.set_idle()
        if cryo:
            cryo.stop_control() 
        if vb: self.message_callback('FlowReactor FINISHED')

    def set_recipe(self,recipe):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put(recipe)

    def prettyprint_recipe(self,rcp):
        rcp_str = 'Recipe: '
        if 'T_set' in rcp:
            T_set = rcp['T_set']
            rcp_str += os.linesep+'      T_set: {:7.3f}C'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += ' (ramp: {}C/min)'.format(rcp['T_ramp'])
        if 'flow_rates' in rcp:
            frts = rcp['flow_rates']
            for nm,frt in frts.items():
                rcp_str += os.linesep+' {:>10}:{:8.2f}uL/min'.format(nm,frt) 
        return rcp_str

    def print_recipe(self,rcp):
        rcp_str = 'Recipe: '
        if 'T_set' in rcp:
            T_set = rcp['T_set']
            rcp_str += 'T_set: {}C'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += ' (ramp: {}C/min)'.format(rcp['T_ramp'])
        if 'flow_rates' in rcp:
            frts = rcp['flow_rates']
            for nm,frt in frts.items():
                rcp_str += ', {}: {:8.2f}uL/min'.format(nm,frt) 
        return rcp_str

    def check_status(self):
        ok_flag = True
        stat_str = 'Status: '
        if self.inputs['cryocon']:
            with self.inputs['cryocon'].state_lock:
                T_read = copy.copy(self.inputs['cryocon'].state['T_read'])
            stat_str += 'T: {}C'.format(T_read)
        for nm, ppc in self.inputs['ppumps'].items():
            with ppc.state_lock:
                setpt_pls = copy.copy(ppc.state['target_flow_rate'])
                frt_pls = copy.copy(ppc.state['flow_rate'])
            if frt_pls is not None:
                frt_ulm = frt_pls*60/1.E6
                stat_str += ' {}:{:8.2f}uL/min'.format(nm,frt_ulm)
            if frt_pls is not None and setpt_pls is not None:
                if setpt_pls > 0:
                    if abs(frt_pls-setpt_pls)/setpt_pls > 0.5:
                        ok_flag = False
        return ok_flag,stat_str
                    

