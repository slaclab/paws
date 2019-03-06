from collections import OrderedDict

import pyFAI

from ..Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(poni_dict=None)

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
 
    Input a text file expressing results of Nika automated calibration.
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
        super(NikaToPONI,self).__init__(inputs,outputs)
        self.input_doc['file_path'] = 'text file expressing nika automated calibration results- '\
            'see documentation of this operation class for the expected format of this file'
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters, as found in a .poni file'

    def run(self):
        fpath = self.inputs['file_path']
        for line in open(fpath,'r'):
            kv = line.strip().split('=')

            if 'sample_to_CCD_mm' in kv[0]:
                d_mm = float(kv[1])
            if 'pixel_size_x_mm' in kv[0]:
                pxsz_x_mm = float(kv[1])
            if 'pixel_size_y_mm' in kv[0]:
                pxsz_y_mm = float(kv[1])
            if 'beam_center_x_pix' in kv[0]:
                bcx_px = float(kv[1])       # Nika reports the x coord relative to 'bottom left' corner of detector
                                            # where beam axis intersects detector plane, in pixels 
            if 'beam_center_y_pix' in kv[0]:
                bcy_px = float(kv[1])       # same as beam_center_x_pix but for y 
            if 'horizontal_tilt_deg' in kv[0]:    
                htilt_deg = float(kv[1])    # Nika reports the horizontal tilt in degrees...
            if 'vertical_tilt_deg' in kv[0]:
                vtilt_deg = float(kv[1])    # Nika reports the vertical tilt in degrees...
            if 'wavelength_A' in kv[0]:
                wl_A = float(kv[1])         # Nika reports wavelength is in Angstroms

        # get wavelength in m 
        wl_m = wl_A*1E-10
        pxsz_x_um = pxsz_x_mm * 1000
        pxsz_y_um = pxsz_y_mm * 1000
        # TODO: check whether these rotation angle mappings are correct. 
        tilt_deg = -1.*htilt_deg
        rot_fit2d = vtilt_deg
        # use a pyFAI.AzimuthalIntegrator() to do the conversion
        p = pyFAI.AzimuthalIntegrator(wavelength = wl_m) 
        p.setFit2D(d_mm,bcx_px,bcy_px,tilt_deg,rot_fit2d,pxsz_x_um,pxsz_y_um)
        poni_dict = p.getPyFAI()
        self.outputs['poni_dict'] = poni_dict 

