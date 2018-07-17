from collections import OrderedDict

import yaml
from ...Operation import Operation

inputs=OrderedDict(
    file_path=None,
    data={},
    append=False)
outputs=OrderedDict()

class SaveYAML(Operation):
    """Save some data to a YAML file."""

    def __init__(self):
        super(SaveYAML, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path where YAML file will be saved'
        self.input_doc['data'] = 'data to save in the YAML file' 
        self.input_doc['append'] = 'boolean: whether or not to append to existing file' 

    def run(self):
        p = self.inputs['file_path']
        d = self.inputs['data']
        app_flag = self.inputs['append']
        if app_flag:
            stream = open(p,'a')
        else:
            stream = open(p,'w')
        yaml.dump(d, stream)

