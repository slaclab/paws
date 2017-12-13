from collections import OrderedDict
import glob
import copy

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

inputs=OrderedDict(
    arrays=None,
    workflow=None,
    input_keys=None)
outputs=OrderedDict(
    batch_inputs=None,
    batch_outputs=None)

class BatchFromArrays(Operation):
    """Batch-execute a workflow using an array of inputs"""

    def __init__(self):
        super(BatchFromArrays,self).__init__(inputs,outputs)
        self.input_doc['arrays'] = 'list of arrays, all of the same size'
        self.input_doc['workflow'] = 'the workflow to be executed in this batch'
        self.input_doc['input_keys'] = 'keys for setting workflow inputs, '\
            'corresponding to the input `arrays`'
        self.output_doc['batch_inputs'] = 'list of dicts of input_key:input_value for each of the input_keys'
        self.output_doc['batch_outputs'] = 'list of dicts of workflow outputs'
        self.input_type['workflow'] = opmod.entire_workflow
        
    def run(self):
        arrs = self.inputs['arrays']
        inpks = self.inputs['input_keys']
        wf = self.inputs['workflow']
        n_batch = len(arrs[0])

        self.outputs['batch_inputs'] = [None for ib in range(n_batch)] 
        self.outputs['batch_outputs'] = [None for ib in range(n_batch)] 
        if self.data_callback: 
            self.data_callback('outputs.batch_inputs',[None for ib in range(n_batch)])
            self.data_callback('outputs.batch_outputs',[None for ib in range(n_batch)])

        self.message_callback('STARTING BATCH')
        for i in range(n_batch):
            inp_dict = OrderedDict() 
            for inpk,arr in zip(inpks,arrs):
                inp_dict[inpk] = arr[i]
                wf.set_wf_input(inpk,arr[i])
            self.message_callback('BATCH RUN {} / {}'.format(i,n_batch-1))
            wf.execute()
            out_dict = wf.wf_outputs_dict()
            self.outputs['batch_inputs'][i] = inp_dict
            self.outputs['batch_outputs'][i] = out_dict
            if self.data_callback: 
                self.data_callback('outputs.batch_inputs.'+str(i),inp_dict)
                self.data_callback('outputs.batch_outputs.'+str(i),copy.deepcopy(out_dict))
        self.message_callback('BATCH FINISHED')

