import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools

class BuildListFromBatch(Operation):
    """
    Given a batch output and a batch output uri, 
    harvest a list of outputs from the batch.
    """

    def __init__(self):
        input_names = ['batch_output','output_key']
        output_names = ['data_list']
        super(BuildListFromBatch,self).__init__(input_names,output_names)        
        self.input_doc['batch_output'] = 'list of dicts produced by a batch execution'
        self.input_doc['output_key'] = 'dict key for batch_output data to be packed into list'
        self.input_type['batch_output'] = opmod.workflow_item
        self.output_doc['data_list'] = 'list of the data fetched from batch_output using data_uri'

    def run(self):
        b_out = self.inputs['batch_output']
        k = self.inputs['output_key']
        if b_out is None or k is None:
            return
        l = [d[k] for d in b_out]
        self.outputs['data_list'] = l 

