import re
from collections import OrderedDict
import glob

from ..operation import Realtime 
from .. import optools
from ...pawstools import FileSystemIterator 

class RealtimeFromFiles(Realtime):
    """
    Provides inputs to be used in repeated execution of a workflow
    from files with names matching a regex, as they arrive in a specified directory.
    Collects the outputs produced for each of the inputs.
    """

    def __init__(self):
        input_names = ['dir_path','regex','input_route','realtime_ops','saved_items']
        output_names = ['realtime_inputs','realtime_outputs']
        super(RealtimeFromFiles,self).__init__(input_names,output_names)
        self.input_doc['dir_path'] = 'path to directory where files will be written and then used as input'
        self.input_doc['regex'] = 'string with * wildcards used to filter or locate input files'
        self.input_doc['input_route'] = 'inputs constructed by the realtime executor are directed to this uri'
        self.input_doc['realtime_ops'] = str('list of ops to be included in the realtime execution- '
        + 'the order of operations in realtime_ops is unimportant, as the proper execution stack is resolved at runtime')
        self.input_doc['saved_items'] = 'list of ops to be saved in the realtime_outputs'
        self.output_doc['realtime_inputs'] = str('iterator over dicts of [input_route:input_value] '
        + 'generated in real time from the local filesystem')
        self.output_doc['realtime_outputs'] = 'list of dicts of [output_route:output_value]'
        self.input_src['dir_path'] = optools.fs_input
        self.input_src['regex'] = optools.text_input 
        self.input_src['input_route'] = optools.wf_input 
        self.input_src['realtime_ops'] = optools.wf_input 
        self.input_src['saved_items'] = optools.wf_input 
        self.input_type['dir_path'] = optools.path_type
        self.input_type['regex'] = optools.str_type
        self.input_type['input_route'] = optools.path_type
        self.input_type['realtime_ops'] = optools.path_type 
        self.input_type['saved_items'] = optools.path_type 
        self.inputs['regex'] = '*.tif' 
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
        self.outputs['realtime_inputs'] = FileSystemIterator(dirpath,rx)
        self.outputs['realtime_outputs'] = [] 

    def input_iter(self):
        return self.outputs['realtime_inputs']

    def output_list(self):
        return self.outputs['realtime_outputs']

    def input_routes(self):
        """Use the Realtime.input_locators to list uri's of all input routes- must return list."""
        return [self.input_locator['input_route'].val]

    def realtime_ops(self):
        """Use the Realtime.input_locator to list uri's of ops to be saved/stored after execution"""
        return self.input_locator['realtime_ops'].val

    def saved_items(self):
        """Use the Realtime.input_locator to list uri's of ops to be included in realtime execution"""
        return self.input_locator['saved_items'].val

    @staticmethod
    def delay():
        """Amount of time to wait between execution attempts, in milliseconds"""
        return 1000




