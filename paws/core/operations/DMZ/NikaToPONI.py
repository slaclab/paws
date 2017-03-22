"""
Operation converts WXDIFF .calib output to PyFAI .poni parameters
"""

import os

import numpy as np
import pyFAI

from ...operation import Operation
from ... import optools

class WXDToPONI(Operation):
    """
    Input .calib file from WXDIFF automated calibration output.
    """
    def __init__(self):
        input_names = ['wxd_file']
        output_names = ['poni_dict']
        super(WXDToPONI,self).__init__(input_names,output_names)
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
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters, as found in a .poni file'

    def run(self):
        fpath = self.inputs['wxd_file']
        pxsz = self.inputs['pixel_size']
        fpolz = self.inputs['fpolz']
        for line in open(fpath,'r'):
            kv = line.strip().split('=')
            if kv[0] == 'bcenter_x':
                # bcenter_x gives the horizontal coord of where the beam hits the detector plane, in pixels
                x0_px = float(kv[1])
            if kv[0] == 'bcenter_y':
                # bcenter_y gives the vertical coord of where the beam hits the detector plane, in pixels
                y0_px = float(kv[1])
            if kv[0] == 'detect_dist':
                # detect_dist is the distance from the sample to the detector plane.
                # wxdiff reports it in pixels, with a 150um pixel size assumption.
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


