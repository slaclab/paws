from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(
    ppump_controllers=None,
    targets=None,
    set_points=None,
    precisions=None,
    status_code=True)
outputs=OrderedDict(
    report=None,
    status_code=None)
        
class SetPPumps(Operation):
    """Set the flow or pressure for an array of P-pump controllers."""

    def __init__(self):
        super(SetPPumps,self).__init__(inputs,outputs)
        self.input_doc['ppump_controllers'] = 'array of MitosPPumpController plugins'
        self.input_doc['targets'] = 'array of control modes (strings) for each pump- '\
            'each entry should be either "flowrate" or "pressure"' 
        self.input_doc['set_points'] = 'array of set points for each pump' 
        self.input_doc['precisions'] = 'fractional precision for each target- '\
            'if not provided, a default of 0.01 is used' 
        self.input_doc['status_code'] = 'boolean flag for whether or not to proceed' 
        self.output_doc['report'] = 'dict reporting details of final state' 
        self.output_doc['status_code'] = 'boolean, positive iff the targets were achieved' 

    def run(self):
        ppcs = self.inputs['ppump_controllers'] 
        tgts = self.inputs['targets']
        setpts = self.inputs['set_points']
        precs = self.inputs['precisions']
        stat = self.inputs['status_code']
        if bool(stat):
            for ipp,ppc in enumerate(ppcs):
                tgt = tgts[ipp]
                setpt = setpts[ipp]
                prec = precs[ipp]
                ppc.set_target(tgt,setpt,prec)
            done = False
            while not done:
                done = True
                for ipp,ppc in enumerate(ppcs):
                    tgt = tgts[ipp]
                    setpt = setpts[ipp]
                    prec = precs[ipp]
                    val = ppc.get_current_value(tgt)
                    if not abs(val-setpt)/setpt < prec:
                        done = False
                # TODO:
                # delay, then check again
                # implement a maximum wait time
        else:
            self.outputs['report'] = {'STATUS':bool(stat)}
            self.outputs['status_code'] = False 


 


