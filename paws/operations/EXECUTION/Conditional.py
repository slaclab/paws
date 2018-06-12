from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from .. import optools

inputs=OrderedDict(
    work_item=None,
    inputs={},
    condition=None,
    run_condition=None)

outputs=OrderedDict(
    outputs=None)
        
# TODO: unify Operation and Workflow APIs to eliminate instance checks

class Conditional(Operation):
    """Conditionally execute a Workflow or Operation"""

    def __init__(self):
        super(Conditional,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'Operation or Workflow to be executed'
        self.input_doc['inputs'] = 'dict to load into `work_item` inputs before running'
        self.input_doc['condition'] = 'condition that determines whether or not to run `work_item`'
        self.input_doc['run_condition'] = '`work_item` is executed if `condition` == `run_condition`'
        self.output_doc['outputs'] = 'if `run_flag` is True, the `work_item` outputs are saved here'
        self.input_datatype['input_keys'] = 'list'
        self.input_datatype['inputs'] = 'list'

    def run(self):
        wrk = self.inputs['work_item']
        cond = self.inputs['condition']
        rcond = self.inputs['run_condition']
        inpd = self.inputs['inputs']

        out_dict = wrk.get_outputs()

        if cond == rcond: 
            self.message_callback('condition met: running')
            if any(inpd): 
                for inpk,inpval in inpd.items():
                    wrk.set_input(inpk,inpval)
            wrk.run()
            out_dict = wrk.get_outputs()
        else:
            self.message_callback('condition not met: skipping execution')

        self.outputs['outputs'] = out_dict

