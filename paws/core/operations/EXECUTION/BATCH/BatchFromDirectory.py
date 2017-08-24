from collections import OrderedDict
import glob
import os

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

class BatchFromDirectory(Operation):
    """
    Read a directory and filter its contents with a regular expression
    to form  a list of file paths to be used as inputs
    for the repeated execution of a specified Workflow.
    Specify, by workflow uri, where this file path will be fed to the workflow.
    Collect outputs from the Workflow for each of the input files.
    """

    def __init__(self):
        input_names = ['dir_path','regex','workflow','input_name']
        output_names = ['batch_inputs','batch_outputs']
        super(BatchFromDirectory,self).__init__(input_names,output_names)
        self.input_doc['dir_path'] = 'path to directory containing batch of files to be used as input'
        self.input_doc['regex'] = 'string with * wildcards that will be substituted to indicate input files'
        self.input_doc['workflow'] = 'the Workflow to be executed'
        self.input_doc['input_name'] = 'name of the workflow input where the file paths will be used'
        self.output_doc['batch_inputs'] = 'list of dicts of [input_name:input_value]'
        self.output_doc['batch_outputs'] = 'list of dicts of [output_name:output_value] for all Workflow outputs'
        self.input_type['workflow'] = opmod.entire_workflow
        self.inputs['regex'] = '*.tif' 
        
    def run(self):
        wf = self.inputs['workflow']
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        inpname = self.inputs['input_name']
        batch_list = glob.glob(os.path.join(dirpath,rx))
        input_dict_list = []
        output_dict_list = []
        n_batch = len(batch_list)
        for i,filename in zip(range(n_batch),batch_list):
            inp_dict = OrderedDict() 
            inp_dict[inpname] = filename
            #import pdb; pdb.set_trace()
            wf.set_wf_input(inpname,filename)
            wf.execute()
            #stk,diag = wf.execution_stack()
            #for lst in stk:
            #    wf.write_log('batch {}/{}: running {}'.format(i,n_batch,op_list))
            #    for op_tag in lst: 
            #        op = self.workflows[wfname].get_data_from_uri(op_tag) 
            #        optools.load_inputs(op,wf.wf_manager,wf.wf_manager.plugin_manager)
            #    self.workflows[wfname].execute(op_list)
            input_dict_list.append(inp_dict)
            output_dict_list.append(wf.wf_outputs_dict())
        self.outputs['batch_inputs'] = input_dict_list
        self.outputs['batch_outputs'] = output_dict_list 

    def input_list(self):
        return self.outputs['batch_inputs']

    def output_list(self):
        return self.outputs['batch_outputs']

    def input_routes(self):
        """Provide the input route- a list is expected"""
        #return [self.input_locator['input_route'].val]
        if isinstance(self.inputs['input_route'],list):
            return self.inputs['input_route']
        else:
            return [self.inputs['input_route']]

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
        self.inputs['batch_ops'] = optools.locate_input(self.input_locator['batch_ops'],wf)

    def set_input_routes(self,wf=None):
        self.inputs['input_route'] = optools.locate_input(self.input_locator['input_route'],wf)




