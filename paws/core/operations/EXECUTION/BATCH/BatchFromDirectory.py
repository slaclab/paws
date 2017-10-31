from collections import OrderedDict
import glob
import os
import copy

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

inputs=OrderedDict(
    dir_path=None,
    regex='*.tif',
    workflow=None,
    input_name=None,
    extra_input_names=[],
    extra_inputs=[])
outputs=OrderedDict(batch_inputs=None,batch_outputs=None)

class BatchFromDirectory(Operation):
    """
    Read a directory and filter its contents with a regular expression
    to form  a list of file paths to be used as inputs
    for the repeated execution of a specified Workflow.
    Specify, by workflow uri, where this file path will be fed to the workflow.
    Collect outputs from the Workflow for each of the input files.
    """

    def __init__(self):
        super(BatchFromDirectory,self).__init__(inputs,outputs)
        self.input_doc['dir_path'] = 'path to directory containing batch of files to be used as input'
        self.input_doc['regex'] = 'string with * wildcards to select input files from dir_path'
        self.input_doc['workflow'] = 'the Workflow to be executed'
        self.input_doc['input_name'] = 'name of the workflow input '\
            'where the file paths will be used'
        self.input_doc['extra_input_names'] = 'list of names '\
            'of batch workflow inputs to be set to extra_inputs before batch-execution'
        self.input_doc['extra_inputs'] = 'data items '\
            'to be set to batch workflow inputs indicated by extra_input_names'
        self.input_type['workflow'] = opmod.entire_workflow
        
    def run(self):
        wf = self.inputs['workflow']
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        inpname = self.inputs['input_name']
        batch_list = glob.glob(os.path.join(dirpath,rx))
        n_batch = len(batch_list)
        self.outputs['batch_inputs'] = [None for ib in range(n_batch)] 
        self.outputs['batch_outputs'] = [None for ib in range(n_batch)] 
        if self.data_callback: 
            self.data_callback('outputs.batch_inputs',[None for ib in range(n_batch)])
            self.data_callback('outputs.batch_outputs',[None for ib in range(n_batch)])
        inps = self.inputs['extra_input_names']
        vals = self.inputs['extra_inputs']
        # Load any additional inputs...
        if any(inps): 
            for inpnm,inpval in zip(inps,vals):
                wf.set_wf_input(inpnm,inpval)
        self.message_callback('STARTING BATCH')
        for i,filename in zip(range(n_batch),batch_list):
            inp_dict = OrderedDict() 
            inp_dict[inpname] = filename
            wf.set_wf_input(inpname,filename)
            self.message_callback('BATCH RUN {} / {}'.format(i,n_batch-1))
            wf.execute()
            out_dict = wf.wf_outputs_dict()
            self.outputs['batch_inputs'][i] = inp_dict
            self.outputs['batch_outputs'][i] = out_dict
            if self.data_callback: 
                self.data_callback('outputs.batch_inputs.'+str(i),inp_dict)
                self.data_callback('outputs.batch_outputs.'+str(i),copy.deepcopy(out_dict))
        self.message_callback('BATCH FINISHED')

