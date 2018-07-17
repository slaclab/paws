from collections import OrderedDict
import os
import time

import numpy as np

from ...Operation import Operation

inputs=OrderedDict(
    flow_reactor=None)
outputs=OrderedDict(
    recipe={},
    header={})
 
class ReadFlowReactor(Operation):
    """Read and package the current state of a FlowReactor Plugin."""

    def __init__(self):
        super(ReadFlowReactor,self).__init__(inputs,outputs)
        self.input_doc['flow_reactor'] = 'FlowReactor plugin'
        self.output_doc['header'] = 'dict '
        self.output_doc['recipe'] = 'formatted FlowReactor recipe'

    def run(self):
        fr = self.inputs['flow_reactor'] 
        flag,statstr,hdr = fr.check_status()
        rcp = {}
        rcp['T_set'] = float(hdr['T_set_A'])
        flowrate_keys = [k for k in hdr.keys() if 'flowrate' in k]
        fr_tot = np.sum([hdr[k] for k in flowrate_keys])
        rcp['flowrate'] = float(fr_tot)
        rcp['solvent'] = fr.inputs['solvent_pump_name'] 
        rcp['reagent_volume_fractions'] = {}
        for k in flowrate_keys:
            if not fr.inputs['solvent_pump_name'] in k:
                rg_name = k[:k.find('_flowrate')]
                fr_rg = float(hdr[k])
                rcp['reagent_volume_fractions'][rg_name] = float(fr_rg/fr_tot)

        self.outputs['recipe'] = rcp
        self.outputs['header'] = hdr 


