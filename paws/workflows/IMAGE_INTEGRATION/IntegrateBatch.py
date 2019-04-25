from collections import OrderedDict
import time
import copy
import os

import numpy as np
import fabio

from ..Workflow import Workflow
from ...pawstools import primitives

inputs = OrderedDict(
    integrator=None, 
    images=[],
    image_paths=[],
    n_points=1000,
    polz_factor=1.,
    output_dir=None
    )

outputs = OrderedDict(
    data=[],
    data_paths=[]
    )

class IntegrateBatch(Workflow):

    def __init__(self):
        super(IntegrateBatch,self).__init__(inputs,outputs)

    def run(self):
        if self.inputs['images']:
            imgs = self.inputs['images']
        else:
            imgs = [fabio.open(imgp).data for imgp in self.inputs['image_paths']]
        for img,imgp in zip(imgs,self.inputs['image_paths']):
            q,I = self.inputs['integrator'].integrate_to_1d(img,
                npt=self.inputs['n_points'],
                polz_factor=self.inputs['polz_factor'])
            q_I = np.array([q,I]).T
            self.outputs['data'].append(q_I)
            if self.inputs['output_dir']:
                dat_fn = os.path.splitext(os.path.split(imgp)[1])[0]+'.dat'
                dat_path = os.path.join(self.inputs['output_dir'],dat_fn)
                np.savetxt(dat_path,q_I,delimiter=' ',header='q (1/Angstrom), I (arb)')
                self.outputs['data_paths'].append(dat_path)
        return self.outputs

