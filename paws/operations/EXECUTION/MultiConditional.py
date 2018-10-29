from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from .. import optools

inputs=OrderedDict(
    work_item=None,
    inputs={},
    conditions=[],
    run_conditions=[],
    decision_mode='all')

outputs=OrderedDict(
    outputs=None)

# TODO: unify Operation and Workflow APIs to eliminate instance checks

class MultiConditional(Operation):
    """Conditionally execute a Workflow or Operation"""

    def __init__(self):
        super(MultiConditional,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'Operation or Workflow to be executed'
        self.input_doc['inputs'] = 'dict to load into `work_item` inputs before running'
        self.input_doc['conditions'] = 'list of conditions that determine whether or not to run `work_item`'
        self.input_doc['run_conditions'] = 'The `conditions` are compared against the `run_conditions` '\
            'to determine whether or not to run the `work_item`'
        self.input_doc['decision_mode'] = 'Either "any" or "all". '\
            'If "all", all `conditions` must match the corresponding `run_conditions`. '\
            'If "any", at least one `condition` must match the corresponding `run_condition`.'
        self.output_doc['outputs'] = 'if `run_flag` is True, the `work_item` outputs are saved here'
        self.input_datatype['inputs'] = 'dict'

    def run(self):
        wrk = self.inputs['work_item']
        conds = self.inputs['conditions']
        rconds = self.inputs['run_conditions']
        inpd = self.inputs['inputs']
        md = self.inputs['decision_mode']

        out_dict = wrk.get_outputs()

        runflag = False
        if md == 'all': runflag = all([cond == rcond for cond,rcond in zip(conds,rconds)]) 
        if md == 'any': runflag = any([cond == rcond for cond,rcond in zip(conds,rconds)]) 
        if runflag:
            self.message_callback('conditions met: running')
            if any(inpd): 
                for inpk,inpval in inpd.items():
                    wrk.set_input(inpk,inpval)
            wrk.run()
            out_dict = wrk.get_outputs()
        else:
            self.message_callback('one or more conditions not met: skipping execution')

        self.outputs['outputs'] = out_dict

