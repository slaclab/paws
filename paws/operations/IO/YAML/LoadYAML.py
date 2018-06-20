from collections import OrderedDict
import os

import numpy as np
import yaml

from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(
    data=None,
    dir_path=None,
    filename=None)

class LoadYAML(Operation):
    """Load data from a YAML file with yaml.load()"""

    def __init__(self):
        super(LoadYAML, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to YAML-formatted data file'
        self.output_doc['data'] = 'the result of yaml.load(file_path)' 
        self.output_doc['dir_path'] = 'directory path'
        self.output_doc['filename'] = 'filename with path and extension stripped'

    def run(self):
        p = self.inputs['file_path']
        self.message_callback('loading {}'.format(p))
        dir_path,filename = os.path.split(p)
        file_noext = os.path.splitext(filename)[0]
        self.outputs['dir_path'] = dir_path 
        self.outputs['filename'] = file_noext 
        f = open(p,'r')
        ds = yaml.load(f)
        f.close()
        self.outputs['data'] = ds 

