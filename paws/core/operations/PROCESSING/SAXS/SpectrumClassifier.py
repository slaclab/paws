import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class SpectrumClassifier(Operation):
    """
    Classifies SAXS spectra.
    """

    def __init__(self):
        input_names = ['features']
        output_names = ['features']
        super(SpectrumClassifier, self).__init__(input_names, output_names)
        self.input_doc['features'] = 'Dict of features as produced by PROCESSING.SAXS.SpectrumProfiler.'
        self.output_doc['features'] = 'Same dict as input but with classification flags.'
        self.input_src['features'] = opmod.wf_input
        self.input_type['features'] = opmod.ref_type

    def run(self):
        f = self.inputs['features']
       
        # classify the spectrum. determine:
        #f['bad_data_flag']
        #f['form_flag']
        #f['structure_flag']
        #f['precursor_flag']
        #(up to 9 classes) 

        # problems for later. determine:
        #f['form_id']
        #f['structure_id']

        self.outputs['features'] = f 


