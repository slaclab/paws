from collections import OrderedDict

import numpy as np

import yaml
from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(
    file_path=None,
    data=None)
outputs=OrderedDict(
    yaml_output=None)

class SaveYAML(Operation):
    """Save some data to a YAML file."""

    def __init__(self):
        super(SaveYAML, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path where YAML file will be saved'
        self.input_doc['data'] = 'data to save in the YAML file' 

    def run(self):
        p = self.inputs['file_path']
        d = self.inputs['data']

        stream = file(p,'w')
        yaml.dump(d, stream)

        #datastring = yaml.dump(data)
        #self.outputs['data_string'] = datastring[:min([len(datastring),1000])]

