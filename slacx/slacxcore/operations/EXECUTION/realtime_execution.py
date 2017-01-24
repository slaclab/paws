import re
from collections import OrderedDict
import glob

from ..slacxop import Realtime 
from .. import optools
from ...slacxtools import FileSystemIterator 

class RealtimeFromFiles(Realtime):
    """
    Provides inputs to be used in repeated execution of a workflow
    from files with names matching a regex, as they arrive in a specified directory.
    Collects the outputs produced for each of the inputs.
    """

    def __init__(self):
        input_names = ['dir_path','regex','input_route','downstream_ops','saved_items']
        output_names = ['batch_inputs','batch_outputs']
        super(RealtimeFromFiles,self).__init__(input_names,output_names)
        self.input_doc['dir_path'] = 'path to directory containing batch of files to be used as input'
        self.input_doc['regex'] = 'string with * wildcards that will be substituted to indicate input files'
        self.input_doc['input_route'] = 'inputs constructed by the batch executor are directed to this uri'
        self.input_doc['downstream_ops'] = 'list of ops to be included in the realtime execution'
        self.input_doc['saved_items'] = 'list of ops to be saved in the realtime_outputs'
        self.output_doc['realtime_inputs'] = 'iterator over dicts of [input_route:input_value] generated in real time from the local filesystem'
        self.output_doc['realtime_outputs'] = 'list of dicts of [output_route:output_value]'
        self.input_src['dir_path'] = optools.fs_input
        self.input_src['regex'] = optools.user_input 
        self.input_src['input_route'] = optools.wf_input 
        self.input_src['downstream_ops'] = optools.wf_input 
        self.input_src['saved_items'] = optools.wf_input 
        self.input_type['regex'] = optools.str_type
        self.input_type['downstream_ops'] = optools.list_type 
        self.input_type['saved_items'] = optools.list_type 
        self.inputs['regex'] = '*.tif' 
        self.inputs['downstream_ops'] = []
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
        self.outputs['batch_inputs'] = FileSystemIterator(dirpath,rx)
        self.outputs['batch_outputs'] = [] 

    def input_iter(self):
        return self.outputs['batch_inputs']

    def output_list(self):
        return self.outputs['batch_outputs']

    def input_routes(self):
        """Use the Realtime.input_locators to list uri's of all input routes"""
        return optools.val_list(self.input_locator['input_route'])

    def downstream_ops(self):
        """Use the Realtime.input_locator to list uri's of ops to be saved/stored after execution"""
        return optools.val_list(self.input_locator['saved_items'])

    def saved_items(self):
        """Use the Realtime.input_locator to list uri's of ops to be included in realtime execution"""
        return optools.val_list(self.input_locator['downstream_ops'])

    @staticmethod
    def delay():
        """Amount of time to wait between execution attempts, in milliseconds"""
        return 1000




