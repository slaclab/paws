from collections import OrderedDict
import glob
import os
import re

from ..Operation import Operation

inputs=OrderedDict(
    dir_path=None,
    regex='*',
    filter_regex=None)
outputs=OrderedDict(
    file_list=None,
    filename_list=None)

class BuildFileList(Operation):
    """
    Read a directory and filter its contents with a regular expression
    to form a list of file paths.
    """

    def __init__(self):
        super(BuildFileList,self).__init__(inputs,outputs)
        self.input_doc['dir_path'] = 'path to directory containing files'
        self.input_doc['regex'] = 'unix-like regex to select files'
        self.input_doc['filter_regex'] = 'regex used to filter output'
        
    def run(self):
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        frx = self.inputs['filter_regex']
        globex = os.path.join(dirpath,rx)
        self.message_callback('seeking files matching {}'.format(globex))
        fl = glob.glob(globex)
        if frx is not None:
            fl = list(filter(re.compile(frx).match,fl))
        fnamel = [os.path.split(p)[-1] for p in fl] 
        self.outputs['file_list'] = fl
        self.outputs['filename_list'] = fnamel

