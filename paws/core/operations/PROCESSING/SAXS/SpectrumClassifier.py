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
        input_names = ['profiler_output','classifier']
        output_names = ['population_flags']
        super(SpectrumClassifier, self).__init__(input_names, output_names)
        self.input_doc['profiler_output'] = 'Dict of scalar features as produced by PROCESSING.SAXS.SpectrumProfiler.'
        self.input_doc['classifier'] = 'A classification model that has been imported or trained before executing this operation.'
        self.output_doc['population_flags'] = 'Dict of flags indicating the presence of various scattering populations'
        self.input_type['profiler_output'] = opmod.workflow_item

    def run(self):
        x = self.inputs['profiler_output']
        clsfr = self.inputs['classifier']
        flags = OrderedDict()
        flags['test'] = True

        ### Classify the spectrum
        # (1) Apply model to input
        # (2) Interpret model to fill in the following:
        #   flags['bad_data']                  - formerly 'bad_data_flag'
        #   flags['precursor_scattering']      - formerly 'precursor_flag'
        #   flags['form_factor_scattering']    - formerly 'form_flag'
        #   flags['diffraction_peaks']         - formerly 'structure_flag'

        # problems for later:
        # if flags['form_factor_scattering']:
        #     # classify the form factor based on inputs  
        #     flags['form_factor_id'] = ''     
        #
        # if flags['diffraction_peaks']:
        #     # classify the space group based on inputs
        #     flags['space_group_id'] = ''
        #

        self.outputs['population_flags'] = flags 


