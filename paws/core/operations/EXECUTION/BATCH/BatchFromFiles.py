from collections import OrderedDict

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

class BatchFromFiles(Operation):
    """
    Take a list of file paths and use them as inputs
    for the repeated execution of a specified Workflow.
    Specify, by workflow uri, where this file path will be fed to the workflow.
    Collect outputs from the Workflow for each of the input files.
    """

    def __init__(self):
        input_names = ['file_list','workflow','input_name']
        output_names = ['batch_inputs','batch_outputs']
        super(BatchFromFiles,self).__init__(input_names,output_names)
        self.input_doc['file_list'] = 'list of file paths'
        self.input_doc['workflow'] = 'the Workflow to be executed'
        self.input_doc['input_name'] = 'name of the workflow input where the file paths will be used'
        self.output_doc['batch_inputs'] = 'list of dicts of [input_name:input_value]'
        self.output_doc['batch_outputs'] = 'list of dicts of [output_name:output_value] for all Workflow outputs'
        self.input_type['workflow'] = opmod.entire_workflow
        
    def run(self):
        batch_list = self.inputs['file_list'] 
        inpname = self.inputs['input_name'] 
        wf = self.inputs['workflow'] 
        input_dict_list = []
        output_dict_list = []
        n_batch = len(batch_list)
        wf.write_log('STARTING BATCH')
        for i,filename in zip(range(n_batch),batch_list):
            inp_dict = OrderedDict() 
            inp_dict[inpname] = filename
            wf.set_wf_input(inpname,filename)
            wf.write_log('BATCH RUN {} / {}'.format(i+1,n_batch))
            wf.execute()
            input_dict_list.append(inp_dict)
            output_dict_list.append(wf.wf_outputs_dict())
        wf.write_log('BATCH FINISHED')
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




