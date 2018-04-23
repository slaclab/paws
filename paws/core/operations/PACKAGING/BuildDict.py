from collections import OrderedDict

from ..Operation import Operation

inputs = OrderedDict(
    dict_keys=None,
    dict_values=None)
outputs = OrderedDict(
    new_dict=None)

class BuildDict(Operation):
    """Create a dict from keys and values"""

    def __init__(self):
        super(BuildDict, self).__init__(inputs, outputs)
        self.input_doc['dict_keys'] = 'list of dict keys'
        self.input_doc['dict_values'] = 'list of dict values'
        self.output_doc['new_dict'] = 'output dict containing keys and values'

    def run(self):
        nd = OrderedDict() 
        for k,v in zip(self.inputs['dict_keys'],self.inputs['dict_values']):
            nd[k] = v
        self.outputs['new_dict'] = nd 

