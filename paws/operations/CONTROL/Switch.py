from collections import OrderedDict

from ..Operation import Operation

inputs=OrderedDict(
    iftrue_data=None,
    else_data=None,
    condition=None,
    truth_condition=None)

outputs=OrderedDict(
    data=None)
        
class Switch(Operation):
    """Output one of two different inputs depending on an input condition"""

    def __init__(self):
        super(Switch,self).__init__(inputs,outputs)
        self.input_doc['iftrue_data'] = 'the output value if `condition`==`truth_condition`'
        self.input_doc['else_data'] = 'the output value if not `condition`==`truth_condition`'
        self.input_doc['condition'] = 'condition for deciding whether or not to run'
        self.input_doc['truth_condition'] = 'value to compare against `condition`'
        self.output_doc['data'] = 'the piece of data selected by the `condition`'

    def run(self):
        cond = self.inputs['condition']
        tcond = self.inputs['truth_condition']
        if cond == tcond: 
            self.outputs['data'] = self.inputs['iftrue_data'] 
        else:
            self.outputs['data'] = self.inputs['else_data'] 

