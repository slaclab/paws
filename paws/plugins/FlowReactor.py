from __future__ import print_function
from collections import OrderedDict
import os
import copy
import time

from .PawsPlugin import PawsPlugin

inputs = OrderedDict(
    timer=None,
    cryocon=None,
    ppumps={},
    solvent_pump_name=None)

class FlowReactor(PawsPlugin):

    def __init__(self):
        super(FlowReactor,self).__init__(inputs)
        self.thread_blocking = True
        self.input_doc['timer'] = 'A Timer plugin for triggering plugin activities'
        self.input_doc['cryocon'] = 'CryoConController plugin for temperature control' 
        self.input_doc['ppumps'] = 'Dict of named MitosPPumpControllers' 
        self.input_doc['solvent_pump_name'] = 'Name (string) of the pump controlling solvent flow' 
        self.thread_blocking = True
        self.verbose = False
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
        ppcs = self.inputs['ppumps']
        cryo = self.inputs['cryocon'] 
        with tmr.dt_lock:
            t_now = tmr.dt_utc()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'START')
        keep_going = True
        #for nm,ppc in ppcs.items():
        #    ppc.set_flowrate(0.)
        if cryo:
            for chan in cryo.inputs['channels'].keys():
                cryo.set_units(chan,'C')
                cryo.loop_setup(chan,'RAMPP')
            cryo.start_control()
        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            # log the flow rates and temperature,
            # check for anomalies in flow rates,
            # stop the reactor if anomalies found
            ok_flag,statstr,statdict = self.check_status()
            #if ok_flag:
            #    self.anomaly_count = 0
            #else:
            #    self.anomaly_count += 1
            #if self.anomaly_count >= 600:
            #    if self.verbose: self.message_callback('Anomalous flow detected: stopping FlowReactor')
            #    with self.proxy.running_lock:
            #        self.proxy.stop()
             
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
        for nm,ppc in ppcs.items():
            ppc.set_idle()
        if cryo:
            cryo.stop_control() 
        if self.verbose: self.message_callback('FlowReactor FINISHED')

    def set_recipe(self,recipe):
        cryo = self.inputs['cryocon']
        tmr = self.inputs['timer']
        for chan,loop_idx in cryo.inputs['channels'].items():
            if loop_idx is not None:
                if 'T_ramp' in recipe:
                    cryo.set_ramp_rate(chan,recipe['T_ramp'])
                if 'T_set' in recipe:
                    with cryo.state_lock:
                        T_current = cryo.state['T_read_{}'.format(chan)]
                    # NOTE: this is a little dance to circumvent a problem with the CryoCon,
                    # where it sometimes ignores the ramp rate 
                    cryo.set_temperature(chan,T_current)
                    T_inter = T_current + (recipe['T_set']-T_current)*0.1
                    cryo.set_temperature(chan,T_inter)
                    time.sleep(5)
                    cryo.set_temperature(chan,recipe['T_set'])
        ppcs = self.inputs['ppumps']
        solv_name = self.inputs['solvent_pump_name']   
        if 'flowrate' in recipe:
            tot_frt = recipe['flowrate']
            solv_frt = tot_frt 
            if 'reagent_volume_fractions' in recipe:
                for rg_name,rg_frac in recipe['reagent_volume_fractions'].items():
                    rg_frt = tot_frt * rg_frac
                    solv_frt = solv_frt - rg_frt
                    if self.verbose: self.message_callback('setting {} to {}/min'.format(rg_name,rg_frt))
                    ppcs[rg_name].set_flowrate(rg_frt)
            if self.verbose: self.message_callback('setting {} to {}/min'.format(solv_name,solv_frt))
            ppcs[solv_name].set_flowrate(solv_frt)
        if self.verbose: self.message_callback(self.prettyprint_recipe(recipe))
        with tmr.dt_lock:
            t_now = float(tmr.dt_utc())
        with self.history_lock:
            self.add_to_history(t_now,self.print_recipe(recipe))

    def prettyprint_recipe(self,rcp):
        rcp_str = ''
        if 'T_set' in rcp:
            rcp_str += os.linesep+'T_set: {}'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += os.linesep+'T_ramp: {}/min'.format(rcp['T_ramp'])
        if 'flowrate' in rcp:
            rcp_str += os.linesep+'flowrate: {}/min'.format(rcp['flowrate'])
        if 'reagent_volume_fractions' in rcp:
            for rg_name,rg_frac in rcp['reagent_volume_fractions'].items():
                rcp_str += os.linesep+'{} volume fraction: {}'.format(rg_name,rg_frac) 
        return rcp_str

    def print_recipe(self,rcp):
        rcp_str = ''
        if 'T_set' in rcp:
            rcp_str += 'T_set: {}, '.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += 'T_ramp: {}/min, '.format(rcp['T_ramp'])
        if 'flowrate' in rcp:
            rcp_str += 'flowrate: {}/min, '.format(rcp['flowrate'])
        if 'reagent_volume_fractions' in rcp:
            for rg_name,rg_frac in rcp['reagent_volume_fractions'].items():
                rcp_str += '{} volume fraction: {}, '.format(rg_name,rg_frac) 
        return rcp_str

    def check_status(self):
        ok_flag = True
        stat_str = ''
        stat_dict = {}
        cryo = self.inputs['cryocon']
        if cryo:
            with cryo.state_lock:
                for chan,idx in cryo.channels.items():
                    T_set_key = 'T_set_{}'.format(chan)
                    T_read_key = 'T_read_{}'.format(chan)
                    T_set = None
                    if T_set_key in cryo.state:
                        T_set = float(copy.copy(cryo.state[T_set_key]))
                    stat_dict[T_set_key] = T_set
                    T_read = copy.copy(cryo.state[T_read_key])
                    stat_dict[T_read_key] = float(T_read)
                    stat_str += 'T_{}: {} (setpt {}), '.format(chan,T_read,T_set)
        ppcs = self.inputs['ppumps']
        if any(ppcs):
            for nm, ppc in ppcs.items():
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
                    if setpt_pls is not None:
                        if setpt_pls > 0:
                            if abs(frt_pls-setpt_pls)/setpt_pls > 0.5:
                                ok_flag = False
                                self.message_callback('ppump {} flowrate {} is far from setpoint {}'
                                .format(nm,truefrt_ulm,truesetpt_ulm))
        tmr = self.inputs['timer']
        with tmr.dt_lock:
            t_sec = float(tmr.t_utc())
            t_now = float(tmr.dt_utc())
            t_str = str(tmr.time_as_string())
        stat_dict['t_utc'] = float(t_sec)
        stat_dict['time'] = t_str
        #if self.verbose: self.message_callback(stat_str)
        with self.history_lock:
            self.add_to_history(t_now,stat_str)
        return ok_flag,stat_str,stat_dict

