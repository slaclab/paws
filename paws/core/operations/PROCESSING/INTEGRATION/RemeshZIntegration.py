import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools.integration import integration
        
inputs = OrderedDict(image_data=None,mask=None,ROI_mask=None,q_norm=None,q_par=None)
outputs = OrderedDict(q_z=None,I=None)

class RemeshZIntegration(Operation):
    """Integrate ROI-masked image in the q-normal (vertical) direction

    Input image data (ndarray), mask, ROI mask, qvrt, qpar
    Output arrays containing q_x and I(q_x) 
    """
    
    def __init__(self):
        super(RemeshZIntegration, self).__init__(inputs, outputs)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['mask'] = '2d array for image mask, same shape as image_data'
        self.input_doc['ROI_mask'] = '2d array for ROI mask, same shape as image_data'
        self.input_doc['q_norm'] = 'q normal component'
        self.input_doc['q_par'] = 'q parallel component'
        self.output_doc['q_z'] = 'Scattering vector z component in 1/Angstrom.'
        self.output_doc['I'] = 'Integrated intensity at q_z.'

    def run(self):
        data = self.inputs['image_data']
        mask = self.inputs['mask']
        cut = self.inputs['ROI_mask']
        qv = self.inputs['q_norm']
        qp = self.inputs['q_par']
        qz, zprof = integration.remeshzintegrate(data, mask, cut = cut, qvrt = qv, qpar = ap)
        self.outputs['q_z'] = qz
        self.outputs['I'] = zprof

