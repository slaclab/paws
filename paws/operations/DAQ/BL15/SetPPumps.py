from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(
    ppump_controllers={},
    targets={},
    set_points={})
outputs=OrderedDict(
    report=None)
        
class SetPPumps(Operation):
    """Set the flow or pressure for an array of P-pump controllers."""

    def __init__(self):
        super(SetPPumps,self).__init__(inputs,outputs)
        self.input_doc['ppump_controllers'] = 'dict of MitosPPumpController plugins'
        self.input_doc['targets'] = 'dict of control modes (strings) for each pump- '\
            'each entry should be either "flowrate" or "pressure", '\
            'defaults to "flowrate" if values are not provided' 
        self.input_doc['set_points'] = 'dict of set points for each pump' 
        #self.input_doc['delay_time'] = 'seconds to wait after setting `set_points`' 
        self.output_doc['report'] = 'dict reporting details of final state' 

    def run(self):
        ppcs = self.inputs['ppump_controllers'] 
        tgts = self.inputs['targets']
        setpts = self.inputs['set_points']
        #delay = self.inputs['delay_time']
        #stat = self.inputs['flag']
        #vals = [None for ppc in ppcs] 
        #if bool(stat):
        if tgts is None:
            tgts = ['flowrate' for ppc in ppcs]
        self.message_callback('setting pumps to: {}'.format(setpts))
        for ppnm,ppc in ppcs.items():
            tgt = tgts[ppnm]
            setpt = setpts[ppnm]
            if tgt == 'pressure':
                ppc.set_pressure(setpt)
            #if tgt == 'flowrate':
            else: 
                ppc.set_flowrate(setpt)
        #self.message_callback('SetPPumps waiting {} seconds...'.format(delay))
        #time.sleep(delay)
            #done = False
            #while not done:
            #    done = True
            #    for ipp,ppc in enumerate(ppcs):
            #        tgt = tgts[ipp]
            #        setpt = setpts[ipp]
            #        prec = precs[ipp]
            #        vals[ipp] = ppc.get_current_value(tgt)
            #        if not abs(vals[ipp]-setpt)/setpt < prec:
            #            done = False
            #    # TODO:
            #    # delay, then check again
            #    # implement a maximum wait time
            #rpt = dict(targets=tgts,final_values=vals)
        #    rpt = {} 
        #    self.outputs['report'] = rpt
        #    self.outputs['flag'] = True
        #else:
        #    self.outputs['report'] = {'STATUS':bool(stat)}
        #    self.outputs['flag'] = False 

