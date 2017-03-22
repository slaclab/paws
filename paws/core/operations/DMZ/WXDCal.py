"""
Operation for getting calibration parameters from WXDIFF .calib output 
"""

import os

import numpy as np
import pyFAI

from ...operation import Operation
from ... import optools

class WXDCal(Operation):
    """
    Input image data (ndarray), pixel size, polz factor.
    Output dictionary of calibration parameters. 
    """
    def __init__(self):
        input_names = ['wxd_file','pixel_size','fpolz']
        output_names = ['cal_params']
        super(WXDCal,self).__init__(input_names,output_names)
        self.input_doc['wxd_file'] = '.calib file produced by WXDIFF calibration'
        self.input_doc['pixel_size'] = 'pixel size in microns'
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_src['wxd_file'] = optools.fs_input
        self.input_src['pixel_size'] = optools.text_input 
        self.input_src['fpolz'] = optools.text_input
        self.input_type['wxd_file'] = optools.path_type
        self.input_type['pixel_size'] = optools.float_type
        self.input_type['fpolz'] = optools.float_type
        self.inputs['pixel_size'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.output_doc['cal_params'] = 'Dictionary of calibration parameters'

    def run(self):
        fpath = self.inputs['wxd_file']
        pxsz = self.inputs['pixel_size']
        fpolz = self.inputs['fpolz']
        for line in open(fpath,'r'):
            kv = line.strip().split('=')
            if kv[0] == 'bcenter_x':
               x0_px = float(kv[1])
            if kv[0] == 'bcenter_y':
                y0_px = float(kv[1])
            if kv[0] == 'detect_dist':
                d_px = float(kv[1])
            if kv[0] == 'detect_tilt_alpha':
                rot_rad = float(kv[1])
            if kv[0] == 'detect_tilt_delta':
                tilt_rad = float(kv[1])
            if kv[0] == 'wavelenght':
                wl = float(kv[1])
        self.outputs['cal_params'] = dict({
            'x0_pixel':x0_px,
            'y0_pixel':y0_px,
            'd_pixel':d_px,
            'pixel_size':pxsz,
            'rotation_rad':rot_rad,
            'tilt_rad':tilt_rad,
            'lambda':wl,
            'fpolz':fpolz})


