import numpy as np

from ... import Operation as op
from ...Operation import Operation
from ... import optools

class BuildListFromBatch(Operation):
    """
    Given a batch output and a batch output uri, 
    harvest a list of outputs from the batch.
    """

    def __init__(self):
        input_names = ['batch_output','data_uri']
        output_names = ['data_list']
        super(BuildListFromBatch,self).__init__(input_names,output_names)        
        self.input_doc['batch_output'] = 'list of dicts produced by a batch execution'
        self.input_doc['data_uri'] = 'uri for data to be packed into list- must be an item saved in batch_output'
        self.input_src['batch_output'] = op.wf_input
        self.input_src['data_uri'] = op.wf_input
        self.input_type['batch_output'] = op.ref_type
        self.input_type['data_uri'] = op.path_type
        self.output_doc['data_list'] = 'list of the data fetched from batch_output using data_uri'

    def run(self):
        b_out = self.inputs['batch_output']
        uri = self.inputs['data_uri']
        data = [optools.get_uri_from_dict(uri,d) for d in b_out]
        self.outputs['data_list'] = data 

