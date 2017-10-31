from collections import OrderedDict

import numpy as np

import yaml
from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(yaml_output=None)

class LoadYAML(Operation):
    """
    Load a YAML file, save the output of yaml.load(open(file_path,'r')) 
    """

    def __init__(self):
        super(LoadYAML, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to YAML-formatted data file'
        self.output_doc['yaml_output'] = 'the result of yaml.load(file_path)' 

    def run(self):
        p = self.inputs['file_path']
        f = open(p,'r')
        ds = yaml.load(f)
        f.close()
        self.outputs['yaml_output'] = ds 


