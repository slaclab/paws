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
        input_names = ['profiler_output', 'scalers', 'classifiers']
        output_names = ['population_flags'] # add propability
        super(SpectrumClassifier, self).__init__(input_names, output_names)
        self.input_doc['profiler_output'] = 'Dict of scalar features as produced by PROCESSING.SAXS.SpectrumProfiler.'
        self.input_doc['classifier'] = 'A classification model that has been imported or trained before executing this operation.'
        self.output_doc['population_flags'] = 'Dict of flags indicating the presence of various scattering populations'
        self.input_type['profiler_output'] = opmod.workflow_item

    def run(self):
        x = self.inputs['profiler_output']

        clsfr = self.inputs['classifiers']['model_for_bad_data'] # bad_data
        clsfr2 = self.inputs['classifiers']['model_for_form'] # form
        clsfr3 = self.inputs['classifiers']['model_for_precursor'] # precursor
        clsfr4 = self.inputs['classifiers']['model_for_structure'] # structure

        flags = OrderedDict()
        flags['test'] = True

        ### Classify the spectrum
        # (1) Apply model to input

        # transform the ordered dictionary into an array of features:
        bin_strengths = x['q_bin_strengths']
        del x['q_bin_strengths']

        # should we do it in profile_spectrum()?
        for i in range(100):
            x[str(i)] = bin_strengths[i]

        # features for bad_data, precursor, and structure labels
        features_analytical_and_60 = ['q_Imax', 'Imax_over_Imean', 'Imax_over_Ilowq',
       'Imax_over_Ihighq', 'Imax_sharpness', 'low_q_ratio', 'high_q_ratio',
       'log_fluctuation','0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13',
       '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25',
       '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37',
       '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
       '50', '51', '52', '53', '54', '55', '56', '57', '58', '59' ]

        # features for form label
        features60 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13',
       '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25',
       '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37',
       '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
       '50', '51', '52', '53', '54', '55', '56', '57', '58', '59']

        input_features1 = [] # analytical and 60 bins
        for item in features_analytical_and_60:
            input_features1.append(x[item])

        input_features2 = [] # 60 bins
        for item in features60:
            input_features2.append(x[item])

        bad_data_scaler = self.inputs['scalers']['analitical_features_and_60bins_for_bad_data']
        transformed_input_features = bad_data_scaler.transform([input_features1])

        flags['bad_data'] = clsfr.predict(transformed_input_features)[0] # [0] since we have only one sample

        if flags['bad_data'] == True:
            flags['precursor_scattering'] = False
            flags['form_factor_scattering'] = False
            flags['diffraction_peaks'] = False
        else:
            #form label
            form_scaler = self.inputs['scalers']['scaler_60bins_no_bad_data']
            transformed_input_features = form_scaler.transform([input_features2])
            flags['form_factor_scattering'] = clsfr2.predict(transformed_input_features)[0]

            # precursor label
            precur_struct_scaler = self.inputs['scalers']['scaler_features_analytical_and_60_no_bad_data']
            transformed_input_features = precur_struct_scaler.transform([input_features1])
            flags['precursor_scattering'] = clsfr3.predict(transformed_input_features)[0]

            # structure label
            flags['diffraction_peaks'] = clsfr4.predict(transformed_input_features)[0]

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


