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
        self.input_doc['timer'] = 'A Timer plugin for triggering plugin activities'
        self.input_doc['cryocon'] = 'CryoConController plugin for temperature control' 
        self.input_doc['ppumps'] = 'Dict of named MitosPPumpControllers' 
        self.input_doc['verbose'] = 'If True, plugin uses its message_callback' 
        self.thread_blocking = True

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
        if cryo:
            cryo.set_units('A','C')
            cryo.loop_setup(1,'A','PID')
            cryo.set_temperature(1,25)
            cryo.start_control(1)
        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            while self.commands.qsize() > 0:
                with tmr.dt_lock:
                    t_now = float(tmr.dt_utc())
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                T_set = cmd['T_set']
                #cmd_str = 'T_set: {}C'.format(T_set)
                cryo.set_temperature(1,T_set)
                #T_ramp = None
                #if 'T_ramp' in cmd: T_ramp = cmd['T_ramp']
                #if T_ramp: cmd_str += ' (ramp: {} C/min)'.format(T_ramp)
                #cmd_str += ', flow setpoints:'
                frts = cmd['flow_rates']
                for nm,frt in frts.items():
                    ppc_map[nm].set_flowrate(frt)
                #    cmd_str += ' {}:{}uL/min'.format(nm,frt)
                if vb: self.message_callback(self.prettyprint_recipe(cmd))
                with self.proxy.history_lock:
                    self.proxy.add_to_history(t_now,self.print_recipe(cmd))
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
        if vb: self.message_callback('FlowReactor FINISHED')

    def set_recipe(self,recipe):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put(recipe)

    def prettyprint_recipe(self,rcp):
        rcp_str = 'Recipe: '
        T_set = rcp['T_set']
        rcp_str += os.linesep+'      T_set: {:7.3f}C'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += ' (ramp: {}C/min)'.format(rcp['T_ramp'])
        frts = rcp['flow_rates']
        for nm,frt in frts.items():
            rcp_str += os.linesep+' {:>10}:{:8.2f}uL/min'.format(nm,frt) 
        return rcp_str

    def print_recipe(self,rcp):
        rcp_str = 'Recipe: '
        T_set = rcp['T_set']
        rcp_str += 'T_set: {}C'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += ' (ramp: {}C/min)'.format(rcp['T_ramp'])
        frts = rcp['flow_rates']
        for nm,frt in frts.items():
            rcp_str += ', {}:{:8.2f}uL/min'.format(nm,frt) 
        return rcp_str

    def print_status(self):
        stat_str = 'Status: '
        #T_read = self.
        #stat_str += 'T: {}C'.format(T_read)
        ppcs = self.inputs['ppumps']
        for nm, ppc in ppcs.items():
            with ppc.state_lock:
                frt_pls = copy.copy(ppc.state['flow_rate'])
            if frt_pls is not None:
                frt_ulm = frt_pls*60/1.E6
                stat_str += ' {}:{:8.2f}uL/min'.format(nm,frt_ulm)
        return stat_str
                    

