import os
import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 

from paws.workflows.IO.BL15 import ReadBatch
from paws.operations.PACKAGING.SortBatch import SortBatch

inputs = copy.deepcopy(ReadBatch.inputs)
inputs.update(
    lower_index = None,
    upper_index = None
    )

outputs = copy.deepcopy(ReadBatch.outputs)

class ReadTimeSeries(Workflow):

    def __init__(self):
        super(ReadTimeSeries,self).__init__(inputs,outputs)
        self.add_operation('read_batch',ReadBatch.ReadBatch())
        self.add_operation('sort',SortBatch())

    def run(self):
        b_outs = self.operations['read_batch'].run_with(**self.inputs) 
        self.operations['sort'].run_with(
            batch_outputs = b_outs,
            x_key='time',
            x_sort_flag=True,
            x_shift_flag=True)
        self.outputs.update(self.operations['sort'].outputs['sorted_outputs'])
        return self.outputs

