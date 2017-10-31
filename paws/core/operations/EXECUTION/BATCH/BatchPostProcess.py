from collections import OrderedDict
import glob
import copy

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

inputs=OrderedDict(
    batch_outputs=None,
    workflow=None,
    output_keys=None,
    input_keys=None)
outputs=OrderedDict(batch_inputs=None,batch_outputs=None)

class BatchPostProcess(Operation):
    """
    Take the batch output (list of dicts) from a previously completed Batch,
    and use each dict to form inputs for the execution of a post-processing workflow.
    For each item to be taken from the previous batch, two keys are needed:
    one key indicates a previous batch workflow output, 
    and another indicates the corresponding current workflow input.
    """

    def __init__(self):
        super(BatchPostProcess,self).__init__(inputs,outputs)
        self.input_doc['batch_outputs'] = 'list of dicts produced as batch output from another batch execution operation'
        self.input_doc['workflow'] = 'the workflow to be executed in this batch'
        self.input_doc['output_keys'] = 'list of keys for harvesting batch outputs'
        self.input_doc['input_keys'] = 'list of keys for setting workflow inputs, in corresponding order to output_keys'
        self.output_doc['batch_inputs'] = 'list of dicts of input_key:input_value for each of the input_keys'
        self.output_doc['batch_outputs'] = 'list of dicts of workflow outputs'
        self.input_type['workflow'] = opmod.entire_workflow
        self.input_type['batch_outputs'] = opmod.workflow_item
        
    def run(self):
        b_out = self.inputs['batch_outputs']
        out_keys = self.inputs['output_keys']
        inp_keys = self.inputs['input_keys']
        wf = self.inputs['workflow']
        n_batch = len(b_out)
        self.outputs['batch_inputs'] = [None for ib in range(n_batch)] 
        self.outputs['batch_outputs'] = [None for ib in range(n_batch)] 
        if self.data_callback: 
            self.data_callback('outputs.batch_inputs',[None for ib in range(n_batch)])
            self.data_callback('outputs.batch_outputs',[None for ib in range(n_batch)])
        self.message_callback('STARTING BATCH')
        for i,d_out in zip(range(n_batch),b_out):
            inp_dict = OrderedDict() 
            for kout,kin in zip(out_keys,inp_keys):
                inp_dict[kin] = d_out[kout]
                wf.set_wf_input(kin,d_out[kout])
            self.message_callback('BATCH RUN {} / {}'.format(i,n_batch-1))
            wf.execute()
            out_dict = wf.wf_outputs_dict()
            self.outputs['batch_inputs'][i] = inp_dict
            self.outputs['batch_outputs'][i] = out_dict
            if self.data_callback: 
                self.data_callback('outputs.batch_inputs.'+str(i),inp_dict)
                self.data_callback('outputs.batch_outputs.'+str(i),copy.deepcopy(out_dict))
        self.message_callback('BATCH FINISHED')

