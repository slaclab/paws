import os

import numpy as np
import pyFAI

from ... import Operation as op
from ...Operation import Operation

class NikaToPONI(Operation):
    """
    Converts Nika calibration output 
    (saved in a text file)
    to a dict of PyFAI PONI parameters,
    by first converting from Nika to Fit2D,
    then using a pyFAI.AzimuthalIntegrator 
    to convert from Fit2D to PONI format.

    WARNING: the map from Nika's horizontal and vertical tilts
    to Fit2D's tilt and tiltPlanRotation
    has not yet been verified by the developers. 
    Use this operation with nonzero tilts at your own risk.
 
    Input a text file expressing results of Nika automated calibration,
    and manually input polarization factor. 
    Output a dict of pyFAI PONI calibration parameters.
    Format of text file for Nika output is expected to be:
    sample_to_CCD_mm=____
    pixel_size_x_mm=____
    pixel_size_y_mm=____
    beam_center_x_pix=____
    beam_center_y_pix=____
    horizontal_tilt_deg=____
    vertical_tilt_deg=____ 
    wavelength_A=____ 
    """
    
    def __init__(self):
        input_names = ['nika_file','fpolz']
        output_names = ['poni_dict']
        super(NikaToPONI,self).__init__(input_names,output_names)
        self.input_doc['nika_file'] = str('text file expressing nika automated calibration results- '
        + 'see Operation documentation for the expected format of this file')
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_src['nika_file'] = op.fs_input
        self.input_src['fpolz'] = op.text_input
        self.input_type['nika_file'] = op.path_type
        self.input_type['fpolz'] = op.float_type
        self.inputs['fpolz'] = 0.95 
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters, as found in a .poni file'

    def run(self):
        fpath = self.inputs['nika_file']
        fpolz = self.inputs['fpolz']
        for line in open(fpath,'r'):
            kv = line.strip().split('=')
            if kv[0] == 'sample_to_CCD_mm':
                d_mm = float(kv[1])         # Nika reports direct detector distance, 
                                            # from sample to where beam axis intersects detector plane, in mm.
            if kv[0] == 'pixel_size_x_mm':
                pxsz_x_mm = float(kv[1])    # Nika uses pixel dimensions in mm- this is the 'horzontal' dimension. 
            if kv[0] == 'pixel_size_y_mm':
                pxsz_y_mm = float(kv[1])    # Nika uses pixel dimensions in mm- this is the 'vertical' dimension. 
            if kv[0] == 'beam_center_x_pix':
                bcx_px = float(kv[1])       # Nika reports the x coord relative to 'bottom left' corner of detector
                                            # where beam axis intersects detector plane, in pixels 
            if kv[0] == 'beam_center_y_pix':
                bcy_px = float(kv[1])       # same as beam_center_x_pix but for y 
            if kv[0] == 'horizontal_tilt_deg':    
                htilt_deg = float(kv[1])    # Nika reports the horizontal tilt in degrees...
            if kv[0] == 'vertical_tilt_deg':
                vtilt_deg = float(kv[1])    # Nika reports the vertical tilt in degrees...
            if kv[0] == 'wavelength_A':
                wl_A = float(kv[1])         # Nika reports wavelength is in Angstroms
        # get wavelength in m 
        wl_m = wl_A*1E-10
        pxsz_x_um = pxsz_x_mm * 1000
        pxsz_y_um = pxsz_y_mm * 1000
        # TODO: figure out how Fit2D angles correspond to Nika angles:
        # cannot use this for tilted geometries until this is done.
        tilt_deg = 0
        rot_fit2d = 0
        # use a pyFAI.AzimuthalIntegrator() to do the conversion
        p = pyFAI.AzimuthalIntegrator(wavelength = wl_m) 
        p.setFit2D(d_mm,bcx_px,bcy_px,tilt_deg,rot_fit2d,pxsz_x_um,pxsz_y_um)
        poni_dict = p.getPyFAI()
        poni_dict['fpolz'] = fpolz
        self.outputs['poni_dict'] = poni_dict 

