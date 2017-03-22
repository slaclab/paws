"""
Convert WXDIFF .calib output 
to a dict of PyFAI PONI parameters,
by first converting from WXDIFF to Fit2D,
then using a pyFAI.AzimuthalIntegrator 
to convert from Fit2D to PONI format.
"""

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
    
    # ---WXDIFF FORMAT--- #

    # ---PONI FORMAT--- #
    # PONI: point of normal incidence
    # PONI format projects the point-shaped sample orthogonally onto projector plane,
    # and gives the coordinates of that projection as the PONI,
    # and the distance to the PONI is the shortest distance from sample to detector plane.
    # coordinate axes: x1 vertical, x2 and x3 horizontal, x3 along beam.
    # detector axes: with zero rotations, d1 vertical, d2 horizontal, d3 along beam.
    # axes defined on C format, first dimension is vertical, second dimension is horizontal.
    # the first dimension (vertical) is fast, the second dimension (horizontal) is slow. TODO: verify this
    # when poni=0 and rot=0, d = x 
    # dictionary keys and definitions:
    # 'dist': distance in meters from sample to PONI on detector plane
    # 'poni1': vertical coordinate of PONIon detector axes where poni intersects detector plane 
    # 'poni2': horizontal coordinate on detector axes where poni intersects detector plane 
    # 'rot1': rotation of detector body about x1, applied first, radians
    # 'rot2': rotation of detector body about x2, applied second, radians
    # 'rot3': rotation of detector body about beam axis x3, applied third, radians
    # 'pixel1': pixel dimension along d1 (vertical), meters
    # 'pixel2': pixel dimension along d2 (horizontal), meters
    # 'wavelength': wavelength in meters
    # 'fpolz': polarization factor- not actually a PONI parameter, but it's ok to put it here 
    # 'detector': optional pyFAI detector object
    # 'splineFile' optional spline file describing detector distortion

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
            if kv[0] == 'bcenter_x':
                bcx_wx = float(kv[1])       # WXDIFF x coord relative to 'bottom left' corner of detector
                                            # where beam axis intersects detector plane,
                                            # in pixels w/ 150um pixel size
                                            # TODO: double check wxdiff units
                                            # Fit2D centerX is in pixels 
                bcx_m = bcx_wx*150E-6
                bcx_f2d = bcx_m/pxsz_m
            if kv[0] == 'bcenter_y':
                bcy_wx = float(kv[1])       # WXDIFF y coord relative to 'bottom left' corner of detector
                                            # where beam axis intersects detector plane,
                                            # in pixels w/ 150um pixel size
                                            # TODO: double check wxdiff units
                                            # Fit2D centerY is in pixels
                bcy_m = bcy_wx*150E-6
                bcy_f2d = bcy_m/pxsz_m
            if kv[0] == 'detect_dist':
                d_px = float(kv[1])         # WXDIFF direct detector distance 
                                            # from sample to where beam axis intersects detector plane,
                                            # in pixels w/ 150um pixel size
                                            # TODO: double check wxdiff units
                                            # Fit2D directDist (mm) = d_px*150E-3
                d_m = d_px*150E-6 
                d_mm = d_m*1E3 
            if kv[0] == 'detect_tilt_alpha':    
                rot_rad = float(kv[1])      # WXDIFF alpha is tilt plane rotation in rad 
                                            # TODO: double check wxdiff units 
                                            # Fit2D tiltPlanRotation  = 360-rot_rad*180/pi 
                rot_deg = rot_rad*float(180)/np.pi
                rot_f2d = float(360)-rot_deg
            if kv[0] == 'detect_tilt_delta':
                tilt_rad = float(kv[1])     # WXDIFF delta is the tilt in rad
                                            # TODO: double check wxdiff units 
                                            # Fit2D tilt = tilt_rad*180/pi
                tilt_deg = tilt_rad*float(180)/np.pi
            if kv[0] == 'wavelenght':
                wl_A = float(kv[1])         # WXDIFF 'wavelenght' is in Angstroms
        # get wavelength in m 
        wl_m = wl_A*1E-10
        # use a pyFAI.AzimuthalIntegrator() to do the conversion
        p = pyFAI.AzimuthalIntegrator(wavelength = wl_m) 
        p.setFit2D(d_mm,bcx_f2d,bcy_f2d,tilt_deg,rot_f2d,pxsz_um,pxsz_um)
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

