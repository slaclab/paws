"""
Calibrate and reduce an image, given calibration parameters.

This module calls on PyFAI.AzimuthalIntegrator 
to calibrate an input image to I(q,chi),
and then reduce it to I(q).
"""

import numpy as np
import pyFAI

from ...operation import Operation
from ... import optools

class CalReduce(Operation):
    """
    Input image data (ndarray) and a dict of calibration parameters  
    Output q, I(q) 
    """
    def __init__(self):
        input_names = ['image_data','cal_params']
        output_names = ['q','I_of_q']
        super(CalReduce,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['cal_params'] = str( 'dict of calibration parameters, '
        + 'including keys x0_pixel, y0_pixel, d_pixel, pixel_size'
        + 'rotation_rad, tilt_rad, fpolz')
        self.input_src['image_data'] = optools.wf_input
        self.input_src['cal_params'] = optools.wf_input
        self.input_type['image_data'] = optools.ref_type
        self.input_type['cal_params'] = optools.ref_type
        self.output_doc['q'] = 'Scattering vector magnitude q. q units are 1/Angstrom if cal_params are in the expected units.'
        self.output_doc['I_of_q'] = 'Integrated intensity at q'

    def run(self):
        img = self.inputs['image_data']
        # pixel_size is expected to be in microns
        pxsz = self.inputs['cal_params']['pixel_size']
        fpolz = self.inputs['cal_params']['fpolz']
        # lambda is expected to be in Angstroms.
        wl = self.inputs['cal_params']['lambda']
        # convert wl from Angstroms to meters
        wl = wl*1E-10
        # detector distance: from pixels to mm
        d_px = self.inputs['cal_params']['d_pixel']
        d_mm = d_px*pxsz*0.001
        rot = (2*np.pi-self.inputs['cal_params']['rotation_rad'])*360/(2*np.pi)
        tilt = self.inputs['cal_params']['tilt_rad']*360/(2*np.pi)
        x0 = self.inputs['cal_params']['x0_pixel']
        y0 = self.inputs['cal_params']['y0_pixel']
        p = pyFAI.AzimuthalIntegrator(wavelength=wl)
        p.setFit2D(d_mm,x0,y0,tilt,rot,pxsz,pxsz)
        # define detector mask, to screen bad pixels
        # should eventually be read in from dezinger output or something
        # for now just screen negative pixels
        # 1 for masked pixels, and 0 for valid pixels
        s = int(img.shape[0])
        detector_mask = np.ones((s,s))*(img <= 0)
        q, I_of_q = p.integrate1d(img, 1000, mask=detector_mask, polarization_factor=fpolz)
        # convert q from 1/nm to 1/Angstrom
        q = q*0.1
        # save results to self.outputs
        self.outputs['q'] = q
        self.outputs['I_of_q'] = I_of_q 
