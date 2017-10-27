import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools

class BuildListFromBatch(Operation):
    """
    Given a batch output (list of dicts)
    and an output name (dict key), 
    harvest a list of outputs from the batch.
    """

    def __init__(self):
        input_names = ['batch_outputs','output_key']
        output_names = ['data_list']
        super(BuildListFromBatch,self).__init__(input_names,output_names)        
        self.input_doc['batch_outputs'] = 'list of dicts produced by a batch execution'
        self.input_doc['output_key'] = 'name of workflow output to be harvested'
        self.input_type['batch_outputs'] = opmod.workflow_item
        self.output_doc['data_list'] = 'list of the data fetched from batch_output'

    def run(self):
        b_out = self.inputs['batch_outputs']
        k = self.inputs['output_key']
        self.outputs['data_list'] = [d[k] for d in b_out]

