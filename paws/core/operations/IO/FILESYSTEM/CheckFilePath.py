from collections import OrderedDict

import os.path

from ...Operation import Operation
from ... import Operation as opmod 

inputs=OrderedDict(
    file_path=None)
outputs=OrderedDict(
    file_exists_flag=None)

class CheckFilePath(Operation):
    """Checks a file path and returns whether or not the file exists"""

    def __init__(self):
        super(CheckFilePath, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'filesystem path'
        self.output_doc['file_exists_flag'] = 'boolean indicating '\
        'whether or not file exists' 

    def run(self):
        fp = self.inputs['file_path']
        self.outputs['file_path'] = os.path.exists(fp)

