from collections import OrderedDict

import os.path

from ...Operation import Operation

inputs=OrderedDict(
    root_dir_path=None,
    new_dir_name=None)
outputs=OrderedDict(
    new_dir_path=None)

class MakeDirectory(Operation):
    """Create a new directory on the local filesystem"""

    def __init__(self):
        super(MakeDirectory, self).__init__(inputs, outputs)
        self.input_doc['root_dir_path'] = 'filesystem path where the new directory will be rooted'
        self.input_doc['new_dir_name'] = 'name of the new directory'
        self.output_doc['new_dir_path'] = 'path to new directory' 

    def run(self):
        rp = str(self.inputs['root_dir_path'])
        dn = str(self.inputs['new_dir_name'])
        ndp = os.path.join(rp,dn)
        if not os.path.exists(ndp):
            os.mkdir(ndp)        
        self.outputs['new_dir_path'] = ndp

