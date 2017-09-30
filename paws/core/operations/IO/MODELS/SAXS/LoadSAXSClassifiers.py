import os.path

import numpy as np
import yaml
from sklearn import preprocessing
from sklearn import linear_model

from .... import Operation as opmod 
from ....Operation import Operation
from ..... import pawstools

# this module implicitly uses sklearn.
# import here for insurance. 
import sklearn

class LoadSAXSClassifiers(Operation):
    """
    Read files to load a set of classifiers to be used on 1-d saxs spectra. 
    """

    def __init__(self):
        input_names = ['file_path']
        output_names = ['classifiers','scalers']
        super(LoadSAXSClassifiers, self).__init__(input_names, output_names)
        self.input_doc['file_path'] = 'path to a pickle file '\
        'with data defining a set of scalers and classifiers '\
        'designed for 1-d (I(q) versus q) SAXS spectra'
        self.output_doc['classifiers'] = 'a dict of sklearn '\
        'classifiers and scalers designed for 1-d SAXS spectra, '\
        'intended for input to PROCESSING.SAXS.SpectrumClassifier.'
        self.output_doc['scalers'] = 'a dict of sklearn '\
        'classifiers and scalers designed for 1-d SAXS spectra, '\
        'intended for input to PROCESSING.SAXS.SpectrumClassifier.'

        self.inputs['file_path'] = os.path.join(pawstools.sourcedir,
        'core','tools','modeling_data','scalers_and_models.yml')

    # helper function - to set parametrs for scalers and models
    def set_param(self, m_s, param):
        for k, v in param.items():
            if isinstance(v, list):
                setattr(m_s, k, np.array(v))
            else:
                setattr(m_s, k, v)

    def run(self):
        p = self.inputs['file_path']

        # load the classifiers and scalers from a file
        s_and_m_file = open(p,'rb')
        s_and_m = yaml.load(s_and_m_file)

        scalers_dict = s_and_m['scalers'] # dict of scalers parametrs
        classifier_dict = s_and_m['models'] # dict of models parametrs

        model_param_bad_data = classifier_dict['model_for_bad_data']
        model_param_form = classifier_dict['model_for_form_factor_scattering']
        model_param_precur = classifier_dict['model_for_precursor_scattering']
        model_param_diff_peaks = classifier_dict['model_for_diffraction_peaks']

        scaler_param_bad_data = scalers_dict['scaler_for_bad_data']
        scaler_param_form = scalers_dict['scaler_for_form_factor_scattering']
        scaler_param_precur = scalers_dict['scaler_for_precursor_scattering']
        scaler_param_diff_peaks = scalers_dict['scaler_for_diffraction_peaks']

        # recreate the scalers
        scaler_bad_data = preprocessing.StandardScaler()
        self.set_param( scaler_bad_data, scaler_param_bad_data)

        scaler_form = preprocessing.StandardScaler()
        self.set_param( scaler_form, scaler_param_form)

        scaler_precur = preprocessing.StandardScaler()
        self.set_param( scaler_precur, scaler_param_precur)

        scaler_diff_peaks = preprocessing.StandardScaler()
        self.set_param( scaler_diff_peaks, scaler_param_diff_peaks)

        # recreate the models
        model_bad_data = linear_model.SGDClassifier()
        self.set_param( model_bad_data, model_param_bad_data)

        model_form = linear_model.SGDClassifier()
        self.set_param( model_form, model_param_form)

        model_precur = linear_model.SGDClassifier()
        self.set_param( model_precur, model_param_precur)

        model_diff_peaks = linear_model.SGDClassifier()
        self.set_param( model_diff_peaks, model_param_diff_peaks)

        # save the dicts of classifiers and scalers as outputs
        self.outputs['classifiers'] = {'model_for_bad_data': model_bad_data,
                                       'model_for_form_factor_scattering': model_form,
                                       'model_for_precursor_scattering': model_precur,
                                       'model_for_diffraction_peaks': model_diff_peaks}
        self.outputs['scalers'] = {'scaler_for_bad_data': scaler_bad_data,
                                       'scaler_for_form_factor_scattering': scaler_form,
                                       'scaler_for_precursor_scattering': scaler_precur,
                                       'scaler_for_diffraction_peaks': scaler_diff_peaks}


