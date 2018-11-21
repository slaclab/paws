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
        self.output_doc['recipe'] = 'FlowReactor recipe data'
        self.output_doc['header'] = 'dict of data related to the recipe'

    def run(self):
        fr = self.inputs['flow_reactor'] 
        flag,statstr,hdr = fr.check_status()
        rcp = {}
        rcp['T_set'] = float(hdr['T_set_A'])
        #rcp['T_read'] = float(hdr['T_read_A'])
        setpt_keys = [k for k in hdr.keys() if 'setpoint' in k]
        fr_tot = np.sum([hdr[k] for k in setpt_keys])
        rcp['flowrate'] = float(fr_tot)
        rcp['solvent'] = fr.solvent_name
        for k in setpt_keys:
            if not k == fr.solvent_name+'_setpoint' in k:
                rg_name = k[:k.find('_setpoint')]
                fr_rg = float(hdr[k])
                rcp[rg_name+'_fraction'] = float(fr_rg/fr_tot)
        #self.message_callback('measured recipe: {}'.format(rcp))
        #self.message_callback('header data: {}'.format(hdr))
        self.outputs['recipe'] = rcp
        self.outputs['header'] = hdr 
        return self.outputs

