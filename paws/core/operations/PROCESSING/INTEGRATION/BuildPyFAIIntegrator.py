import numpy as np
from collections import OrderedDict

import pyFAI

from ... import Operation as opmod 
from ...Operation import Operation

inputs = OrderedDict(poni_dict=None) 
outputs = OrderedDict(integrator=None) 

class BuildPyFAIIntegrator(Operation):
    """Produce a PyFAI.AzimuthalIntegrator from a dict of PONI parameters.

    Input PONI dict should be similar 
    to the output of PyFAI.AzimuthalIntegrator.getPyFAI()
    """
    def __init__(self):
        super(BuildPyFAIIntegrator,self).__init__(inputs,outputs)
        self.input_doc['poni_dict'] = str( 'dict of calibration parameters; '
        + 'minimally including keys dist, poni1, poni2, rot1, rot2, rot3, pixel1, pixel2, wavelength;'
        + 'optionally including keys fpolz, detector, splineFile; '
        + 'same specifications as pyFAI .poni format calibration parameters')
        self.input_datatype['poni_dict'] = 'dict'
        self.output_doc['integrator'] = 'PyFAI.AzimuthalIntegrator object set up with input poni_dict'

    def run(self):
        pd = self.inputs['poni_dict']
        p = pyFAI.AzimuthalIntegrator()
        p.setPyFAI(**pd)
        self.outputs['integrator'] = p

