from __future__ import print_function
from collections import OrderedDict
import os
import copy
import time

from .PawsPlugin import PawsPlugin

content = OrderedDict(
    timer=None,
    cryocon=None,
    ppumps={},
    volume_limits={},
    bad_flow_tolerance=1E9)

class FlowReactor(PawsPlugin):

    def __init__(self):
        super(FlowReactor,self).__init__(content)
        self.thread_blocking = True
        self.content_doc['timer'] = 'A Timer plugin for triggering plugin activities'
        self.content_doc['cryocon'] = 'CryoConController plugin for temperature control' 
        self.content_doc['ppumps'] = 'Dict of named MitosPPumpControllers' 
        self.content_doc['volume_limits'] = 'Dict of pump volume limits (in microlitres)' 
        #self.content_doc['solvent_pump_name'] = 'Name (string) of the pump controlling solvent flow' 
        self.content_doc['bad_flow_tolerance'] = 'Number of timer ticks '\
            'to tolerate bad flow readings before stopping the reactor' 
        self.thread_blocking = True
        self.verbose = False
        self.anomaly_count = 0
        self.solvent_name = None

    def description(self):
        desc = 'FlowReactor Plugin: '\
            'Coordinates a CryoConController '\
            'and a set of MitosPPumpControllers '\
            'to set recipes for a flow reactor.'
        return desc

    def start(self):
        super(FlowReactor,self).start()

    def run(self):
        tmr = self.content['timer'] 
        ppcs = self.content['ppumps']
        cryo = self.content['cryocon']
        bftol = self.content['bad_flow_tolerance']
        vlimits = self.content['volume_limits']
        vdelivered = dict.fromkeys(vlimits.keys())
        for k in vdelivered.keys(): vdelivered[k] = 0.
        with tmr.dt_lock:
            t_now = tmr.dt_utc()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'START')
        keep_going = True
        stop_flag = False
        timer_dt_minutes = float(tmr.content['dt'])/60.
        #for nm,ppc in ppcs.items():
        #    ppc.set_flowrate(0.)
        if cryo:
            for chan in cryo.content['channels'].keys():
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
            if ok_flag:
                self.anomaly_count = 0
            else:
                self.anomaly_count += 1
                if self.anomaly_count >= bftol:
                    if self.verbose: self.message_callback('Anomalous flow detected: stopping FlowReactor')
                    stop_flag = True
                
            if vlimits:
                for pump_nm, lmt in vlimits.items():
                    # get the true ul/m flowrate from statdict
                    fr = statdict['{}_flowrate'.format(pump_nm)]
                    # add flowrate * dt in minutes vdelivered[pump_nm]
                    vdelivered[pump_nm] += fr*timer_dt_minutes
                    # check if vdelivered[pump_nm] >= lmt: if so, throw the stop.
                    #if self.verbose: self.message_callback(
                    #    '{} volume delivered: {} / {}'.format(
                    #    pump_nm,vdelivered[pump_nm],lmt))
                    if vdelivered[pump_nm] >= lmt:
                        stop_flag = True
                        if self.verbose: self.message_callback('Volume limit reached: stopping FlowReactor')

            if stop_flag:
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
        if self.verbose: self.message_callback('Stopping FlowReactor at {}'.format(t_now))
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'STOP')
            self.proxy.dump_history()
        # set pumps to idle, stop cryocon loop
        for nm,ppc in ppcs.items():
            if self.verbose: self.message_callback('Setting pump {} to idle'.format(nm))
            ppc.set_idle()
        if cryo:
            if self.verbose: self.message_callback('Stopping CryoCon control loop')
            cryo.stop_control() 

    def set_recipe(self,recipe):
        cryo = self.content['cryocon']
        tmr = self.content['timer']
        self.solvent_name = recipe['solvent']
        for chan,loop_idx in cryo.content['channels'].items():
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
        ppcs = self.content['ppumps']
        if 'flowrate' in recipe:
            tot_frt = recipe['flowrate']
            solv_frt = tot_frt 
        for itm_nm, val in recipe.items():
            if '_fraction' in itm_nm:
                rg_nm = itm_nm[:itm_nm.find('_fraction')]
                rg_frt = tot_frt * val
                solv_frt -= rg_frt
                if self.verbose: self.message_callback('setting {} to {}/min'.format(rg_nm,rg_frt))
                ppcs[rg_nm].set_flowrate(rg_frt)
        if self.verbose: self.message_callback('setting solvent ({}) to {}/min'.format(self.solvent_name,solv_frt))
        ppcs[self.solvent_name].set_flowrate(solv_frt)
        if self.verbose: self.message_callback(self.prettyprint_recipe(recipe))
        with tmr.dt_lock:
            t_now = float(tmr.dt_utc())
        with self.history_lock:
            self.add_to_history(t_now,self.print_recipe(recipe))

    @staticmethod
    def prettyprint_recipe(rcp):
        rcp_str = ''
        if 'T_set' in rcp:
            rcp_str += os.linesep+'T_set: {}'.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += os.linesep+'T_ramp: {}/min'.format(rcp['T_ramp'])
        if 'flowrate' in rcp:
            tot_frt = rcp['flowrate'] 
            rcp_str += os.linesep+'flowrate: {}/min'.format(tot_frt)
            solv_frt = tot_frt 
        for itm_nm, val in rcp.items():
            if '_fraction' in itm_nm:
                rg_nm = itm_nm[:itm_nm.find('_fraction')]
                rcp_str += os.linesep+'{} volume fraction: {}'.format(rg_nm,val) 
                rg_frt = tot_frt * val
                solv_frt -= rg_frt
        rcp_str += os.linesep+'{} (solvent) volume fraction: {}'.format(rcp['solvent'],solv_frt/tot_frt) 
        return rcp_str

    @staticmethod
    def print_recipe(rcp):
        rcp_str = ''
        if 'T_set' in rcp:
            rcp_str += 'T_set: {}, '.format(rcp['T_set'])
        if 'T_ramp' in rcp: 
            rcp_str += 'T_ramp: {}/min, '.format(rcp['T_ramp'])
        if 'flowrate' in rcp:
            tot_frt = rcp['flowrate'] 
            rcp_str += 'flowrate: {}/min, '.format(tot_frt)
            solv_frt = tot_frt 
        for itm_nm, val in rcp.items():
            if '_fraction' in itm_nm:
                rg_nm = itm_nm[:itm_nm.find('_fraction')]
                rcp_str += '{} volume fraction: {}'.format(rg_nm,val) 
                rg_frt = tot_frt * val
                solv_frt -= rg_frt
        rcp_str += '{} (solvent) volume fraction: {}'.format(rcp['solvent'],solv_frt/tot_frt) 
        return rcp_str

    def check_status(self):
        ok_flag = True
        stat_str = ''
        stat_dict = {}
        cryo = self.content['cryocon']
        if cryo:
            with cryo.state_lock:
                for chan,idx in cryo['channels'].items():
                    T_set_key = 'T_set_{}'.format(chan)
                    T_read_key = 'T_read_{}'.format(chan)
                    T_set = None
                    if T_set_key in cryo.state:
                        T_set = float(copy.copy(cryo.state[T_set_key]))
                    stat_dict[T_set_key] = T_set
                    T_read = copy.copy(cryo.state[T_read_key])
                    stat_dict[T_read_key] = float(T_read)
                    stat_str += 'T_{}: {} (setpt {}), '.format(chan,T_read,T_set)
        ppcs = self.content['ppumps']
        if any(ppcs):
            for nm, ppc in ppcs.items():
                with ppc.state_lock:
                    setpt_pls = copy.copy(ppc['state']['target_flow_rate'])
                    frt_pls = copy.copy(ppc['state']['flow_rate'])
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
                            if abs(frt_pls-setpt_pls)/setpt_pls > 0.5 and truesetpt_ulm > 2.:
                                ok_flag = False
                                self.message_callback('ppump {} flowrate {} is far from setpoint {}'
                                .format(nm,truefrt_ulm,truesetpt_ulm))
        tmr = self.content['timer']
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

