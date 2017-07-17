from ... import Operation as op
from ...Operation import Realtime 
from ... import optools

class RealtimeFromFiles(Realtime):
    """
    Provides inputs to be used in repeated execution of a workflow
    from files with names matching a regex, as they arrive in a specified directory.
    Collects the outputs produced for each of the inputs.
    """

    def __init__(self):
        input_names = ['dir_path','regex','new_files_only','input_route','realtime_ops','saved_items']
        output_names = ['realtime_inputs','realtime_outputs']
        super(RealtimeFromFiles,self).__init__(input_names,output_names)
        self.input_doc['dir_path'] = 'path to directory where files will be written and then used as input'
        self.input_doc['regex'] = 'string with * wildcards used to filter or locate input files'
        self.input_doc['new_files_only'] = 'if true, ignore existing files and only process new arrivals'
        self.input_doc['input_route'] = 'inputs constructed by the realtime executor are directed to this uri'
        self.input_doc['realtime_ops'] = str('list of ops to be included in the realtime execution- '
        + 'the order of operations in realtime_ops is unimportant, as the proper execution stack is resolved at runtime')
        self.input_doc['saved_items'] = 'list of ops to be saved in the realtime_outputs'
        self.output_doc['realtime_inputs'] = str('iterator over dicts of [input_route:input_value] '
        + 'generated in real time from the local filesystem')
        self.output_doc['realtime_outputs'] = 'list of dicts of [output_route:output_value]'
        self.input_src['dir_path'] = op.fs_input
        self.input_src['regex'] = op.text_input 
        self.input_src['new_files_only'] = op.text_input 
        self.input_src['input_route'] = op.wf_input 
        self.input_src['realtime_ops'] = op.wf_input 
        self.input_src['saved_items'] = op.wf_input 
        self.input_type['dir_path'] = op.path_type
        self.input_type['regex'] = op.str_type
        self.input_type['new_files_only'] = op.bool_type
        self.input_type['input_route'] = op.path_type
        self.input_type['realtime_ops'] = op.path_type 
        self.input_type['saved_items'] = op.path_type 
        self.inputs['regex'] = '*.tif' 
        self.inputs['new_files_only'] = True 
        self.inputs['realtime_ops'] = []
        self.inputs['saved_items'] = []
        
    def run(self):
        """
        This should create an iterator 
        whose next() gives a {uri:value} dict 
        built from the latest-arrived file 
        """
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        inproute = self.inputs['input_route']
        process_existing_files = not self.inputs['new_files_only']
        self.outputs['realtime_inputs'] = optools.FileSystemIterator(dirpath,rx,process_existing_files)
        self.outputs['realtime_outputs'] = [] 

    def input_iter(self):
        return self.outputs['realtime_inputs']

    def output_list(self):
        return self.outputs['realtime_outputs']

    def input_routes(self):
        """Use the Realtime.input_locators to list uri's of all input routes- must return list."""
        if isinstance(self.inputs['input_route'],list):
            return self.inputs['input_route']
        else:
            return [self.inputs['input_route']]

    def batch_ops(self):
        """Use the Realtime.input_locator to list uri's of ops to be saved/stored after execution"""
        if isinstance(self.inputs['realtime_ops'],list):
            return self.inputs['realtime_ops']
        else:
            return [self.inputs['realtime_ops']]

    def saved_items(self):
        """Use the Realtime.input_locator to list uri's of ops to be included in realtime execution"""
        if isinstance(self.inputs['saved_items'],list):
            return self.inputs['saved_items']
        else:
            return [self.inputs['saved_items']]

    def batch_outputs_tag(self):
        return 'realtime_outputs'

    @staticmethod
    def delay():
        """Amount of time to wait between execution attempts, in milliseconds"""
        return 1000

    def set_batch_ops(self,wf=None):
        data = optools.locate_input(self.input_locator['realtime_ops'],wf)
        self.inputs['realtime_ops'] = data
        #self.input_locator['realtime_ops'].data = data 

    def set_input_routes(self,wf=None):
        data = optools.locate_input(self.input_locator['input_route'],wf)
        self.inputs['input_route'] = data
        #self.input_locator['input_route'].data = data 


