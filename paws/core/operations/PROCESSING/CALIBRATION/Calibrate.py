"""
Calibrate and reduce an image, given calibration parameters.

This module calls on PyFAI.AzimuthalIntegrator 
to calibrate an input image to I(q,chi).
"""

import numpy as np
import pyFAI

from ...operation import Operation
from ... import optools


class Calibrate(Operation):
    """
    Input image data (ndarray) and a dict of calibration parameters 
    Return q, chi, I(q,chi) 
    """
    def __init__(self):
        input_names = ['image_data','cal_params']
        output_names = ['q','chi','I_q_chi','I_q']
        super(Calibrate,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['cal_params'] = str( 'dict of calibration parameters, '
        + 'including keys x0_pixel, y0_pixel, d_pixel, pixel_size'
        + 'rotation_rad, tilt_rad, fpolz')
        self.input_src['image_data'] = optools.wf_input
        self.input_src['cal_params'] = optools.wf_input
        self.input_type['image_data'] = optools.ref_type
        self.input_type['cal_params'] = optools.ref_type
        self.inputs['pixel_size'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.output_doc['q'] = 'Scattering vector magnitude'
        self.output_doc['chi'] = 'Azimuthal angle in degrees'     
        self.output_doc['I_q_chi'] = 'Integrated intensity at q, chi'
        self.output_doc['I_q'] = 'Chi-integrated intensity at q'

    def run(self):
        img = self.inputs['image_data']
        pxsz = self.inputs['cal_params']['pixel_size']
        fpolz = self.inputs['cal_params']['fpolz']
        wl = self.inputs['cal_params']['lambda']
        d = self.inputs['cal_params']['d_pixel']*pxsz*0.001
        rot = (2*np.pi-self.inputs['cal_params']['rotation_rad'])/(2*np.pi)*360
        tilt = self.inputs['cal_params']['tilt_rad']/(2*np.pi)*360
        x0 = self.inputs['cal_params']['x0_pixel']
        y0 = self.inputs['cal_params']['y0_pixel']
        s = int(img.shape[0])
        p = pyFAI.AzimuthalIntegrator(wavelength=wl)
        p.setFit2D(d,x0,y0,tilt,rot,pxsz,pxsz)
        detector_mask = np.ones((s,s))*(img <= 0)
        I_q_chi, q, chi = p.integrate2d(img, 1000, mask=detector_mask, polarization_factor=fpolz)
        q1d, I_q = p.integrate1d(img, 1000, mask=detector_mask, polarization_factor=fpolz)
        q = q * 1E9
        # save results to self.outputs
        self.outputs['q'] = q
        self.outputs['chi'] = chi 
        self.outputs['I_q_chi'] = I_q_chi 
        self.outputs['I_q'] = I_q 


