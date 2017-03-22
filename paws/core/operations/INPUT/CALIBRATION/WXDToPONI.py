"""
Convert WXDIFF .calib output 
to a dict of PyFAI PONI parameters,
by first converting from WXDIFF to Fit2D,
then using a pyFAI.AzimuthalIntegrator 
to convert from Fit2D to PONI format.

    
WXDIFF FORMAT
-------------

This format is buried somewhere deep in the knowledge of a few diffraction experts.
I hope it can be cleanly documented here over time.
Detector plane origin is the bottom left corner of the detector. TODO: verify

.calib file lines (and notes):                  
    imagetype=uncorrected-q         (???)
    dtype=uint16                    (img data type = unsigned 16-bit integers)
    horsize=___                     (horizontal extent in pixels)
    versize=___                     (vertical extent in pixels)
    region_ulc_x=___                (???)
    region_ulc_y=___                (???)
    bcenter_x=___                   (horizontal position of beam center, in 150um pixels)
    bcenter_y=___                   (vertical position of beam center, in 150um pixels)
    detect_dist=___                 (direct distance to detector plane intersection along beam axis, in 150um pixels)
    detect_tilt_alpha=___           (rotation of detector tilt axis in radians)
    detect_tilt_delta=___           (detector tilt in radians)
    wavelenght=___                  (the typo 'wavelenght' is built into wxdiff, and it is reported in angstroms)
    Qconv_const=0.000725200948528   (???)


FIT2D FORMAT
------------

Similar to WXDIFF format, with key differences.
Detector plane origin is the bottom left corner of the detector.

Fit2D dict keys and definitions:
   'directDist': direct distance to detector plane along beam axis, in mm
   'centerX': horizontal position on the detector plane where the beam intersects, in px
   'centerY': vertical position on the detector plan where the beam intersects, in px
   'pixelX': horizontal size of pixel, in um 
   'pixelY': vertical size of pixel, in um 
   'tilt': detector tilt in degrees
   'tiltPlanRotation': detector rotation in degrees = 360 minus WXDIFF alpha 
   'splineFile' optional spline file describing detector distortion


PONI FORMAT
-----------

PONI: point of normal incidence
PONI format projects the point-shaped sample orthogonally onto projector plane,
and gives the coordinates of that projection as the PONI,
and the distance to the PONI is the shortest distance from sample to detector plane.
coordinate axes: x1 vertical, x2 and x3 horizontal, x3 along beam.
detector axes: with zero rotations, d1 vertical, d2 horizontal, d3 along beam.
axes defined on C format, first dimension is vertical, second dimension is horizontal.
the first dimension (vertical) is fast, the second dimension (horizontal) is slow. 
when poni=0 and rot=0, d = x 

PONI dict keys and definitions:
    'dist': distance in meters from sample to PONI on detector plane
    'poni1': vertical coordinate of PONIon detector axes where poni intersects detector plane 
    'poni2': horizontal coordinate on detector axes where poni intersects detector plane 
    'rot1': rotation of detector body about x1, applied first, radians
    'rot2': rotation of detector body about x2, applied second, radians
    'rot3': rotation of detector body about beam axis x3, applied third, radians
    'pixel1': pixel dimension along d1 (vertical), meters
    'pixel2': pixel dimension along d2 (horizontal), meters
    'wavelength': wavelength in meters
    'fpolz': polarization factor- not actually a PONI parameter, but it's ok to put it here 
    'detector': optional pyFAI detector object
    'splineFile' optional spline file describing detector distortion
"""
# TODO: verify wxdiff units and description

import os

import numpy as np
import pyFAI

from ...operation import Operation
from ... import optools

