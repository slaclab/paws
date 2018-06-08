from __future__ import print_function
from collections import OrderedDict
import os
import copy

from .PawsPlugin import PawsPlugin

inputs = OrderedDict(
    timer=None,
    spec_infoclient=None,
    ppump_controllers=[],
    ppump_names=[],
    verbose=False)

class FlowReactor(PawsPlugin):

    def __init__(self):
        super(FlowReactor,self).__init__(inputs)
        self.input_doc['timer'] = 'A Timer plugin for triggering plugin activities'
        self.input_doc['spec_infoclient'] = 'SpecInfoClient plugin for temperature control' 
        self.input_doc['pump_controllers'] = 'List of MitosPPumpControllers' 
        self.input_doc['pump_names'] = 'Names for identifying the MitosPPumpControllers' 
        self.input_doc['verbose'] = 'If True, plugin uses its message_callback' 

    def description(self):
        desc = 'FlowReactor Plugin: '\
            'Coordinates a running SpecInfoClient '\
            'and a set of MitosPPumpControllers '\
            'to set recipes for a flow reactor.'
        return desc

    def start(self):
        self.run_clone() 

    def run(self):
        tmr = self.inputs['timer'] 
        ppc_names = self.inputs['ppump_names']
        ppcs = self.inputs['ppump_controllers']
        ppc_map = OrderedDict()
        for nm, ppc in zip(ppc_names,ppcs):
            ppc_map[nm] = ppc
        spinfcl = self.inputs['spec_infoclient'] 
        spinfcl.enable_cryocon()
        vb = self.inputs['verbose'] 
        with tmr.dt_lock:
            t_now = tmr.dt_utc()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'START','')
        keep_going = True
        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            #if vb: self.message_callback(self.print_flow_rates())
            while self.commands.qsize() > 0:
                with tmr.dt_lock:
                    t_now = float(tmr.dt_utc())
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                T_set = cmd['T_set']
                cmd_str = 'T_set: {}C'.format(T_set)
                T_ramp = None
                if 'T_ramp' in cmd: T_ramp = cmd['T_ramp']
                if T_ramp: cmd_str += ' (ramp: {} C/min)'.format(T_ramp)
                spinfcl.set_cryocon(T_set,T_ramp)
                cmd_str += ', flow setpoints:'
                nms = cmd['ppump_names']
                frts = cmd['flow_rates']
                for nm,frt in zip(nms,frts):
                    ppc = ppc_map[nm]
                    ppc.set_flowrate(frt)
                    cmd_str += ' {}:{}uL/min'.format(nm,frt)
                if vb: self.message_callback(cmd_str)
                with self.proxy.history_lock:
                    self.proxy.add_to_history(t_now,cmd_str,'')

            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        with tmr.dt_lock:
            t_now = tmr.dt_utc()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'STOP','')
            self.proxy.dump_history()

    def set_recipe(self,recipe):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put(recipe)

    def print_recipe(self,rcp):
        rcp_str = 'Recipe: '
        T_set = rcp['T_set']
        rcp_str += os.linesep+'T_set: {}C'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += ' (ramp: {}C/min)'.format(rcp['T_ramp'])
        nms = rcp['ppump_names']
        frts = rcp['flow_rates']
        for nm,frt in zip(nms,frts):
            rcp_str += os.linesep+' {:>20}:{:8.2f}uL/min'.format(nm,frt) 
        return rcp_str

    def print_flow_rates(self):
        stat_str = 'Current flow rates: '
        ppc_names = self.inputs['ppump_names']
        ppcs = self.inputs['ppump_controllers']
        for nm, ppc in zip(ppc_names,ppcs):
            with ppc.state_lock:
                frt_pls = copy.copy(ppc.state['flow_rate'])
            if frt_pls is not None:
                frt_ulm = frt_pls*60/1.E6
                stat_str += os.linesep+' {:>20}:{:8.2f}uL/min'.format(nm,frt_ulm)
        return stat_str
                    

