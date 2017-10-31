import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools.integration import integrate

inputs = OrderedDict(image_data=None,geom=None,alpha_i=None)
outputs = OrderedDict(q_parallel=None,q_normal=None,I=None)

class Remesh(Operation):
"""Remesh an image for Ewald's sphere corrections under grazing incidence."""

    def __init__(self):
        super(Remesh, self).__init__(inputs, outputs)
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.input_doc['geom'] = 'pyFAI.Geometry object describing measurement geometry'
        self.input_doc['alpha_i'] = 'angle of incidence'
        self.input_type['image_data'] = opmod.workflow_item
        self.input_type['geom'] = opmod.workflow_item
        self.output_doc['q_par'] = 'q-parallel'
        self.output_doc['q_norm'] = 'q-vertical' 
        self.output_doc['I'] = 'array of intensities corresponding to q_parallel and q_vertical'

    def run(self):
        img = self.inputs['image_data']
        g = self.inputs['geom']
        a = self.inputs['alpha_i']
        qpar, qvrt, intensity = integrate.remesh(img, geometry, alphai)
        # save results to self.outputs
        self.outputs['q_par'] = qpar
        self.outputs['q_norm'] = qvrt
        self.outputs['I'] = intensity

