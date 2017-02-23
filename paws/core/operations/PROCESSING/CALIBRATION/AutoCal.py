"""
Operation for automatic discovery of diffraction image calibration parameters. 
"""

import os

import numpy as np
import pyFAI

from ...operation import Operation
from ... import optools

class AutoCal(Operation):
    """
    Input image data (ndarray), pixel size, polz factor.
    Output dictionary of calibration parameters. 
    """
    def __init__(self):
        input_names = ['image_data','pixel_size','fpolz']
        output_names = ['cal_params']
        super(AutoCal,self).__init__(input_names,output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['pixel_size'] = 'pixel size in microns'
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_src['image_data'] = optools.wf_input
        self.input_src['pixel_size'] = optools.text_input 
        self.input_src['fpolz'] = optools.text_input
        self.input_type['image_data'] = optools.ref_type
        self.input_type['pixel_size'] = optools.float_type
        self.input_type['fpolz'] = optools.float_type
        self.inputs['pixel_size'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.output_doc['cal_params'] = 'Dictionary of the solved calibration parameters'

    def run(self):
        img = self.inputs['image_data']
        pxsz = self.inputs['pixel_size']
        fpolz = self.inputs['fpolz']
        x0_px = 0
        y0_px = 0
        d_px = 0
        rot_rad = 0
        tilt_rad = 0
        wl = 0
        d = dict({'x0_pixel':x0_px,
            'y0_pixel':y0_px,
            'd_pixel':d_px,
            'pixel_size':pxsz,
            'rotation_rad':rot_rad,
            'tilt_rad':tilt_rad,
            'lambda':wl,
            'PP':fpolz})
        self.outputs['cal_params'] = d


