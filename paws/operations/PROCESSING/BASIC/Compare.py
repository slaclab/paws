import numpy as np
from collections import OrderedDict

from ...Operation import Operation

inputs=OrderedDict(
    data=None,
    comparison_value=None)

outputs=OrderedDict(
    is_greater=None,
    is_lesser=None,
    is_equal=None)

class Compare(Operation):
    """Compare input `data` against a `comparison_value`."""

    def __init__(self):
        super(Compare,self).__init__(inputs,outputs)        
        self.input_doc['data'] = 'Input data'
        self.input_doc['comparison_value'] = 'Value to compare against'
        self.output_doc['is_greater'] = 'True if `data` > `comparison_value`'
        self.output_doc['is_lesser'] = 'True if `data` < `comparison_value`'
        self.output_doc['is_equal'] = 'True if `data` == `comparison_value`'

    def run(self):
        self.outputs['is_greater'] = self.inputs['data'] > self.inputs['comparison_value']
        self.outputs['is_lesser'] = self.inputs['data'] < self.inputs['comparison_value']
        self.outputs['is_equal'] = self.inputs['data'] == self.inputs['comparison_value']

