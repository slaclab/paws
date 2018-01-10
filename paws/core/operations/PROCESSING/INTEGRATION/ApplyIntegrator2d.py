import numpy as np
from collections import OrderedDict

import pyFAI

from ... import Operation as opmod 
from ...Operation import Operation

inputs = OrderedDict(
    image_data=None,
    integrator=None,
    npt_rad=1000,
    npt_azim=1000,
    polz_factor=0.,
    unit='q_A^-1',
    integrate_args={})
outputs = OrderedDict(
    q=None,
    chi=None,
    I_at_q_chi=None)

class ApplyIntegrator2d(Operation):
    """Integrate an image using an existing PyFAI.AzimuthalIntegrator.
    
    Input image data (ndarray), PyFAI.AzimuthalIntegrator, 
    and a dict of other keyword parameters to be passed to
    PyFAI.AzimuthalIntegrator.integrate1d().
    
    Refer to the PyFAI documentation at 
    http://pyfai.readthedocs.io/en/latest/ 
    for supported keyword arguments 
    as well as parameter definitions and defaults.
    """

    def __init__(self):
        super(ApplyIntegrator2d,self).__init__(inputs,outputs)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['integrator'] = 'A PyFAI.AzimuthalIntegrator object'
        self.input_doc['npt_rad'] = 'number of q-points to integrate'
        self.input_doc['npt_azim'] = 'number of chi-points to integrate'
        self.input_doc['polz_factor'] = 'polarization factor, '\
            'in case polarization correction is needed'
        self.input_doc['unit'] = 'choice of unit. See PyFAI documentation for options.' 
        self.input_doc['integrate_args'] = 'dict of keyword args '\
            'to pass to pyFAI.AzimuthalIntegrator.integrate2d(). '\
            'Where relevant, the values in this dict will be replaced '\
            'by inputs to the operation, e.g. for npt_rad and npt_azim.' 
        self.output_doc['q'] = 'Scattering vector magnitude q array in 1/Angstrom.'
        self.output_doc['chi'] = 'Azimuthal angle array.'
        self.output_doc['I_at_q_chi'] = '2d array of integrated intensity at q,chi.'
        self.input_datatype['unit'] = 'str'
        self.input_datatype['integrate_args'] = 'dict'
        self.input_datatype['npt_rad'] = 'int'
        self.input_datatype['npt_azim'] = 'int'
        self.input_datatype['polz_factor'] = 'float'

    def run(self):
        img = self.inputs['image_data']
        intgtr = self.inputs['integrator']
        npt_rad = self.inputs['npt_rad']
        npt_azim = self.inputs['npt_azim']
        kw = self.inputs['integrate_args']
        if self.inputs['polz_factor']:
            kw['polarization_factor'] = self.inputs['polz_factor']
        if self.inputs['unit']:
            kw['unit'] = self.inputs['unit']

        I_at_q_chi,q,chi = intgtr.integrate2d(img,npt_rad,npt_azim,**kw)
        
        self.outputs['q'] = q
        self.outputs['chi'] = chi
        self.outputs['I_at_q_chi'] = I_at_q_chi

