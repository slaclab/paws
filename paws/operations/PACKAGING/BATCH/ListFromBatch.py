from collections import OrderedDict

import numpy as np

from ...Operation import Operation
from ... import optools

inputs=OrderedDict(
    batch_outputs=None,
    output_key=None,
    lower_index=None,
    upper_index=None)
outputs=OrderedDict(data_list=None)

class ListFromBatch(Operation):
    """
    Given a batch output (list of dicts)
    and an output name (dict key), 
    harvest a list of outputs from the batch.
    """

    def __init__(self):
        super(ListFromBatch,self).__init__(inputs,outputs)        
        self.input_doc['batch_outputs'] = 'list of dicts produced by a batch execution'
        self.input_doc['output_key'] = 'name of workflow output to be harvested'
        self.input_doc['lower_index'] = 'optional list slice lower limit, inclusive'
        self.input_doc['upper_index'] = 'optional list slice upper limit, exclusive'
        self.output_doc['data_list'] = 'list of the data fetched from batch_output'

    def run(self):
        b_out = self.inputs['batch_outputs']
        k = self.inputs['output_key']
        lidx = self.inputs['lower_index']
        uidx = self.inputs['upper_index']
        dl = [d[k] for d in b_out]

        if lidx is not None:
            dl = dl[lidx:]
            uidx = uidx-lidx
        if uidx is not None:
            dl = dl[:uidx]

        self.outputs['data_list'] = dl

