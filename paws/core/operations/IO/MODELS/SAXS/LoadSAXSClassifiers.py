import numpy as np
import pickle

from .... import Operation as opmod 
from ....Operation import Operation
from ..... import pawstools

class LoadSAXSClassifiers(Operation):
    """
    Read files to load a set of classifiers to be used on 1-d saxs spectra. 
    """

    def __init__(self):
        input_names = ['file_path']
        output_names = ['classifiers']
        super(LoadSAXSClassifiers, self).__init__(input_names, output_names)
        self.input_doc['file_path'] = 'path to a pickle file '\
        'with data defining a set of scalers and classifiers '\
        'designed for 1-d (I(q) versus q) SAXS spectra'
        self.output_doc['classifiers'] = 'a dict of sklearn '\
        'classifiers and scalers designed for 1-d SAXS spectra, '\
        'intended for input to PROCESSING.SAXS.SpectrumClassifier.'
        self.inputs['file_path'] = os.path.join(pawstools.sourcedir,'core','tools','modeling_data','scalers_and_models.pkl')

        print("TEST: in LOadSAXS: init__")

    def run(self):
        print("TEST: in LOadSAXS: 11111111111111")
        #p = self.inputs['file_path']
        #f = open(p,'r')
        #ds = yaml.load(f)
        # (1) Load the data from the file

        #f.close()
        
        # (2) Use the data to build the set of classifiers and scalers
        # classifier_dict = None

        # (2) or load the classifiers and scalers from a file
        #s_and_m_file = open('../../../../..core/tools/modeling_data/scalers_and_models.pickle​','r')
        s_and_m_file = open(self.inputs['file_path'],'r') 
        s_and_m = pickle.load(s_and_m_file)
        scalers_dict = s_and_m['scalers'] # dict of scalers
        classifier_dict = s_and_m['models'] # dict of models


        # (3) save the dict of classifiers and scalers as output
        self.outputs['classifiers'] = classifier_dict
        self.outputs['scalers'] = scalers_dict

        print("TEST: in LOadSAXS: ", classifier_dict)

        #self.inputs['classifiers'] = classifier_dict
        #self.inputs['scalers'] = scalers_dict

