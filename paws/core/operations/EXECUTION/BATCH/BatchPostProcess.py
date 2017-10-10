from collections import OrderedDict
import glob

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

class BatchPostProcess(Operation):
    """
    Take the batch output (list of dicts) from a previously completed Batch,
    and use each dict to form inputs for the execution of a post-processing workflow.
    For each item to be taken from the previous batch, two keys are needed:
    one key indicates a previous batch workflow output, 
    and another indicates the corresponding current workflow input.
    """

    def __init__(self):
        input_names = ['batch_output','output_keys','workflow','input_keys']
        output_names = ['batch_inputs','batch_outputs']
        super(BatchPostProcess,self).__init__(input_names,output_names)
        self.input_doc['batch_output'] = 'list of dicts produced as batch output from another batch execution operation'
        self.input_doc['output_keys'] = 'list of keys for harvesting batch outputs (must be outputs of the previous batch workflow)'
        self.input_doc['workflow'] = 'a reference to the workflow to be executed in this batch'
        self.input_doc['input_keys'] = 'list of keys for setting workflow inputs, in corresponding order to output_keys'
        self.output_doc['batch_inputs'] = 'list of dicts of input_key:input_value for each of the input_keys'
        self.output_doc['batch_outputs'] = 'list of dicts of workflow outputs'
        self.input_type['workflow'] = opmod.entire_workflow
        self.input_type['batch_output'] = opmod.workflow_item
        
    def run(self):
        """
        Build a list of [uri:value] dicts to be used in the workflow.
        """
        batch_output = self.inputs['batch_output']
        out_keys = self.inputs['output_keys']
        inp_keys = self.inputs['input_keys']
        wf = self.inputs['workflow']
        if (wf is None or batch_output is None or out_keys is None or inp_keys is None):
            return
        self.outputs['batch_inputs'] = []
        self.outputs['batch_outputs'] = []
        n_batch = len(batch_output)
        for d_out in batch_output:
            inp_dict = OrderedDict() 
            for kout,kin in zip(out_keys,inp_keys):
                inp_dict[kin] = d_out[kout]
                wf.set_wf_input(kin,d_out[kout])
            wf.execute()
            self.outputs['batch_inputs'].append(inp_dict)
            self.outputs['batch_outputs'].append(wf.wf_outputs_dict())

