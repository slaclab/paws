from collections import OrderedDict
import glob
import os

from ...Operation import Operation
from ... import optools

inputs=OrderedDict(
    dir_path=None,
    regex='*.tif',
    new_files_only=False)
outputs=OrderedDict(file_iterator=None)

class FileIterator(Operation):
    """Iterate over files matching a regex in a directory"""

    def __init__(self):
        super(FileIterator,self).__init__(inputs,outputs)
        self.input_doc['dir_path'] = 'path to directory containing files'
        self.input_doc['regex'] = 'regular expression to select files'
        self.input_doc['new_files_only'] = 'regular expression to select files'

    def run(self):
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        process_existing_files = not self.inputs['new_files_only']
        it = optools.FileSystemIterator(dirpath,rx,process_existing_files) 
        self.outputs['file_iterator'] = it


