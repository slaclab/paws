import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

class LoadSKLearnClassifier(Operation):
    """
    Read a file and use it to build a sklearn classifier. 
    """

    def __init__(self):
        input_names = ['file_path']
        output_names = ['classifier']
        super(LoadSKLearnClassifier, self).__init__(input_names, output_names)
        self.input_doc['file_path'] = 'path to a file (yaml?) containing the data needed to build the classifier'
        self.output_doc['classifier'] = 'a sklearn classifier built from the data in the input file' 

    def run(self):
        p = self.inputs['file_path']
        f = open(p,'r')
        #ds = yaml.load(f)
        # (1) Load the data from the file
        f.close()
        
        # (2) Use the data to build a classifier

        # (3) save the classifier object as output
        #self.outputs['classifier'] =  


