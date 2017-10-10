import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxs


class SpectrumClassifier(Operation):
    """Identifies scatterer populations from SAXS spectra.
    """

    def __init__(self):
        input_names = ['profiler_output', 'saxs_classifier']
        output_names = ['population_flags']
        super(SpectrumClassifier, self).__init__(input_names, output_names)
        self.input_doc['profiler_output'] = 'Dict of scalar features '\
            'as produced by PROCESSING.SAXS.SpectrumProfiler.'
        self.input_doc['saxs_classifier'] = 'A SaxsClassifier object, '\
            'as produced by IO.MODELS.SAXS.LoadSAXSClassifier.'
        self.output_doc['population_flags'] = 'Dict of boolean flags '\
            'indicating the presence of various scattering populations.'
        self.input_type['profiler_output'] = opmod.workflow_item
        self.input_type['saxs_classifier'] = opmod.workflow_item

    def run(self):
        x = self.inputs['profiler_output']
        c = self.inputs['saxs_classifier'] 
        self.outputs['population_flags'] = c.classify(x) 

