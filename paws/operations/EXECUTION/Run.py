from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from .. import optools

inputs=OrderedDict(
    work_item=None,
    inputs={})

outputs=OrderedDict(outputs=None)

class Run(Operation):
    """Execute a Workflow or Operation"""

    def __init__(self):
        super(Run,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'the Operation '\
            'or Workflow object to be executed'
        self.input_doc['inputs'] = 'dict of inputs to add to `work_item`'
        self.output_doc['outputs'] = '`work_item` outputs'
        self.input_datatype['inputs'] = dict 

    def run(self):
        wrk = self.inputs['work_item']
        inps = self.inputs['inputs']
        if any(inps): 
            for inpk,inpval in inps.items():
                wrk.set_input(inpk,inpval)
        wrk.run()
        out_dict = wrk.get_outputs()
        self.outputs['outputs'] = out_dict

