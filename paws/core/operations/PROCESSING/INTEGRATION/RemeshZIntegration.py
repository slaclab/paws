# -- coding: utf-8 --
"""
Integrate an ROI on image in Z-direction
"""

import numpy as np
# TODO: this shouldn't depend on xicam's pipeline
#from pipeline import remesh_integ

from ... import Operation as opmod 
from ...Operation import Operation

class RemeshZIntegration(Operation):
    """
    Input image data (ndarray), mask, ROI mask, qvrt, qpar
    Output lists containing q and I(q) 
    """
    def __init__(self):
        input_names = list(['data', 'mask', 'ROI_mask', 'qvrt', 'qpar'])
        output_names = list(['qz','zprofile'])
        super(RemeshZIntegration, self).__init__(input_names, output_names)
        self.input_doc['data'] = '2d array representing intensity for each pixel'
        self.input_doc['mask'] = '2d array for image mask, same shape as image_data'
        self.input_doc['ROI_mask'] = '2d array for ROI mask, same shape as image_data'
        self.input_doc['qvrt'] = 'q_z axis'
        self.input_doc['qpar'] = 'q_p axis'

        self.output_doc['qz'] = 'Scattering vector magnitude q in 1/Angstrom.'
        self.output_doc['zprofile'] = 'Integrated intensity at q.'

    def run(self):
        data = self.inputs['data']
        mask = self.inputs['mask']
        cut = self.inputs['ROI_mask']
        qv = self.inputs['qvrt']
        qp = self.inputs['qpar']
        qz, zprof = None, None
        #qz, zprof = remesh_integ.remeshzintegrate(data, mask, cut = cut, qvrt = qv, qpar = ap)
        self.outputs['qz'] = qz
        self.outputs['zprofile'] = zprof
