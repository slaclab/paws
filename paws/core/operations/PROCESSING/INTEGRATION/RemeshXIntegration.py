# -- coding: utf-8 --
"""
Integrate an ROI on image in X-direction
"""

import numpy as np
# TODO: this shouldn't depend on xicam's pipeline module
#from pipeline import remesh_integ

from ... import Operation as opmod 
from ...Operation import Operation

class RemeshXIntegration(Operation):
    """
    Input image data (ndarray), mask, ROI mask, qvrt, qpar
    Output arrays containing q and I(q) 
    """
    def __init__(self):
        input_names = list(['data', 'mask', 'ROI_mask', 'qvrt', 'qpar'])
        output_names = list(['qx','xprofile'])
        super(RemeshXIntegration, self).__init__(input_names, output_names)
        self.input_doc['data'] = '2d array representing intensity for each pixel'
        self.input_doc['mask'] = '2d array for image mask, same shape as image_data'
        self.input_doc['ROI_mask'] = '2d array for ROI mask, same shape as image_data'
        self.input_doc['qvrt'] = 'q_z axis'
        self.input_doc['qpar'] = 'q_p axis'

        self.output_doc['qx'] = 'Scattering vector magnitude q in 1/Angstrom.'
        self.output_doc['xprofile'] = 'Integrated intensity at q.'

    def run(self):
        data = self.inputs['data']
        mask = self.inputs['mask']
        cut = self.inputs['ROI_mask']
        qv = self.inputs['qvrt']
        qp = self.inputs['qpar']
        #qx, xprof = remesh_integ.remeshzintegrate(data, mask, cut = cut, qvrt = qv, qpar = ap)
        qx, xprof = None, None
        self.outputs['qx'] = qx
        self.outputs['xprofile'] = xprof
