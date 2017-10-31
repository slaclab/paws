from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools.integration import integration
        
inputs = OrderedDict(image_data=None,mask=None,ROI_mask=None,q_norm=None,q_par=None)
outputs = OrderedDict(q_x=None,I=None)

class RemeshXIntegration(Operation):
    """Integrate ROI-masked image in the q-parallel (horizontal) direction

    Input image data (ndarray), mask, ROI mask, qvrt, qpar
    Output arrays containing q_x and I(q_x) 
    """
    def __init__(self):
        super(RemeshXIntegration, self).__init__(inputs, outputs)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['mask'] = '2d array for image mask, same shape as image_data'
        self.input_doc['ROI_mask'] = '2d array for ROI mask, same shape as image_data'
        self.input_doc['q_norm'] = 'q_z axis'
        self.input_doc['q_par'] = 'q_p axis'
        self.output_doc['q_x'] = 'Scattering vector x component in 1/Angstrom.'
        self.output_doc['I'] = 'Integrated intensity at q_x.'

    def run(self):
        img = self.inputs['image_data']
        mask = self.inputs['mask']
        cut = self.inputs['ROI_mask']
        qv = self.inputs['q_norm']
        qp = self.inputs['q_par']
        qx, xprof = integration.remeshzintegrate(data, mask, cut = cut, qvrt = qv, qpar = ap)
        self.outputs['q_x'] = qx
        self.outputs['I'] = xprof
