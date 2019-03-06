from collections import OrderedDict

import pyFAI

from ..Operation import Operation

inputs=OrderedDict(
    fit2d_file=None,
    wavelength_A=None)
outputs=OrderedDict(
    poni_dict=None,
    fit2d_dict=None)

class Fit2DToPONI(Operation):
    """Produce PONI calibration parameters from a Fit2D calibration result. 

    Reads in Fit2D calibration result from a text file,
    converts it to a dict of PyFAI PONI parameters.

    WARNING: Some developers have claimed that 
    the Fit2D software itself computes tilted geometries incorrectly.
    If using actual Fit2D output with tilts, 
    it is suggested that a new calibration be attempted,
    with a different package (something other than Fit2D).
    Use tilts from Fit2D output at your own risk.
 
    Format of text file for Fit2D parameters is expected to be:
    directDist=____         # sample-detector
    centerX=____            # beam center on detector, in pixels
    centerY=____            # beam center on detector, in pixels
    pixelX=____             # pixel width, microns
    pixelY=____             # pixel height, microns
    tilt=____               # degrees
    tiltPlanRotation=____   # degrees
    splineFile=____         # optional detector distortion correction file
    """
    
    def __init__(self):
        super(Fit2DToPONI,self).__init__(inputs,outputs)
        self.input_doc['fit2d_file'] = 'text file describing Fit2D geometry'
        self.input_doc['wavelength_A'] = 'wavelength in Angstroms'
        self.output_doc['fit2d_dict'] = 'Fit2D calibration parameters'
        self.output_doc['poni_dict'] = 'pyFAI calibration parameters'

    def run(self):
        fpath = self.inputs['fit2d_file']
        fit2d_dict = OrderedDict() 
        for line in open(fpath,'r'):
            kv = line.strip().split('=')
            fit2d_dict[kv[0]] = float(kv[1])
        # get wavelength in m 
        wl_m = self.inputs['wavelength_A']*1E-10
        # use a pyFAI.AzimuthalIntegrator() to do the conversion
        p = pyFAI.AzimuthalIntegrator(wavelength = wl_m) 
        p.setFit2D(
            fit2d_dict['directDist'],
            fit2d_dict['centerX'],
            fit2d_dict['centerY'],
            fit2d_dict['tilt'],
            fit2d_dict['tiltPlanRotation'],
            fit2d_dict['pixelX'],
            fit2d_dict['pixelY'])
        poni_dict = p.getPyFAI()
        self.outputs['fit2d_dict'] = fit2d_dict 
        self.outputs['poni_dict'] = poni_dict 

