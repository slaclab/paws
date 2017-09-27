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
        output_names = ['population_flags']
        super(SpectrumClassifier, self).__init__(input_names, output_names)
        self.input_doc['profiler_output'] = 'Dict of scalar features as produced by PROCESSING.SAXS.SpectrumProfiler.'
        self.input_doc['scalers'] = 'A classification model that has been imported or trained before executing this operation.'
        self.input_doc['classifiers'] = 'A classification model that has been imported or trained before executing this operation.'
        self.output_doc['population_flags'] = 'Dict of flags indicating the presence of various scattering populations'
        self.input_type['profiler_output'] = opmod.workflow_item
        self.input_type['scalers'] = opmod.workflow_item
        self.input_type['classifiers'] = opmod.workflow_item

    def run(self):
        x = self.inputs['profiler_output']
        clsfrs = self.inputs['classifiers'] 
        sclrs = self.inputs['scalers'] 
        if x is None or clsfrs is None or sclrs is None:
            return

        # TODO: use keys: 'bad_data', 'precursor_scattering', 'form_factor_scattering', and 'diffraction_peaks',
        # i.e. same keys as population_flags output dict

        model_bad_data = clsfrs['model_for_bad_data']
        model_form = clsfrs['model_for_form_factor_scattering']
        model_precur = clsfrs['model_for_precursor_scattering']
        model_diff_peaks = clsfrs['model_for_diffraction_peaks']

        scaler_bad_data = sclrs['scaler_for_bad_data']
        scaler_form = sclrs['scaler_for_form_factor_scattering']
        scaler_precur = sclrs['scaler_for_precursor_scattering']
        scaler_diff_peaks = sclrs['scaler_for_diffraction_peaks']

        flags = OrderedDict()
        flags['test'] = True

        ### Classify the spectrum
        # (1) Apply model to input

        # transform the ordered dictionary into an array of features:
        bin_strengths = x['q_bin_strengths']
        del x['q_bin_strengths']

        #edges = x['q_bin_edges']
        del x['q_bin_edges']

        # we can use edges instead to indexes, but it could cause a problem
        # when not all samples have a specific edge
        #for i in range(len(edges)):
        #    x[str(edges[i])] = bin_strengths[i]

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

        transformed_input_features = scaler_bad_data.transform([input_features1])
        bad_data = model_bad_data.predict(transformed_input_features)[0] # [0] since we have only one sample
        if bad_data:
            pr_bad_data = model_bad_data.predict_proba(transformed_input_features)[0, 1]
        else:
            pr_bad_data = model_bad_data.predict_proba(transformed_input_features)[0, 0]

        flags['bad_data'] = (bad_data, pr_bad_data) # label and propability to have this label

        if bad_data == True:
            flags['precursor_scattering'] = (False, None)
            flags['form_factor_scattering'] = (False, None)
            flags['diffraction_peaks'] = (False, None)
        else:
            #form label
            transformed_input_features = scaler_form.transform([input_features2])
            form = model_form.predict(transformed_input_features)[0]
            if form:
                pr_form = model_form.predict_proba(transformed_input_features)[0, 1]
            else:
                pr_form = model_form.predict_proba(transformed_input_features)[0, 0]
            flags['form_factor_scattering'] = (form, pr_form) # label and propability to have this label

            # precursor label
            transformed_input_features = scaler_precur.transform([input_features1])
            prec = model_precur.predict(transformed_input_features)[0]
            if prec:
                pr_prec = model_precur.predict_proba(transformed_input_features)[0, 1]
            else:
                pr_prec = model_precur.predict_proba(transformed_input_features)[0, 0]
            flags['precursor_scattering'] = (prec, pr_prec)

            # difraction peaks label
            transformed_input_features = scaler_diff_peaks.transform([input_features1])
            picks = model_diff_peaks.predict(transformed_input_features)[0]
            if picks:
                pr_picks = model_diff_peaks.predict_proba(transformed_input_features)[0, 1]
            else:
                pr_picks = model_diff_peaks.predict_proba(transformed_input_features)[0, 0]
            flags['diffraction_peaks'] = (picks, pr_picks)

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


