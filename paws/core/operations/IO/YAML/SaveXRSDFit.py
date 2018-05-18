from collections import OrderedDict

from xrsdkit.tools import save_fit

from ...Operation import Operation

inputs=OrderedDict(
    file_path=None,
    populations={},
    fixed_params={},
    param_bounds={},
    param_constraints={},
    report={})
outputs=OrderedDict()

class SaveXRSDFit(Operation):
    """Save xrsdkit fitting data to a YAML file."""

    def __init__(self):
        super(SaveXRSDFit, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path where YAML file will be saved'
        self.input_doc['populations'] = 'xrsdkit populations'
        self.input_doc['fixed_params'] = 'xrsdkit fixed_params'
        self.input_doc['param_bounds'] = 'xrsdkit param_bounds'
        self.input_doc['param_constraints'] = 'xrsdkit param_constraints'
        self.input_doc['report'] = 'xrsdkit fit report'

    def run(self):
        save_fit(self.inputs['file_path'],
            self.inputs['populations'],
            self.inputs['fixed_params'],
            self.inputs['param_bounds'],
            self.inputs['param_constraints'],
            self.inputs['report'])

