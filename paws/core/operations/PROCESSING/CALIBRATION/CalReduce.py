"""
Calibrate and reduce an image, given calibration parameters.

This module calls on PyFAI.AzimuthalIntegrator 
to calibrate an input image to I(q,chi),
and then reduce it to I(q).
"""

import numpy as np
import pyFAI

from ... import Operation as op
from ...Operation import Operation

class CalReduce(Operation):
    """
    Input image data (ndarray) and a dict of .poni format calibration parameters
    Output q, I(q) 
    """
    def __init__(self):
        input_names = ['image_data','poni_dict']
        output_names = ['q','I','q_I']
        super(CalReduce,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['poni_dict'] = str( 'dict of calibration parameters; '
        + 'minimally including keys dist, poni1, poni2, rot1, rot2, rot3, pixel1, pixel2, wavelength;'
        + 'optionally including keys fpolz, detector, splineFile; '
        + 'same specifications as pyFAI .poni format calibration parameters')
        self.input_src['image_data'] = op.wf_input
        self.input_src['poni_dict'] = op.wf_input
        self.input_type['image_data'] = op.ref_type
        self.input_type['poni_dict'] = op.ref_type
        self.output_doc['q'] = 'Scattering vector magnitude q in 1/Angstrom.'
        self.output_doc['I'] = 'Integrated intensity at q.'
        self.output_doc['q_I'] = 'q and I zipped together an a n-by-2 numpy array.'

    def run(self):
        img = self.inputs['image_data']
        pd = self.inputs['poni_dict']
        p = pyFAI.AzimuthalIntegrator()
        p.setPyFAI(**pd)
        fpolz = pd['fpolz']
        # use a mask to screen negative pixels
        # mask should be 1 for masked pixels, 0 for unmasked pixels
        msk = np.ones(img.shape)*(img <= 0)
        q, I_of_q = p.integrate1d(img, 1000, radial_range=(0.0005,1.0005), mask=msk, polarization_factor=fpolz, unit='q_A^-1')
        # save results to self.outputs
        self.outputs['q'] = q
        self.outputs['I'] = I_of_q
        self.outputs['q_I'] = np.array([q,I_of_q]).T

