from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from .. import optools

inputs=OrderedDict(
    work_item=None,
    inputs=None,
    input_keys=None)

outputs=OrderedDict(outputs=None)

class Run(Operation):
    """Execute a Workflow or Operation"""

    def __init__(self):
        super(Run,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'the Operation '\
            'or Workflow object to be executed'
        self.input_doc['inputs'] = 'one object for each of '\
            'the `work_item` inputs indicated by `input_keys`.'
        self.input_doc['input_keys'] = 'list of keys for setting '\
            'inputs of the `work_item`.'
        self.output_doc['outputs'] = 'if `run_flag` is True, '\
            'this will hold the `work_item` outputs'
        self.input_datatype['input_keys'] = 'list'
        self.input_datatype['inputs'] = 'list'

    def run(self):
        wrk = self.inputs['work_item']
        inpks = self.inputs['input_keys']
        inpvals = self.inputs['inputs']

        if any(inpks): 
            for inpk,inpval in zip(inpks,inpvals):
                wrk.set_input(inpk,inpval)
        wrk.run()
        out_dict = wrk.get_outputs()

        self.outputs['outputs'] = out_dict

