from collections import OrderedDict
import glob
import os

import numpy as np

from ..Workflow import Workflow 
from ...operations.IO.NumpyLoad import NumpyLoad 
from ...operations.PROCESSING.ArrayYMean import ArrayYMean 
from ...operations.PROCESSING.BACKGROUND.BgSubtract import BgSubtract
from ...operations.IO.NumpySave import NumpySave

inputs = OrderedDict(
    bg_dir = None,
    bg_regex = '*.dat',
    sample_dir = None,
    sample_regex = '*.dat',
    output_file = ''
    )

outputs = OrderedDict(
    q_I_bgsub = [],
    )

class BatchAverageBgSubtract(Workflow):

    def __init__(self):
        super(BatchAverageBgSubtract,self).__init__(inputs,outputs)
        self.add_operation('read',NumpyLoad())
        self.add_operation('y_mean',ArrayYMean())
        self.add_operation('bg_subtract',BgSubtract())
        self.add_operation('write_q_I_bgsub',NumpySave())

    def run(self):
        bg_files = glob.glob(os.path.join(self.inputs['bg_dir'],self.inputs['bg_regex']))
        sample_files = glob.glob(os.path.join(self.inputs['sample_dir'],self.inputs['sample_regex']))
        q_I_bg = []
        q_I_sample = []
        for fn in bg_files:
            bgdata = self.operations['read'].run_with(file_path=fn)
            q_I_bg.append(bgdata['data'])
        for fn in sample_files:
            sdata = self.operations['read'].run_with(file_path=fn)
            q_I_sample.append(sdata['data'])
        bg_q_I_mean = self.operations['y_mean'].run_with(x_y_arrays=q_I_bg)['x_ymean']
        sample_q_I_mean = self.operations['y_mean'].run_with(x_y_arrays=q_I_sample)['x_ymean']
        bgsub_data = self.operations['bg_subtract'].run_with(q_I=sample_q_I_mean,q_I_bg=bg_q_I_mean)
        q_I_bgsub = bgsub_data['q_I_bgsub']
        self.outputs['q_I_bgsub'] = q_I_bgsub
        self.operations['write_q_I_bgsub'].run_with(
            data = q_I_bgsub,
            header = 'q (1/Angstrom), Intensity (arb)',
            file_path = self.inputs['output_file']
            )
        return self.outputs

