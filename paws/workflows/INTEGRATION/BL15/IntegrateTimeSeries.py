import os
import copy
from collections import OrderedDict

import numpy as np

from ...Workflow import Workflow 
from ...IO.BL15 import ReadTimeSeries 
from .. import IntegrateBatch

inputs = copy.deepcopy(ReadTimeSeries.inputs)
inputs.update(
    integrator = None,
    q_min = 0.,
    q_max = float('inf'),
    output_dir = None
    )

outputs = copy.deepcopy(IntegrateBatch.outputs)

class IntegrateTimeSeries(Workflow):
    
    def __init__(self):
        super(IntegrateTimeSeries,self).__init__(inputs,outputs)
        self.add_operations(
            read = ReadTimeSeries.ReadTimeSeries(),
            integrate = IntegrateBatch.IntegrateBatch()
            )

    def run(self):
        self.operations['read'].operations['read_batch'].operations['read'].disable_ops('read_q_I','read_system')
        read_inputs = OrderedDict([(k,self.inputs[k]) for k in ReadTimeSeries.inputs.keys()])
        read_outputs = self.operations['read'].run_with(**read_inputs)

        self.outputs = self.operations['integrate'].run_with(
            image_data = read_outputs['image_data'],
            integrator = self.inputs['integrator'],
            q_min = self.inputs['q_min'],
            q_max = self.inputs['q_max'],
            output_dir = self.inputs['output_dir'],
            output_filenames = read_outputs['filenames']
            )

        return self.outputs

