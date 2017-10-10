from collections import OrderedDict

import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

class GetSAXSFlags(Operation):
    """
    Operation for retrieving SAXS population flags
    from a set of dicts read in from a previously saved YAML file 
    """

    def __init__(self):
        input_names = ['dicts','dict_key']
        output_names = ['flags']
        super(GetSAXSFlags, self).__init__(input_names, output_names)
        self.input_doc['dicts'] = 'dict of dicts read in from a YAML file where data labels were previously saved'
        self.input_doc['dict_key'] = 'The key to use to extract the flags from the input dicts'
        self.output_doc['flags'] = 'a dict with keys "bad_data", "precursor_scattering", '\
        '"form_factor_scattering", and "diffraction_peaks"' 

    def run(self):
        ds = self.inputs['dicts']
        k = self.inputs['dict_key']
        if ds is None or k is None:
            return
        f = OrderedDict()
        f['bad_data'] = ds['bad_data_flags'][k]
        f['precursor_scattering'] = ds['precursor_flags'][k]
        f['form_factor_scattering'] = ds['form_flags'][k]
        f['diffraction_peaks'] = ds['structure_flags'][k]

        self.outputs['flags'] = f 


