from collections import OrderedDict

from xrsdkit.system import save_to_yaml

from ...Operation import Operation

inputs=OrderedDict(
    file_path=None,
    system={}
    )
outputs=OrderedDict()

class SaveXRSDSystem(Operation):
    """Save xrsdkit.system.System object to a YAML file."""

    def __init__(self):
        super(SaveXRSDSystem, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path where YAML file will be saved'
        self.input_doc['system'] = 'xrsdkit.system.System object'

    def run(self):
        self.message_callback('writing to {}'.format(self.inputs['file_path']))
        save_to_yaml(self.inputs['file_path'],self.inputs['system'])

