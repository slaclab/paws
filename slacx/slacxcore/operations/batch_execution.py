import re

from slacxop import Operation
import optools

class BatchFromFiles(Operation):
    """
    Provides a sequence of inputs to be used in repeated execution of a workflow.
    Collects the outputs produced for each of the inputs in the sequence.
    """

    def __init__(self):
        input_names = ['dir_path','regex','substitutions']
        output_names = ['batch_iterator','batch_outputs']
        super(BatchFromFiles,self).__init__(input_names,output_names)
        self.input_doc['dir_path'] = 'path to directory containing batch of files to be used as input'
        self.input_doc['regex'] = 'string with * wildcards that will be substituted to indicate input files'
        self.input_doc['substitutions'] = 'list of substitutions for regex to build file names'
        self.output_doc['batch_iterator'] = 'iterator whose next() method emits the next file path'
        self.output_doc['batch_outputs'] = 'Dict of dicts containing the workflow outputs for each input file'
        self.categories = ['EXECUTION.BATCH']
        self.input_src['dir_path'] = optools.fs_input
        self.input_src['regex'] = optools.text_input 
        self.input_src['substitutions'] = optools.op_input 
        self.input_type['regex'] = optools.str_type
        
    def run(self):
        """
        For Batch, this should form a list of inputs to be used in the workflow,
        then wrap that list in an iterator and return that iterator.
        """
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        subs = self.inputs['substitutions']
        # Perform the computation
        batch_list = [dirpath+'/'*rx.replace('*',sub) for sub in subs]
        # Save the output
        #self.outputs['batch_iterator'] = iter(batch_list) 
        self.outputs['batch_iterator'] = batch_list 
        # Instantiate the batch_output dict
        self.outputs['batch_outputs'] = dict.fromkeys(batch_list)

