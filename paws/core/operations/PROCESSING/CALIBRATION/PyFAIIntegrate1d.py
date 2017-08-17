"""
Integrate and reduce an image,
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
        'q_range','chi_range','npts','polarization_factor','units','method','integration_mode'])
        output_names = ['q','I','q_I']
        super(PyFAIIntegrate1d,self).__init__(input_names,output_names)
        self.input_doc['data'] = '2d array representing intensity for each pixel'
        self.input_doc['integrator'] = 'A PyFAI.AzimuthalIntegrator object'
        self.input_doc['mask'] = '2d array for image mask, same shape as image_data'
        self.input_doc['ROI_mask'] = '2d array for ROI mask, same shape as image_data'
        self.input_doc['dark_image'] = '2d array for dark field, same shape as image_data'
        self.input_doc['flat_image'] = '2d array for flat field, same shape as image_data'
        self.input_doc['q_range'] = 'list with two values, lower and upper limits of q (scattering vector)'
        self.input_doc['chi_range'] = 'list with two values, lower and upper limits of chi (azimuthal angle)'
        self.input_doc['npts'] = 'number of q-points to integrate, as evenly spaced bins between q_range[0] and q_range[1]'
        self.input_doc['polarization_factor'] = 'polarization factor, if polarization correction is needed'
        self.input_doc['units'] = 'choice of units. See PyFAI documentation for options.' 
        self.input_doc['method'] = 'choice of integration method. See PyFAI documentation for options.' 
        self.input_doc['method'] = 'choice of integration method. See PyFAI documentation for options.' 

        self.input_type['image_data'] = opmod.workflow_item
        self.input_type['integrator'] = opmod.workflow_item
        self.input_type['mask'] = opmod.workflow_item
        self.input_type['ROI_mask'] = opmod.workflow_item
        self.input_type['dark_image'] = opmod.workflow_item
        self.input_type['flat_image'] = opmod.workflow_item
        self.input_type['q_range'] = opmod.float_type
        self.input_type['chi_range'] = opmod.float_type
        self.input_type['npts'] = opmod.integer_type
        self.input_type['polarization_factor'] = opmod.float_type
        self.input_type['units'] = opmod.string_type
        self.input_type['method'] = opmod.string_type

        self.inputs['mask'] = None 
        self.inputs['ROI_mask'] = None 
        self.inputs['dark_image'] = None 
        self.inputs['flat_image'] = None 
        self.inputs['q_range'] = None 
        self.inputs['chi_range'] = None  
        self.inputs['npts'] = 1000
        self.inputs['polarization_factor'] = 1.
        self.inputs['units'] = 'q_A^-1' 
        self.inputs['method'] = None 

        self.output_doc['q'] = 'Scattering vector magnitude q in 1/Angstrom.'
        self.output_doc['I'] = 'Integrated intensity at q.'
        self.output_doc['q_I'] = 'q and I zipped together an a n-by-2 numpy array.'

    def run(self):
        if self.inputs['ROI_mask']: self.inputs['mask'] = self.inputs['mask'] | self.inputs['ROI_mask']
        # use a mask to screen negative pixels
        # mask should be 1 for masked pixels, 0 for unmasked pixels
        kwargexcludemask = ['ROI_mask','integrator']
        kwargs = {item for item in self.inputs.iteritems() if item[0] not in kwargexcludemask}

        integ_result = self.inputs['integrator'].integrate1d(**kwargs)
        # save results to self.outputs
        q = integ_result.radial
        I = integ_result.intensity
        self.outputs['q'] = q 
        self.outputs['I'] = I
        self.outputs['q_I'] = zip(q,I) 

