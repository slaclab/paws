import numpy as np

from ... import Operation as opmod
from ...Operation import Operation

class SpectrumClassifier(Operation):
    """Identifies scatterer populations from features of SAXS spectra."""

    def __init__(self):
        input_names = ['features', 'classifier']
        output_names = ['flags']
        super(SpectrumClassifier, self).__init__(input_names, output_names)
        self.input_doc['features'] = 'Dict of scalar features '\
            'as produced by PROCESSING.SAXS.SpectrumProfiler.'
        self.input_doc['classifier'] = 'A SaxsClassifier object, '\
            'as produced by IO.MODELS.SAXS.LoadSAXSClassifier.'
        self.output_doc['flags'] = 'Dict of boolean flags '\
            'indicating the presence of various scattering populations.'
        self.input_type['features'] = opmod.workflow_item
        self.input_type['classifier'] = opmod.workflow_item

    def run(self):
        x = self.inputs['features']
        c = self.inputs['classifier'] 
        # for py3, the dict.values() has to be cast as a list,
        # then the list has to be cast as a reshaped np.array
        # to be correctly understood by scikit-learn.
        self.outputs['flags'] = c.classify(np.array(list(x.values())).reshape(1,-1))

