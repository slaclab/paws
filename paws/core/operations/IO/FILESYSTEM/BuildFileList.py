from collections import OrderedDict
import glob
import os

from ...Operation import Operation

inputs=OrderedDict(
    dir_path=None,
    regex='*.tif')
outputs=OrderedDict(file_list=None)

class BuildFileList(Operation):
    """
    Read a directory and filter its contents with a regular expression
    to form a list of file paths.
    """

    def __init__(self):
        super(BuildFileList,self).__init__(inputs,outputs)
        self.input_doc['dir_path'] = 'path to directory containing files'
        self.input_doc['regex'] = 'regular expression to select files'
        
    def run(self):
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        fl = glob.glob(os.path.join(dirpath,rx))
        self.outputs['file_list'] = fl

