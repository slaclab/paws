"""
Produce a PyFAI.AzumthalIntegrator to use for calibrating and integrating images.
"""

import numpy as np
import pyFAI

from ... import Operation as opmod 
from ...Operation import Operation

class BuildPyFAIIntegrator(Operation):
    """
    Input dict of calibration parameters 
    Return AzimuthalIntegrator 
    """
    def __init__(self):
        input_names = ['poni_dict']
        output_names = ['integrator']
        super(BuildPyFAIIntegrator,self).__init__(input_names,output_names)
        self.input_doc['poni_dict'] = str( 'dict of calibration parameters; '
        + 'minimally including keys dist, poni1, poni2, rot1, rot2, rot3, pixel1, pixel2, wavelength;'
        + 'optionally including keys fpolz, detector, splineFile; '
        + 'same specifications as pyFAI .poni format calibration parameters')
        self.input_type['poni_dict'] = opmod.workflow_item
        self.output_doc['integrator'] = 'PyFAI.AzimuthalIntegrator object set up with input poni_dict'

    def run(self):
        pd = self.inputs['poni_dict']
        p = pyFAI.AzimuthalIntegrator()
        if pd is not None:
            p.setPyFAI(**pd)
        self.outputs['integrator'] = p

