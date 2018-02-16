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
    status_code=False)
        
class SetPPumps(Operation):
    """Set the flow or pressure for an array of P-pump controllers."""

    def __init__(self):
        super(SetPPumps,self).__init__(inputs,outputs)
        self.input_doc['ppump_controllers'] = 'list of MitosPPumpController plugins'
        self.input_doc['targets'] = 'list of control modes (strings) for each pump- '\
            'each entry should be either "flowrate" or "pressure"' 
        self.input_doc['set_points'] = 'list of set points for each pump' 
        self.input_doc['precisions'] = 'list of floats '\
            'specifying the fractional precision for each target'
        self.input_doc['status_code'] = 'boolean flag for whether or not to proceed' 
        self.output_doc['report'] = 'dict reporting details of final state' 
        self.output_doc['status_code'] = 'boolean, positive iff the targets were achieved' 

    def run(self):
        ppcs = self.inputs['ppump_controllers'] 
        tgts = self.inputs['targets']
        setpts = self.inputs['set_points']
        precs = self.inputs['precisions']
        stat = self.inputs['status_code']
        vals = [None for ppc in ppcs] 
        if bool(stat):
            for ipp,ppc in enumerate(ppcs):
                tgt = tgts[ipp]
                setpt = setpts[ipp]
                prec = precs[ipp]
                if tgt == 'flowrate':
                    ppc.set_flowrate(setpt,prec)
                elif tgt == 'pressure':
                    ppc.set_pressure(setpt,prec)
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
            rpt = {} 
            self.outputs['report'] = rpt
            self.outputs['status_code'] = True
        else:
            self.outputs['report'] = {'STATUS':bool(stat)}
            self.outputs['status_code'] = False 


 


