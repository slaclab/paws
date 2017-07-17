"""
Operation for automatic discovery of diffraction image calibration parameters. 
"""

import numpy as np
import pyFAI as pf
import pyFAI.calibrant as pfc

from ... import Operation as op
from ...Operation import Operation

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
        self.input_doc['calibrant'] = 'name of calibrant- supported values: AgBh'
        self.input_doc['wavelength'] = 'wavelength, in Angstrom'
        self.input_doc['pixel_size'] = 'pixel size in microns'
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_src['image_data'] = op.wf_input
        self.input_src['calibrant'] = op.text_input 
        self.input_src['wavelength'] = op.text_input 
        self.input_src['pixel_size'] = op.text_input 
        self.input_src['fpolz'] = op.text_input
        self.input_type['image_data'] = op.ref_type
        self.input_type['calibrant'] = op.str_type
        self.input_type['wavelength'] = op.float_type
        self.input_type['pixel_size'] = op.float_type
        self.input_type['fpolz'] = op.float_type
        self.inputs['calibrant'] = 'AgBh' 
        self.inputs['wavelength'] = 0.799898 
        self.inputs['pixel_size'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.output_doc['cal_params'] = 'Dictionary of the solved calibration parameters, .poni format'

    def run(self):
        img = self.inputs['image_data']
        calid = self.inputs['calibrant']
        wl = self.inputs['wavelength'] 
        pxsz = self.inputs['pixel_size']
        fpolz = self.inputs['fpolz']
        if calid == 'AgBh':
            # Define an AgBh calibrant
            cal = pfc.ALL_CALIBRANTS[calid]
            cal.set_wavelength(1E-10)
        else:
            raise ValueError('[{}] Unsupported calibrant: {}'.format(__name__,calid))

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


