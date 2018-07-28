from collections import OrderedDict

import os.path

from ...Operation import Operation

inputs=OrderedDict(
    file_path=None)
outputs=OrderedDict(
    file_exists=None)

class CheckFilePath(Operation):
    """Checks a file path and returns whether or not the file exists"""

    def __init__(self):
        super(CheckFilePath, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'filesystem path'
        self.output_doc['file_exists'] = 'boolean indicating '\
        'whether or not file exists' 

    def run(self):
        fp = self.inputs['file_path']
        self.message_callback('checking file path {}'.format(fp))
        if fp:
            self.outputs['file_exists'] = os.path.exists(fp)
        else:
            self.outputs['file_exists'] = False 


