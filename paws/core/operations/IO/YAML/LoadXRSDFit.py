from collections import OrderedDict

from xrsdkit.tools import load_fit

from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(
    populations={},
    fixed_params={},
    param_bounds={},
    param_constraints={},
    report={})

class LoadXRSDFit(Operation):
    """Load xrsdkit fitting data from a YAML file."""

    def __init__(self):
        super(LoadXRSDFit, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to YAML file'
        self.output_doc['populations'] = 'xrsdkit populations'
        self.output_doc['fixed_params'] = 'xrsdkit fixed_params'
        self.output_doc['param_bounds'] = 'xrsdkit param_bounds'
        self.output_doc['param_constraints'] = 'xrsdkit param_constraints'
        self.output_doc['report'] = 'xrsdkit fit report'

    def run(self):
        self.message_callback('loading from {}'.format(self.inputs['file_path']))
        pops,fp,pb,pc,rpt = load_fit(self.inputs['file_path'])
        self.outputs['populations'] = pops
        self.outputs['fixed_params'] = fp
        self.outputs['param_bounds'] = pb
        self.outputs['param_constraints'] = pc
        self.outputs['report'] = rpt

