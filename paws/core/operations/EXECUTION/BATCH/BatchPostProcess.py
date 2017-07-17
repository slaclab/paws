from collections import OrderedDict
import glob

from ... import Operation as op
from ...Operation import Batch
from ... import optools

class BatchPostProcess(Batch):
    """
    Take the batch output (list of dicts) from a previously completed Batch,
    and use each dict to form inputs for the execution of a post-processing workflow.
    For each input to be taken from the dict, two uris are needed:
    one to locate it within the (previous) batch outputs, 
    and another to specify where it will be fed to the (current) workflow.
    Collect specified outputs from the workflow for each of the inputs.
    """

    def __init__(self):
        input_names = ['batch_output','batch_uris','input_routes','batch_ops','saved_items']
        output_names = ['batch_inputs','batch_outputs']
        super(BatchPostProcess,self).__init__(input_names,output_names)
        self.input_doc['batch_output'] = ''
        self.input_doc['batch_uris'] = str('uris from batch_output at which the inputs for the current workflow should be found- '
        + ' one batch_uri is expected for each of the input_routes')
        self.input_doc['input_routes'] = 'inputs found from batch_uris are directed to these inputs, which should all be within in batch_ops'
        self.input_doc['batch_ops'] = str('list of workflow uris pointing to Operations to be included in batch execution- '
        + 'the order of entries is unimportant, as the proper execution stack is resolved at runtime')
        self.input_doc['saved_items'] = 'list of uris to be saved in the batch_outputs'
        self.output_doc['batch_inputs'] = 'list of dicts of [input_route:input_value] as determined by batch_uris and input_routes'
        self.output_doc['batch_outputs'] = 'list of dicts of [output_route:output_value] for all saved_items '
        self.input_src['batch_output'] = op.plugin_input
        self.input_src['batch_uris'] = op.wf_input 
        self.input_src['input_routes'] = op.wf_input 
        self.input_src['batch_ops'] = op.wf_input 
        self.input_src['saved_items'] = op.wf_input 
        self.input_type['batch_output'] = op.ref_type
        self.input_type['batch_uris'] = op.path_type
        self.input_type['input_routes'] = op.path_type
        self.input_type['batch_ops'] = op.path_type 
        self.input_type['saved_items'] = op.path_type 
        self.inputs['batch_uris'] = []
        self.inputs['input_routes'] = []
        self.inputs['batch_ops'] = []
        self.inputs['saved_items'] = []
        
    def run(self):
        """
        Build a list of [uri:value] dicts to be used in the workflow.
        """
        b_prev = self.inputs['batch_output']
        b_uris = self.inputs['batch_uris']
        inp_rts = self.inputs['input_routes']
        input_dict_list = []
        output_dict_list = []
        for b_out in b_prev:
            inp_dict = OrderedDict() 
            for b_uri,inp_rt in zip(b_uris,inp_rts):
                inp_dict[inp_rt] = optools.get_uri_from_dict(b_uri,b_out)
            input_dict_list.append(inp_dict)
            output_dict_list.append(OrderedDict())
        self.outputs['batch_inputs'] = input_dict_list
        # Instantiate the batch_outputs list
        self.outputs['batch_outputs'] = output_dict_list 

    def input_list(self):
        return self.outputs['batch_inputs']

    def output_list(self):
        return self.outputs['batch_outputs']

    def input_routes(self):
        """Provide the input route- currently batch execution expects a list."""
        if isinstance(self.inputs['input_routes'],list):
            return self.inputs['input_routes']
        else: 
            return [self.inputs['input_routes']]

    def batch_ops(self):
        """Provide a list of uri's of ops to be included in batch execution"""
        if isinstance(self.inputs['batch_ops'],list):
            return self.inputs['batch_ops']
        else: 
            return [self.inputs['batch_ops']]

    def saved_items(self):
        """List uris to be saved/stored after execution"""
        if isinstance(self.inputs['saved_items'],list):
            return self.inputs['saved_items']
        else: 
            return [self.inputs['saved_items']]

    def batch_outputs_tag(self):
        return 'batch_outputs'

    def set_batch_ops(self,wf=None):
        data = optools.locate_input(self.input_locator['batch_ops'],wf)
        self.input_locator['batch_ops'].data = data 
        self.inputs['batch_ops'] = data

    def set_input_routes(self,wf=None):
        data = optools.locate_input(self.input_locator['input_routes'],wf)
        self.input_locator['input_routes'].data = data 
        self.inputs['input_routes'] = data





