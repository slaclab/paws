from collections import OrderedDict

from xrsdkit.tools.ymltools import load_sys_from_yaml

from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(
    system=None,
    system_dict={}
    )

class LoadXRSDSystem(Operation):
    """Load xrsdkit.system.System object from a YAML file."""

    def __init__(self):
        super(LoadXRSDSystem, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to YAML file'
        self.output_doc['system'] = 'xrsdkit.system.System object'

    def run(self):
        self.message_callback('loading from {}'.format(self.inputs['file_path']))
        sys, sys_dict = load_sys_from_yaml(self.inputs['file_path'])
        self.outputs['system'] = sys
        self.outputs['system_dict'] = sys_dict
        return self.outputs

