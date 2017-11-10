from collections import OrderedDict
import os.path

import numpy as np
import yaml
from sklearn import preprocessing
from sklearn import linear_model

from .... import Operation as opmod 
from ....Operation import Operation
from ..... import pawstools
from saxskit.saxs_classify import SaxsClassifier

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(saxs_classifier=None)

class LoadSAXSClassifier(Operation):
    """
    Read files to load a set of classifiers to be used on 1-d saxs spectra. 
    """

    def __init__(self):
        super(LoadSAXSClassifier, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to a pickle file '\
            'with data defining a set of scalers and classifiers '\
            'designed for 1-d (I(q) versus q) SAXS spectra. '\
            'If left blank, the default SAXS classifiers will be loaded.'
        self.output_doc['saxs_classifier'] = 'an object containing '\
            'scikit-learn classification models '\
            'designed for 1-d SAXS spectra.'

    def run(self):
        p = self.inputs['file_path']
        self.outputs['saxs_classifier'] = SaxsClassifier(p)

