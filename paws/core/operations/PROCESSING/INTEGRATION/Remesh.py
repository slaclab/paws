"""
Calibrate and reduce an image, given calibration parameters.

This module calls on pipeline.remesh.remesh 
to correct the (GI) images for curvature of 
the Ewald's sphere. 
"""

import numpy as np
from pyFAI.geometry import Geometry
# TODO: this op shouldn't depend on Xicam's pipeline module
#from pipeline import remesh

from ... import Operation as opmod 
from ...Operation import Operation

class Remesh(Operation):
    """
    Input image data (ndarray), pyFAI Geometory object, Angle of Incidence
    Return q_par, q_vrt, I(q_par, q_vrt) 
    """
    def __init__(self):
        input_names = ['image_data','pyFAI_geometory', 'alphai']
        output_names = ['qpar','qvrt','I']
        super(Remesh, self).__init__(input_names, output_names)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['pyFAI_geometory'] = 'PyFAI Geometry python object'
        self.input_doc['alphai'] = 'Angle of Incidence'
        self.input_type['image_data'] = opmod.workflow_item
        self.input_type['pyFAI_geometory'] = opmod.workflow_item
        self.input_type['alphai'] = opmod.workflow_item
        self.output_doc['qpar'] = 'q-parallel'
        self.output_doc['qvrt'] = 'q-vertical' 
        self.output_doc['I'] = 'intensity as a function of qpar, qvrt'

    def run(self):
        img = self.inputs['image_data']
        geometry = self.inputs['pyFAI_geometory']
        alphai = self.inputs['alphai']
        #qpar, qvrt, intensity = remesh.remesh(img, geometry, alphai)
        qpar, qvrt, intensity = None, None, None
        # save results to self.outputs
        self.outputs['qpar'] = qpar
        self.outputs['qvrt'] = qvrt
        self.outputs['I'] = intensity
