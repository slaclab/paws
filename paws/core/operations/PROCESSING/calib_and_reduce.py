"""
Operations for remeshing and and reducing an image

author: Fang Ren, Apurva Mehta, Ron Pandolfi
For details, please refer to the recent paper submitted to ACS Combinatorial Science
F. Ren implemented the remeshing on scripting level, contributed by R. Pandolfi from LBL. F. Ren originally contributed
it to slacx

Please add yours too, Amanda, Lenson.

contributors: fangren, apf, lensonp
"""

import os

import numpy as np
import pyFAI

from ..operation import Operation
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
        self.input_src['image_data'] = optools.wf_input
        self.input_src['wxd_dict'] = optools.wf_input
        self.input_src['pixel_size'] = optools.text_input 
        self.input_src['fpolz'] = optools.text_input
        self.input_type['image_data'] = optools.ref_type
        self.input_type['wxd_dict'] = optools.ref_type
        self.input_type['pixel_size'] = optools.float_type
        self.input_type['fpolz'] = optools.float_type
        self.inputs['pixel_size'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.output_doc['q'] = 'Scattering vector magnitude q'
        self.output_doc['I_of_q'] = 'Integrated intensity at q'

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
        s = int(img.shape[0])
        p = pyFAI.AzimuthalIntegrator(wavelength=l)
        p.setFit2D(d,x0,y0,tilt,rot,pxsz,pxsz)
        # define detector mask, to screen bad pixels
        # should eventually be read in from dezinger output or something
        # for now just screen negative pixels
        # 1 for masked pixels, and 0 for valid pixels
        detector_mask = np.ones((s,s))*(img <= 0)
        q, I_of_q = p.integrate1d(img, 1000, mask=detector_mask, polarization_factor=fpolz)
        q = q * 1E9
        # save results to self.outputs
        self.outputs['q'] = q
        self.outputs['I_of_q'] = I_of_q 


class ReduceByWXDDict_mask_error(Operation):
    """
    Input image data (ndarray) and a dict of calibration parameters from a WxDiff .calib file
    Return q, I(q)
    """
    def __init__(self):
        input_names = ['image_data','wxd_dict','pixel_size','fpolz','calculate_noise','inverse_gain','readnoise','mask']
        output_names = ['q','I_of_q','dI_of_q']
        super(ReduceByWXDDict_mask_error,self).__init__(input_names,output_names)
        # docs
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['wxd_dict'] = str( 'dict of calibration parameters read in from a .calib file,'
        + ' with keys d_pixel, rotation_rad, tilt_rad, lambda, x0_pixel, y0_pixel,'
        + ' PP (polarization factor), pixel_size, and d_pixel')
        self.input_doc['pixel_size'] = 'pixel size in microns'
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_doc['calculate_noise'] = 'Calculate error estimate?'
        self.input_doc['inverse_gain'] = str('inverse gain, i.e. electrons on chip per digital count;'
        + ' applies primarily to CCDs')
        self.input_doc['readnoise'] = 'detector readnoise in electrons; applies primarily to CCDs'
        self.input_doc['mask'] = str('Bad pixel locations, if known (e.g., inactive detector regions, dead pixels,'
        + ' zingers/cosmic rays).  Boolean array of same shape as image, True indicating'
        + ' bad data and False indicating good, or None for default behavior.'
        + ' Default masking behavior is to mask all non-positive pixels.')
        self.output_doc['q'] = 'Scattering vector magnitude q'
        self.output_doc['I_of_q'] = 'Integrated intensity at q'
        self.output_doc['dI_of_q'] = 'Error estimate of integrated intensity at q'
        # src & type
        self.input_src['image_data'] = optools.wf_input
        self.input_src['wxd_dict'] = optools.wf_input
        self.input_src['pixel_size'] = optools.text_input
        self.input_src['fpolz'] = optools.text_input
        self.input_src['calculate_noise'] = optools.text_input
        self.input_src['inverse_gain'] = optools.text_input
        self.input_src['readnoise'] = optools.text_input
        self.input_src['mask'] = optools.text_input
        self.input_type['pixel_size'] = optools.float_type
        self.input_type['fpolz'] = optools.float_type
        self.input_type['calculate_noise'] = optools.bool_type
        self.input_type['inverse_gain'] = optools.float_type
        self.input_type['readnoise'] = optools.float_type
        # defaults
        self.inputs['pixel_size'] = 79.
        self.inputs['fpolz'] = 0.95
        self.inputs['calculate_noise'] = True
        #self.inputs['inverse_gain'] = 21.97 # 1 for no gain, sort of
        self.inputs['inverse_gain'] = 49.44 # 1 for no gain, sort of
        self.inputs['readnoise'] = 9.0 # 0 for no readnoise
        self.inputs['mask'] = None

    def run(self):
        img = self.inputs['image_data']
        # initialization parameters, change into Fit2D format
        pxsz = self.inputs['pixel_size'] # in microns
        fpolz = self.inputs['fpolz']
        l = self.inputs['wxd_dict']['lambda'] # wavelength (in what units??? need to check)
        d = self.inputs['wxd_dict']['d_pixel']*pxsz*0.001 # converting distance from pixel-widths to millimeters
        rot = (2*np.pi-self.inputs['wxd_dict']['rotation_rad'])/(2*np.pi)*360
        tilt = self.inputs['wxd_dict']['tilt_rad']/(2*np.pi)*360
        x0 = self.inputs['wxd_dict']['x0_pixel']
        y0 = self.inputs['wxd_dict']['y0_pixel']
        # PyFAI magic go!
        p = pyFAI.AzimuthalIntegrator(wavelength=l)
        p.setFit2D(d,x0,y0,tilt,rot,pxsz,pxsz)
        # define detector mask, to screen bad pixels
        # 1 for masked pixels, and 0 for valid pixels
        if self.inputs['mask'] is None:
            detector_mask = np.ones(img.shape)*(img <= 0)
        else:
            detector_mask = self.inputs['mask']
        q, I_of_q = p.integrate1d(img, 1000, mask=detector_mask, polarization_factor=fpolz) # 2nd arg number of bins
        q = q * 1E9 
        # noise model
        if bool(self.inputs['calculate_noise']):
            inverse_gain = self.inputs['inverse_gain']
            readnoise = self.inputs['readnoise']
            noise_model_squared = inverse_gain**-2 * (inverse_gain * img + readnoise**2)
            _, dI_squared = p.integrate1d(noise_model_squared, 1000, mask=detector_mask, polarization_factor=fpolz)
            dI_of_q = dI_squared**0.5
        else:
            dI_of_q = None
        # output
        self.outputs['q'] = q
        self.outputs['I_of_q'] = I_of_q
        self.outputs['dI_of_q'] = dI_of_q


class CalByWXDDict(Operation):
    """
    Input image data (ndarray) and a dict of calibration parameters from a WxDiff .calib file 
    Return q, chi, I(q,chi) 
    """
    def __init__(self):
        input_names = ['image_data','wxd_dict','pixel_size','fpolz']
        output_names = ['q','chi','I_q_chi','I_q']
        super(CalByWXDDict,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['wxd_dict'] = str( 'dict of calibration parameters read in from a .calib file,'
        + ' with keys d_pixel, rotation_rad, tilt_rad, lambda, x0_pixel, y0_pixel,'
        + ' PP (polarization factor), pixel_size, and d_pixel')
        self.input_doc['pixel_size'] = 'pixel size in microns'
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_src['image_data'] = optools.wf_input
        self.input_src['wxd_dict'] = optools.wf_input
        self.input_src['pixel_size'] = optools.text_input 
        self.input_src['fpolz'] = optools.text_input
        self.input_type['image_data'] = optools.ref_type
        self.input_type['wxd_dict'] = optools.ref_type
        self.input_type['pixel_size'] = optools.float_type
        self.input_type['fpolz'] = optools.float_type
        self.inputs['pixel_size'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.output_doc['q'] = 'Scattering vector magnitude'
        self.output_doc['chi'] = 'Azimuthal angle in degrees'     
        self.output_doc['I_q_chi'] = 'Integrated intensity at q, chi'
        self.output_doc['I_q'] = 'Integrated intensity at q'

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
        s = int(img.shape[0])
        p = pyFAI.AzimuthalIntegrator(wavelength=l)
        p.setFit2D(d,x0,y0,tilt,rot,pxsz,pxsz)
        # define detector mask, to screen bad pixels
        # should eventually be read in from dezinger output or something
        # for now just screen negative pixels
        # 1 for masked pixels, and 0 for valid pixels
        detector_mask = np.ones((s,s))*(img <= 0)
        I_q_chi, q, chi = p.integrate2d(img, 1000, mask=detector_mask, polarization_factor=fpolz)
        q1d, I_q = p.integrate1d(img, 1000, mask=detector_mask, polarization_factor=fpolz)
        q = q * 1E9
        # save results to self.outputs
        self.outputs['q'] = q
        self.outputs['chi'] = chi 
        self.outputs['I_q_chi'] = I_q_chi 
        self.outputs['I_q'] = I_q 


