from collections import OrderedDict

import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

inputs = OrderedDict(dicts=None,dict_key=None)
outputs = OrderedDict(flags=None)

class GetSAXSFlags(Operation):
    """
    Operation for retrieving SAXS population flags
    from a set of dicts read in from a previously saved YAML file 
    """

    def __init__(self):
        super(GetSAXSFlags, self).__init__(inputs, outputs)
        self.input_doc['dicts'] = 'dict of dicts read in from a YAML file where data labels were previously saved'
        self.input_doc['dict_key'] = 'The key to use to extract the flags from the input dicts'
        self.output_doc['flags'] = 'a dict with keys "bad_data", "precursor_scattering", '\
        '"form_factor_scattering", and "diffraction_peaks"' 

    def run(self):
        ds = self.inputs['dicts']
        k = self.inputs['dict_key']
        f = OrderedDict()
        f['unidentified'] = int(ds['bad_data_flags'][k])
        f['guinier_porod'] = int(ds['precursor_flags'][k])
        f['spherical_normal'] = int(ds['form_flags'][k])
        f['diffraction_peaks'] = int(ds['structure_flags'][k])
        self.outputs['flags'] = f 

