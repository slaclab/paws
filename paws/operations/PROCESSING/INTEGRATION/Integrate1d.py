from __future__ import print_function
import numpy as np
from collections import OrderedDict

import pyFAI

from ...Operation import Operation

inputs = OrderedDict(
    image_data=None,
    integrator=None,
    npt=1000,
    polz_factor=0.,
    unit='q_A^-1')
outputs = OrderedDict(
    q=None,
    I=None,
    q_I=None)
        
class Integrate1d(Operation):
    """Integrate an image using a PyFAIIntegrator plugin.
    
    Input image data (ndarray), PyFAI.AzimuthalIntegrator, 
    and other parameters for PyFAI.AzimuthalIntegrator.integrate1d().
    
    Refer to the PyFAI documentation at 
    http://pyfai.readthedocs.io/en/latest/ 
    for supported keyword arguments 
    as well as parameter definitions and defaults.
    """

    def __init__(self):
        super(Integrate1d,self).__init__(inputs,outputs)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['integrator'] = 'A PyFAIIntegrator PawsPlugin'
        self.input_doc['npt'] = 'number of q-points to integrate'
        self.input_doc['polz_factor'] = 'polarization factor'
        self.input_doc['unit'] = 'choice of unit: see PyFAI documentation for options' 
        self.output_doc['q'] = 'Scattering vector magnitude q in 1/Angstrom'
        self.output_doc['I'] = 'Integrated intensity at q'
        self.output_doc['q_I'] = 'q and I together as n-by-2 numpy array'

    def run(self):
        img = self.inputs['image_data']
        npt = self.inputs['npt']
        intgtr = self.inputs['integrator']
        pzfac = self.inputs['polz_factor']
        u = self.inputs['unit']
        q,I = intgtr.integrate_to_1d(img,npt,polz_factor=pzfac,unit=u)
        self.outputs['q'] = q 
        self.outputs['I'] = I
        self.outputs['q_I'] = np.array([q,I]).T

