from collections import OrderedDict

import numpy as np

from ..Operation import Operation

inputs=OrderedDict(
    data=None,
    key=None)
outputs=OrderedDict(
    value=None)

class GetValue(Operation):
    """Unpack a `value` from container `data`, given a valid `key`"""

    def __init__(self):
        super(GetValue,self).__init__(inputs,outputs)        
        self.input_doc['data'] = 'A data structure'
        self.input_doc['key'] = 'A valid key for `data`.__getitem__'
        self.output_doc['value'] = 'The value stored at `data`[`key`]'

    def run(self):
        self.outputs['value'] = self.inputs['data'][self.inputs['key']] 

