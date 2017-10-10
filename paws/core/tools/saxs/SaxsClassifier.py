"""Class for loading and applying the SAXS classifiers.
"""
import yaml
import sklearn
from sklearn import preprocessing

from ... import pawstools

class SaxsClassifier(object):

    def __init__(self,yml_file=None):
        if yml_file is None:
            p = os.path.abspath(__file__)
            # p = (pawsroot)/paws/core/tools/saxs/SaxsClassifier.py
            d = os.path.dirname(p)
            # d = (pawsroot)/paws/core/tools/saxs/
            yml_file = os.path.join(d,'modeling_data','scalers_and_models.yml')

            s_and_m_file = open(yml_file,'rb')
            s_and_m = yaml.load(s_and_m_file)

            sk_version = s_and_m['version']
            cur_version = map(int,sklearn.__version__.split('.'))

            if (major != sk_version[0] or minor != sk_version[1]):
                version_str = ".".join(map(str,sk_version))
                msg = 'found scikit-learn v{}.{}.x. '\
                    'SAXS classification models were built '\
                    'with scikit-learn v{}. '\
                    'Please try again with a matching version of scikit-learn.'\
                    .format(major,minor,version_str) 
            raise RuntimeError(msg)

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
            self.models = {'bad_data': model_bad_data,
                           'form_factor_scattering': model_form,
                           'precursor_scattering': model_precur,
                           'diffraction_peaks': model_diff_peaks}
            self.scalers = {'bad_data': scaler_bad_data,
                           'form_factor_scattering': scaler_form,
                           'precursor_scattering': scaler_precur,
                           'diffraction_peaks': scaler_diff_peaks}

    # helper function - to set parametrs for scalers and models
    def set_param(self, m_s, param):
        for k, v in param.items():
            if isinstance(v, list):
                setattr(m_s, k, np.array(v))
            else:
                setattr(m_s, k, v)

