import copy
from collections import OrderedDict

from . import ReadBatch
from ..Workflow import Workflow 
from ...operations.SORTING.SortBatch import SortBatch

inputs = copy.deepcopy(ReadBatch.inputs)
inputs.update(
    lower_index = None,
    upper_index = None,
    index_step = 1
    )

outputs = copy.deepcopy(ReadBatch.outputs)

class ReadTimeSeries(Workflow):

    def __init__(self):
        super(ReadTimeSeries,self).__init__(inputs,outputs)
        self.batch_reader = ReadBatch.ReadBatch()
        self.sorter = SortBatch()

    def run(self):
        read_inputs = OrderedDict([(k,self.inputs[k]) for k in ReadBatch.inputs.keys()])
        batch_outputs = self.batch_reader.run_with(**read_inputs) 
        self.sorter.run_with(
            batch_outputs=batch_outputs,
            x_values=batch_outputs['time'],
            x_sort_flag=True,
            x_shift_flag=True,
            lower_index=self.inputs['lower_index'],
            upper_index=self.inputs['upper_index'],
            index_step=self.inputs['index_step']
            )
        self.outputs.update(self.sorter.outputs['sorted_outputs'])
        return self.outputs

