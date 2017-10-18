"""
Integrate an image,
using an existing PyFAI.AzimuthalIntegrator,
with a bunch of input parameters
for calling AzimuthalIntegrator.integrate1d().
"""

import numpy as np
import pyFAI

from ... import Operation as opmod 
from ...Operation import Operation

class ApplyIntegrator1d(Operation):
    """
    Input image data (ndarray), PyFAI.AzimuthalIntegrator, 
    mask, ROI mask, dark field image, flat field image,
    q-range, chi-range, number of points for integration bin centers,
    polz factor, choice of unit (string), 
    and choice of integration method (string).

    Refer to the PyFAI documentation at ..... 
    for parameter definitions and defaults.
    TODO: fill in web uri above. 

    Output arrays containing q and I(q) 
    """
    def __init__(self):
        input_names = ['image_data','integrator','mask','ROI_mask','dark','flat',\
        'radial_range','azimuth_range','npt','polarization_factor','unit','method','integration_mode']
        output_names = ['q','I','q_I']
        super(ApplyIntegrator1d,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['integrator'] = 'A PyFAI.AzimuthalIntegrator object'
        self.input_doc['mask'] = '2d array for image mask, same shape as image_data'
        self.input_doc['ROI_mask'] = '2d array for ROI mask, same shape as image_data'
        self.input_doc['dark'] = '2d array for dark field, same shape as image_data'
        self.input_doc['flat'] = '2d array for flat field, same shape as image_data'
        self.input_doc['radial_range'] = 'list with two values, lower and upper limits of q (scattering vector)'
        self.input_doc['azimuth_range'] = 'list with two values, lower and upper limits of chi (azimuthal angle)'
        self.input_doc['npt'] = 'number of q-points to integrate, as evenly spaced bins between radial_range[0] and radial_range[1]'
        self.input_doc['polarization_factor'] = 'polarization factor, if polarization correction is needed'
        self.input_doc['unit'] = 'choice of unit. See PyFAI documentation for options.' 
        self.input_doc['method'] = 'choice of integration method. See PyFAI documentation for options.' 
        self.input_doc['integration_mode'] = 'not yet implemented' 

        self.input_type['image_data'] = opmod.workflow_item
        self.input_type['integrator'] = opmod.workflow_item

        self.inputs['npt'] = 1000
        self.inputs['polarization_factor'] = 1.
        self.inputs['unit'] = 'q_A^-1'

        self.output_doc['q'] = 'Scattering vector magnitude q in 1/Angstrom.'
        self.output_doc['I'] = 'Integrated intensity at q.'
        self.output_doc['q_I'] = 'q and I zipped together an a n-by-2 numpy array.'

    def run(self):
        img = self.inputs['image_data']
        intgtr = self.inputs['integrator']
        m = None
        if self.inputs['mask'] is not None and self.inputs['ROI_mask'] is not None: 
            m = self.inputs['mask'] | self.inputs['ROI_mask']
        elif self.inputs['mask'] is not None:
            m = self.inputs['mask']
        elif self.inputs['ROI_mask'] is not None:
            m = self.inputs['ROI_mask']
        self.inputs['mask'] = m
        #if self.inputs['ROI_mask']: self.inputs['mask'] = self.inputs['mask'] | self.inputs['ROI_mask']
        kwargexcludemask = [k for k in self.inputs.keys() if self.inputs[k] is None]
        kwargexcludemask = kwargexcludemask + ['image_data','ROI_mask','integrator','integration_mode']
        kwargs = {key:val for key,val in self.inputs.items() if key not in kwargexcludemask}

        q,I = intgtr.integrate1d(img,**kwargs)
        #integ_result = intgtr.integrate1d(**kwargs)
        # save results to self.outputs
        #q = integ_result.radial
        #I = integ_result.intensity

        self.outputs['q'] = q 
        self.outputs['I'] = I
        self.outputs['q_I'] = np.array([q,I]).T

