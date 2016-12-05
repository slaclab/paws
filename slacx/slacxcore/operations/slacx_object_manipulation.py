from slacxop import Operation
import optools


'''
class selectBatchItems(Operation):
    """Return list of outputs for a given variable from batch."""

    def __init__(self):
        input_names = ['batch_outputs','from_outputs','operation','var_name']
        output_names = ['var_list']
        super(selectBatchItems, self).__init__(input_names, output_names)
        self.input_doc['ndarray'] = 'ndarray of any type or shape'
        self.output_doc['any_zeros'] = 'existence of any zero / False elements'
        # source & type
        self.input_src['ndarray'] = optools.wf_input
        self.categories = ['MISC.NDARRAY MANIPULATION']

    def run(self):
        batch_outputs = self.inputs['batch_outputs']
        if self.inputs['from_outputs'] == True:
            source = 'outputs'
        else:
            source = 'inputs'
        num_items = len(batch_outputs)
        batch['outputs']['batch_outputs'][ii][operation][source]['var_name']
'''


class selectBatchTest(Operation):
    """Return a single output from batch."""

    def __init__(self):
        input_names = ['batch_outputs','index','from_outputs','operation','var_name']
        output_names = ['var0','var1','var2','var3']
        #output_names = ['var']
        super(selectBatchTest, self).__init__(input_names, output_names)
        #self.input_doc['ndarray'] = 'ndarray of any type or shape'
        #self.output_doc['any_zeros'] = 'existence of any zero / False elements'
        # source & type
        self.input_src['batch_outputs'] = optools.wf_input
        self.input_src['index'] = optools.user_input
        self.input_src['from_outputs'] = optools.user_input
        self.input_src['operation'] = optools.user_input
        self.input_src['var_name'] = optools.user_input
        self.input_type['index'] = optools.int_type
        self.input_type['from_outputs'] = optools.bool_type
        self.input_type['operation'] = optools.str_type
        self.input_type['var_name'] = optools.str_type
        # defaults
        #self.inputs['from_inputs'] = True
        self.categories = ['MISC.SLACX OBJECT MANIPULATION']

    def run(self):
        batch_outputs = self.inputs['batch_outputs']
        if self.inputs['from_outputs'] == True:
            source = 'outputs'
        else:
            source = 'inputs'
        index = int(self.inputs['index'])
        op_name = self.inputs['operation']
        var_name = self.inputs['var_name']
        self.outputs['var0'] = batch_outputs[index]
        self.outputs['var1'] = batch_outputs[index][op_name]
        self.outputs['var2'] = batch_outputs[index][op_name][source]
        self.outputs['var3'] = batch_outputs[index][op_name][source][var_name]
