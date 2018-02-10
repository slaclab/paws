from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from ...workflows.Workflow import Workflow
from .. import optools

inputs=OrderedDict(
    work_item=None,
    inputs=None,
    input_keys=None,
    condition=None,
    run_condition=None)

outputs=OrderedDict(
    outputs=None)
        
# TODO: unify Operation and Workflow APIs to eliminate instance checks

class Conditional(Operation):
    """Conditionally execute a Workflow or Operation"""

    def __init__(self):
        super(Conditional,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'the Operation '\
            'or Workflow object to be executed'
        self.input_doc['inputs'] = 'one object for each of '\
            'the `work_item` inputs indicated by `input_keys`.'
        self.input_doc['input_keys'] = 'list of keys for setting '\
            'inputs of the `work_item`.'
        self.input_doc['condition'] = 'condition that determines '\
            'whether or not to run `work_item`.'
        self.input_doc['run_condition'] = '`work_item` is executed '\
            'if `condition` == `run_condition`.'
        self.output_doc['outputs'] = 'if `run_flag` is True, '\
            'this will hold the `work_item` outputs'
        self.input_datatype['input_keys'] = 'list'
        self.input_datatype['inputs'] = 'list'

    def run(self):
        wrk = self.inputs['work_item']
        cond = self.inputs['condition']
        rcond = self.inputs['run_condition']
        inpks = self.inputs['input_keys']
        inpvals = self.inputs['inputs']

        if isinstance(wrk,Workflow):
            wrkitm = wrk.clone_wf()
        else:
            wrkitm = wrk.clone_op()

        if isinstance(wrkitm,Workflow):
            out_dict = wrkitm.workflow_outputs()
        else:
            out_dict = wrkitm.outputs

        if cond == rcond: 
            if any(inpks): 
                for inpk,inpval in zip(inpks,inpvals):
                    if isinstance(wrki,Workflow):
                        wrki.set_wf_input(inpk,inpval)
                    else:
                        # assume it's an Operation
                        wrki.inputs[inpk] = inpval
            if isinstance(wrkitm,Workflow):
                wrkitm.execute()
                out_dict = wrkitm.workflow_outputs()
            else:
                wrkitm.run()
                out_dict = wrkitm.outputs

        self.outputs['outputs'] = out_dict

