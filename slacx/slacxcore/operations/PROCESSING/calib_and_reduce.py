"""
Operations for remeshing and and reducing an image
contributors: fangren, apf, lensonp
Last updated 2016/12/05 by lensonp
"""
import os

import numpy as np
import pyFAI

from ..slacxop import Operation
from .. import optools

class ReduceByWXDDict(Operation):
    """
    Input image data (ndarray) and a dict of calibration parameters from a WxDiff .calib file 
    Return q, I(q) 
    """
    def __init__(self):
        input_names = ['image_data','wxd_dict','pixel_size','fpolz']
        output_names = ['q','I_of_q']
        super(ReduceByWXDDict,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['wxd_dict'] = str( 'dict of calibration parameters read in from a .calib file,'
        + ' with keys d_pixel, rotation_rad, tilt_rad, lambda, x0_pixel, y0_pixel,'
        + ' PP (polarization factor), pixel_size, and d_pixel')
        self.input_doc['pixel_size'] = 'pixel size in microns'
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_doc['gain'] = 'detector gain'
        self.input_doc['readnoise'] = 'detector readnoise'
        self.input_doc['mask'] = str('Bad pixel locations, if known (e.g., inactive detector regions, dead pixels,'
                                     + ' zingers/cosmic rays).  Boolean array of same shape as image or None.')
        self.input_src['pixel_size'] = optools.user_input
        self.input_src['fpolz'] = optools.user_input
        self.input_src['gain'] = optools.user_input
        self.input_src['readnoise'] = optools.user_input
        self.input_src['mask'] = optools.user_input
        self.input_type['pixel_size'] = optools.float_type
        self.input_type['fpolz'] = optools.float_type
        self.inputs['pixel_size'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.inputs['gain'] = 1.0
        self.inputs['readnoise'] = 1.0
        self.inputs['mask'] = None
        self.output_doc['q'] = 'Scattering vector magnitude q'
        self.output_doc['I_of_q'] = 'Integrated intensity at q'
        self.output_doc['dI_of_q'] = 'Error estimate of integrated intensity at q'
        self.input_src['image_data'] = optools.wf_input
        self.input_src['wxd_dict'] = optools.wf_input
        self.categories = ['PROCESSING']

    def run(self):
        img = self.inputs['image_data']
        pxsz = self.inputs['pixel_size']
        fpolz = self.inputs['fpolz']
        l = self.inputs['wxd_dict']['lambda']
        d = self.inputs['wxd_dict']['d_pixel']*pxsz*0.001
        rot = (2*np.pi-self.inputs['wxd_dict']['rotation_rad'])/(2*np.pi)*360
        tilt = self.inputs['wxd_dict']['tilt_rad']/(2*np.pi)*360
        # initialization parameters, change into Fit2D format
        x0 = self.inputs['wxd_dict']['x0_pixel']
        y0 = self.inputs['wxd_dict']['y0_pixel']
        # PyFAI magic go!
        p = pyFAI.AzimuthalIntegrator(wavelength=l)
        p.setFit2D(d,x0,y0,tilt,rot,pxsz,pxsz)
        # define detector mask, to screen bad pixels
        # should eventually be read in from dezinger output or something
        # for now just screen negative pixels
        # 1 for masked pixels, and 0 for valid pixels
        if self.inputs['mask'] is None:
            detector_mask = np.ones(img.shape)*(img <= 0)
        else:
            detector_mask = self.inputs['mask']
        q, I_of_q = p.integrate1d(img, 1000, mask=detector_mask, polarization_factor=fpolz)
        q = q * 1E9
        # save results to self.outputs
        self.outputs['q'] = q
        self.outputs['I_of_q'] = I_of_q
        self.outputs['dI_of_q'] = None # placeholder

