import numpy as np
from collections import OrderedDict

import pyFAI

from ... import Operation as opmod 
from ...Operation import Operation

inputs = OrderedDict(
    image_data=None,
    integrator=None,
    npt=1000,
    polz_factor=0.,
    unit='q_A^-1',
    integrate_args={})
outputs = OrderedDict(
    q=None,
    I=None,
    q_I=None)
        
class ApplyIntegrator1d(Operation):
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
        super(ApplyIntegrator1d,self).__init__(inputs,outputs)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['integrator'] = 'A PyFAI.AzimuthalIntegrator object'
        self.input_doc['npt'] = 'number of q-points to integrate'
        self.input_doc['polz_factor'] = 'polarization factor, '\
            'in case polarization correction is needed'
        self.input_doc['unit'] = 'choice of unit. See PyFAI documentation for options.' 
        self.input_doc['integrate_args'] = 'dict of keyword args '\
            'to pass to pyFAI.AzimuthalIntegrator.integrate1d(). '\
            'Where relevant, the values in this dict will be replaced '\
            'by inputs to the operation, e.g. for npt.' 
        self.output_doc['q'] = 'Scattering vector magnitude q in 1/Angstrom.'
        self.output_doc['I'] = 'Integrated intensity at q.'
        self.output_doc['q_I'] = 'q and I zipped together an a n-by-2 numpy array.'
        self.input_datatype['unit'] = 'str'
        self.input_datatype['integrate_args'] = 'dict'
        self.input_datatype['npt'] = 'int'
        self.input_datatype['polz_factor'] = 'float'

    def run(self):
        img = self.inputs['image_data']
        npt = self.inputs['npt']
        intgtr = self.inputs['integrator']
        kw = self.inputs['integrate_args']
        if self.inputs['polz_factor']:
            kw['polarization_factor'] = self.inputs['polz_factor']
        if self.inputs['unit']:
            kw['unit'] = self.inputs['unit']
        q,I = intgtr.integrate1d(img,npt,**kw)
        self.outputs['q'] = q 
        self.outputs['I'] = I
        self.outputs['q_I'] = np.array([q,I]).T