class WXDToPONI(Operation):
    """
    Input .calib file from WXDIFF automated calibration,
    input pixel size and polarization factor,
    output dict of pyFAI PONI calibration parameters.
    """
    
    def __init__(self):
        input_names = ['wxd_file','pixel_size_um','fpolz']
        output_names = ['poni_dict']
        super(WXDToPONI,self).__init__(input_names,output_names)
        self.input_doc['wxd_file'] = '.calib file produced by WXDIFF calibration'
        self.input_doc['pixel_size_um'] = 'pixel size in microns'
        self.input_doc['fpolz'] = 'polarization factor'
        self.input_src['wxd_file'] = optools.fs_input
        self.input_src['pixel_size_um'] = optools.text_input 
        self.input_src['fpolz'] = optools.text_input
        self.input_type['wxd_file'] = optools.path_type
        self.input_type['pixel_size_um'] = optools.float_type
        self.input_type['fpolz'] = optools.float_type
        self.inputs['pixel_size_um'] = 79 
        self.inputs['fpolz'] = 0.95 
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters, as found in a .poni file'

    def run(self):
        fpath = self.inputs['wxd_file']
        pxsz_um = self.inputs['pixel_size_um']
        pxsz_m = pxsz_um*1E-6
        fpolz = self.inputs['fpolz']
        for line in open(fpath,'r'):
            kv = line.strip().split('=')
            if kv[0] == 'detect_dist':
                d_px = float(kv[1])         # WXDIFF direct detector distance, 
                                            # from sample to where beam axis intersects detector plane,
                                            # in pixels w/ 150um pixel size.
                                            # Fit2D uses this input in mm to set its spatial scale,
                                            # so it has to be converted to distance units (mm for Fit2D). 
                                            # Because this scales the spatial representation for Fit2D,
                                            # the other inputs can still be given in pixel units,
                                            # without converting between pixel sizes.
                d_m = d_px*150E-6 
                d_mm = d_m*1E3 
            if kv[0] == 'bcenter_x':
                bcx_px = float(kv[1])       # WXDIFF x coord relative to 'bottom left' corner of detector
                                            # where beam axis intersects detector plane, in pixels 
                                            # Fit2D centerX is also in pixels 
            if kv[0] == 'bcenter_y':
                bcy_px = float(kv[1])       # WXDIFF y coord relative to 'bottom left' corner of detector
                                            # where beam axis intersects detector plane, in pixels 
                                            # Fit2D centerY is also in pixels
            if kv[0] == 'detect_tilt_alpha':    
                rot_rad = float(kv[1])      # WXDIFF alpha is tilt plane rotation in rad 
                                            # Fit2D tiltPlanRotation  = 360-rot_rad*180/pi 
                rot_deg = rot_rad*float(180)/np.pi
                rot_fit2d = float(360)-rot_deg
            if kv[0] == 'detect_tilt_delta':
                tilt_rad = float(kv[1])     # WXDIFF delta is the tilt in rad
                tilt_deg = tilt_rad*float(180)/np.pi
            if kv[0] == 'wavelenght':
                wl_A = float(kv[1])         # WXDIFF 'wavelenght' is in Angstroms
        # get wavelength in m 
        wl_m = wl_A*1E-10
        # use a pyFAI.AzimuthalIntegrator() to do the conversion
        p = pyFAI.AzimuthalIntegrator(wavelength = wl_m) 
        p.setFit2D(d_mm,bcx_px,bcy_px,tilt_deg,rot_fit2d,pxsz_um,pxsz_um)

        print p

        poni_dict = p.getPyFAI()
        poni_dict['fpolz'] = fpolz
        self.outputs['poni_dict'] = poni_dict 

        # pixel_size is expected to be in microns
        #pxsz = self.inputs['cal_params']['pixel_size']
        #fpolz = self.inputs['cal_params']['fpolz']
        # lambda is expected to be in Angstroms.
        #wl = self.inputs['cal_params']['lambda']
        # convert wl from Angstroms to meters
        #wl = wl*1E-10
        # detector distance: from pixels to mm
        #d_px = self.inputs['cal_params']['d_pixel']
        #d_mm = d_px*pxsz*0.001
        #rot = (2*np.pi-self.inputs['cal_params']['rotation_rad'])*360/(2*np.pi)
        #tilt = self.inputs['cal_params']['tilt_rad']*360/(2*np.pi)
        #x0 = self.inputs['cal_params']['x0_pixel']
        #y0 = self.inputs['cal_params']['y0_pixel']
        #p = pyFAI.AzimuthalIntegrator(wavelength=wl)
        #p.setFit2D(d_mm,x0,y0,tilt,rot,pxsz,pxsz)
        #p.write('example.poni')

