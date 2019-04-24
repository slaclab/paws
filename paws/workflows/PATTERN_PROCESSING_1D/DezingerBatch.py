from collections import OrderedDict
import time
import copy
import os

import numpy as np 

from ..Workflow import Workflow
from ...pawstools import primitives
from ...operations.ZINGERS.EasyZingers1d import EasyZingers1d

inputs = OrderedDict(
    q_I_arrays=[],
    q_I_paths=[],
    sharpness_limit=40.,
    window_width=10,
    output_dir=None
    )

outputs = OrderedDict(
    data=[],
    data_paths=[]
    )

class DezingerBatch(Workflow):

    def __init__(self):
        super(DezingerBatch,self).__init__(inputs,outputs)

    def run(self):
        dz = EasyZingers1d()
        if self.inputs['q_I_arrays']:
            q_I_arrs = self.inputs['q_I_arrays']
        else:
            q_I_arrs = [np.loadtxt(datp) for datp in self.inputs['q_I_paths']]
        for q_I,q_I_path in zip(q_I_arrs,self.inputs['q_I_paths']):
            dz_out = dz.run_with(q_I=q_I,
                sharpness_limit=self.inputs['sharpness_limit'],
                window_width=self.inputs['window_width'])
            q_I_dz = dz_out['q_I_dz'] 
            self.outputs['data'].append(q_I_dz)
            if self.inputs['output_dir']:
                dz_fn = os.path.splitext(os.path.split(q_I_path)[1])[0]+'_dz.dat'
                dz_path = os.path.join(self.inputs['output_dir'],dz_fn)
                np.savetxt(dz_path,q_I_dz,delimiter=' ',header='q (1/Angstrom), I (arb)')
                self.outputs['data_paths'].append(dz_path)
        return self.outputs

