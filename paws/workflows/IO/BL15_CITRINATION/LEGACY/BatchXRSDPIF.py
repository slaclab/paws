import os
import copy
from collections import OrderedDict

import numpy as np

from ....Workflow import Workflow 
from ...BL15.LEGACY.ReadTimeSeries import ReadTimeSeries 
from .....operations.PACKAGING.PIF.PackXRSDPIF import PackXRSDPIF
from .....operations.IO.CITRINATION.UploadPIF import UploadPIF

inputs = OrderedDict(
    citrination_client = None,
    experiment_id = 'test',
    source_wavelength = None,
    header_dir = None,
    header_suffix = None,
    header_regex = None,
    q_I_dir = None,
    q_I_suffix = '',
    q_I_ext = '.dat',
    system_dir = None, 
    system_suffix = '',
    dataset_id = None,
    upload_pif = False,
    keep_pif_json = True
    )

outputs = OrderedDict()

class BatchXRSDPIF(Workflow):
    
    def __init__(self):
        super(BatchXRSDPIF,self).__init__(inputs,outputs)
        self.add_operations(
            read = ReadTimeSeries(),
            make_pif = PackXRSDPIF(),
            upload_pif = UploadPIF()
            )

    def run(self):
        expt_id = self.inputs['experiment_id']
        src_wl = self.inputs['source_wavelength']
        # READ THE TIMESERIES 
        self.operations['read'].operations['read_batch'].operations['read'].disable_ops('read_image')
        ts_data = self.operations['read'].run_with(
            header_dir = self.inputs['header_dir'],
            header_suffix = self.inputs['header_suffix'],
            header_regex = self.inputs['header_regex'],
            q_I_dir = self.inputs['q_I_dir'], 
            q_I_suffix = self.inputs['q_I_suffix'],
            q_I_ext = self.inputs['q_I_ext'],
            system_dir = self.inputs['system_dir'], 
            system_suffix = self.inputs['system_suffix'] 
            )
        # CREATE TIMESERIES OF PIFS
        all_pifs = []
        ts = ts_data['time']
        hdrs = ts_data['header_data']
        syss = ts_data['system']
        q_Is = ts_data['q_I']
        npifs = len(ts)
        for ipif, t_utc, hdr_data, sys, q_I in zip(range(len(ts)),ts,hdrs,syss,q_Is): 
            pif_uid = expt_id+'_'+str(int(t_utc))
            self.message_callback('making PIF {} / {} ({})'.format(ipif,npifs,pif_uid))
            pif_outputs = self.operations['make_pif'].run_with(
                experiment_id = expt_id,
                source_wavelength = src_wl,
                t_utc = t_utc,
                header_data = hdr_data,
                q_I = q_I, 
                system = sys 
                )
            all_pifs.append(pif_outputs['pif'])
        # SAVE AND UPLOAD THE PIFS
        pif_json_path = os.path.join(self.inputs['system_dir'],expt_id+'_pif.json') 
        self.operations['upload_pif'].run_with(
            pif = all_pifs,
            citrination_client = self.inputs['citrination_client'],
            dsid = self.inputs['dataset_id'],
            json_path = pif_json_path,
            keep_json = self.inputs['keep_pif_json'],
            upload_flag = self.inputs['upload_pif']
            )
        return self.outputs

