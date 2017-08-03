"""
Calibrate and reduce an image, 
using a PyFAI.AzimuthalIntegrator, a mask, 
and a cut/sector/ROI mask.

This module calls on PyFAI.AzimuthalIntegrator 
to calibrate and integrate (reduce) an image to I(q) vs q.
"""

import numpy as np
import pyFAI

from ... import Operation as opmod 
from ...Operation import Operation

class PyFAIIntegrate1d(Operation):
    """
    Input image data (ndarray), PyFAI.AzimuthalIntegrator, 
    mask, ROI mask, dark field image, flat field image,
    q-range, chi-range, number of points for integration bin centers,
    polz factor, choice of units (string), 
    and choice of integration method (string).
 
    Output arrays containing q and I(q) 
    """
    def __init__(self):
        input_names = list(['image_data','integrator','mask','ROI_mask','dark_image','flat_image',
        'q_range','chi_range','n_points','polz_factor','units','method','integration_mode'])
        output_names = ['q','I','q_I']
        super(PyFAIIntegrate1d,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['integrator'] = 'A PyFAI.AzimuthalIntegrator object'
        self.input_doc['mask'] = '2d array for image mask, same shape as image_data'
        self.input_doc['ROI_mask'] = '2d array for ROI mask, same shape as image_data'
        self.input_doc['dark_image'] = '2d array for dark field, same shape as image_data'
        self.input_doc['flat_image'] = '2d array for flat field, same shape as image_data'
        self.input_doc['q_range'] = 'list with two values, lower and upper limits of q (scattering vector)'
        self.input_doc['chi_range'] = 'list with two values, lower and upper limits of chi (azimuthal angle)'
        self.input_doc['n_points'] = 'number of q-points to integrate, as evenly spaced bins between q_range[0] and q_range[1]'
        self.input_doc['polz_factor'] = 'polarization factor, if polarization correction is needed'
        self.input_doc['units'] = 'choice of units. See PyFAI documentation for options.' 
        self.input_doc['method'] = 'choice of integration method. See PyFAI documentation for options.' 
        self.input_doc['method'] = 'choice of integration method. See PyFAI documentation for options.' 

        self.input_src['image_data'] = opmod.wf_input
        self.input_src['integrator'] = opmod.wf_input
        self.input_src['mask'] = opmod.wf_input
        self.input_src['ROI_mask'] = opmod.wf_input
        self.input_src['dark_image'] = opmod.wf_input
        self.input_src['flat_image'] = opmod.wf_input
        self.input_src['q_range'] = opmod.text_input
        self.input_src['chi_range'] = opmod.text_input
        self.input_src['n_points'] = opmod.text_input
        self.input_src['polz_factor'] = opmod.text_input
        self.input_src['units'] = opmod.text_input
        self.input_src['method'] = opmod.text_input
        self.input_type['image_data'] = opmod.ref_type
        self.input_type['integrator'] = opmod.ref_type
        self.input_type['mask'] = opmod.ref_type
        self.input_type['ROI_mask'] = opmod.ref_type
        self.input_type['dark_image'] = opmod.ref_type
        self.input_type['flat_image'] = opmod.ref_type
        self.input_type['q_range'] = opmod.float_type
        self.input_type['chi_range'] = opmod.float_type
        self.input_type['n_points'] = opmod.int_type
        self.input_type['polz_factor'] = opmod.float_type
        self.input_type['units'] = opmod.str_type
        self.input_type['method'] = opmod.str_type
        self.inputs['mask'] = None 
        self.inputs['ROI_mask'] = None 
        self.inputs['dark_image'] = None 
        self.inputs['flat_image'] = None 
        self.inputs['q_range'] = None 
        self.inputs['chi_range'] = None  
        self.inputs['n_points'] = 1000 
        self.inputs['polz_factor'] = 1. 
        self.inputs['units'] = 'q_A^-1' 
        self.inputs['method'] = None 

        self.output_doc['q'] = 'Scattering vector magnitude q in 1/Angstrom.'
        self.output_doc['I'] = 'Integrated intensity at q.'
        self.output_doc['q_I'] = 'q and I zipped together an a n-by-2 numpy array.'

    def run(self):
        img = self.inputs['image_data']
        pfint = self.inputs['integrator']
        fpolz = self.inputs['polz_factor']
        msk = self.inputs['mask']
        # use a mask to screen negative pixels
        # mask should be 1 for masked pixels, 0 for unmasked pixels
        integ_result = p.integrate1d(img, 1000, radial_range=(0.0005,1.0005), mask=msk, polarization_factor=fpolz, unit='q_A^-1')
        # save results to self.outputs
        q = integ_result. 
        I = integ_result. 
        self.outputs['q'] = q 
        self.outputs['I'] = I
        self.outputs['q_I'] = zip(q,I) 

