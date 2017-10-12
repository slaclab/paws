import os.path

import numpy as np
import yaml
from sklearn import preprocessing
from sklearn import linear_model

from .... import Operation as opmod 
from ....Operation import Operation
from ..... import pawstools
from .....tools.saxs.saxs_classify import SaxsClassifier

class LoadSAXSClassifier(Operation):
    """
    Read files to load a set of classifiers to be used on 1-d saxs spectra. 
    """

    def __init__(self):
        input_names = ['file_path']
        output_names = ['saxs_classifier']
        super(LoadSAXSClassifier, self).__init__(input_names, output_names)
        self.input_doc['file_path'] = 'path to a pickle file '\
        'with data defining a set of scalers and classifiers '\
        'designed for 1-d (I(q) versus q) SAXS spectra. '\
        'If left blank, the default SAXS classifiers will be loaded.'
        self.output_doc['saxs_classifier'] = 'an object containing '\
            'scikit-learn classification models '\
            'designed for 1-d SAXS spectra.'
        self.inputs['file_path'] = os.path.join(pawstools.sourcedir,
        'core','tools','saxs','modeling_data','scalers_and_models.yml')

    def run(self):
        p = self.inputs['file_path']
        self.outputs['saxs_classifier'] = SaxsClassifier(p)


