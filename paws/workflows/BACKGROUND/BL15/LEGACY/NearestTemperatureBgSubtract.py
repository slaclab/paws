from collections import OrderedDict
import os

import numpy as np

from ....Workflow import Workflow 
from ....IO.BL15.LEGACY.ReadBatch import ReadBatch
from .....operations.PROCESSING.BACKGROUND.BgSubtract import BgSubtract
from .....operations.IO.NumpySave import NumpySave

inputs = OrderedDict(
    bg_header_dir = None,
    bg_header_regex = '*.txt',
    bg_header_suffix = '',
    bg_data_dir = None,
    bg_data_suffix = '',
    bg_data_ext = '.dat',
    sample_header_dir = None,
    sample_header_regex = '*.txt',
    sample_header_suffix = '',
    sample_data_dir = None,
    sample_data_suffix = '',
    sample_data_ext = '.dat',
    temperature_key = 'TEMP',
    output_dir = None,
    output_suffix = '_bgsub'
    )

outputs = OrderedDict(
    bg_temperatures = [],
    sample_temperatures = [],
    nearest_bg_temperatures = [],
    q_I_bgsub = [],
    dI_bgsub = []
    )

class NearestTemperatureBgSubtract(Workflow):

    def __init__(self):
        super(NearestTemperatureBgSubtract,self).__init__(inputs,outputs)
        self.add_operation('read_bgs',ReadBatch())
        self.add_operation('read_samples',ReadBatch())
        self.add_operation('bg_subtract',BgSubtract())
        self.add_operation('write_q_I_bgsub',NumpySave())

    def run(self):
        self.operations['read_bgs'].operations['read'].disable_ops('read_image','read_system')
        self.operations['read_samples'].operations['read'].disable_ops('read_image','read_system')
        bg_data = self.operations['read_bgs'].run_with(
            header_dir=self.inputs['bg_header_dir'],
            header_suffix=self.inputs['bg_header_suffix'],
            header_regex=self.inputs['bg_header_regex'],
            q_I_dir=self.inputs['bg_data_dir'],
            q_I_suffix=self.inputs['bg_data_suffix'],
            q_I_ext=self.inputs['bg_data_ext']
            )
        sample_data = self.operations['read_samples'].run_with(
            header_dir=self.inputs['sample_header_dir'],
            header_suffix=self.inputs['sample_header_suffix'],
            header_regex=self.inputs['sample_header_regex'],
            q_I_dir=self.inputs['sample_data_dir'],
            q_I_suffix=self.inputs['sample_data_suffix'],
            q_I_ext=self.inputs['sample_data_ext']
            )
        T_key = self.inputs['temperature_key']
        bg_temps = [hdr[T_key] for hdr in bg_data['header_data']]
        sample_temps = [hdr[T_key] for hdr in sample_data['header_data']]
        closest_T_idx = [np.argmin(np.abs([T_bg - T_meas for T_bg in bg_temps])) for T_meas in sample_temps]
        sample_bg_temps = [bg_temps[idx] for idx in closest_T_idx]
        q_I_bgsub = []
        dI_bgsub = []
        nsamp = len(sample_temps)
        for isamp, sfn, q_I_sample, dI_sample, T_sample, T_bg, bg_idx in \
        zip(range(nsamp),sample_data['filenames'],sample_data['q_I'],sample_data['dI'],sample_temps,sample_bg_temps,closest_T_idx):
            self.message_callback('RUNNING {} / {}'.format(isamp,nsamp))
            self.message_callback('Sample temperature: {}, nearest background: {}'.format(T_sample,T_bg))
            bgsub_output = self.operations['bg_subtract'].run_with(
                q_I = q_I_sample,
                q_I_bg = bg_data['q_I'][bg_idx],
                dI = dI_sample,
                dI_bg = bg_data['dI'][bg_idx]
                )
            dI_bgsub.append(bgsub_output['dI'])
            q_I_bgsub.append(bgsub_output['q_I_bgsub'])
            outfile = os.path.join(self.inputs['output_dir'],sfn+self.inputs['output_suffix']+'.dat')
            self.operations['write_q_I_bgsub'].run_with(
                data = bgsub_output['q_I_bgsub'],
                header = 'q (1/Angstrom), Intensity (arb)',
                file_path = outfile
                )
        self.outputs.update(
            bg_temperatures = bg_temps,
            sample_temperatures = sample_temps,
            nearest_bg_temperatures = sample_bg_temps,
            q_I_bgsub = q_I_bgsub,
            dI_bgsub = dI_bgsub 
            )
        return self.outputs

