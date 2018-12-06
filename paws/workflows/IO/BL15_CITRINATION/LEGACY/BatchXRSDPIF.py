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
    upload_data = False,
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
        q_I_files = ts_data['q_I_files']
        npifs = len(ts)
        for ipif, t_utc, hdr_data, sys, q_I, q_I_file in zip(range(len(ts)),ts,hdrs,syss,q_Is,q_I_files): 
            self.message_callback('making PIF {} / {} ({})'.format(ipif,npifs,sys.sample_metadata['sample_id']))
            pif_outputs = self.operations['make_pif'].run_with(
                system = sys,
                q_I = None, 
                q_I_file = os.path.split(q_I_file)[1], 
                t_utc = t_utc,
                temperature = hdr_data['temperature'],
                source_wavelength = src_wl
                )
            all_pifs.append(pif_outputs['pif'])
        # UPLOAD THE q_I DATA FILES
        if self.inputs['upload_data']:
            for ifp, fp in enumerate(q_I_files):
                fn = os.path.split(fp)[1]
                self.message_callback('Uploading data file {} / {} ({})'.format(ifp,npifs,fn))
                self.inputs['citrination_client'].client.upload(self.inputs['dataset_id'],fp,fn)
        # SAVE AND UPLOAD THE PIFS
        pif_json_path = os.path.join(self.inputs['system_dir'],'pif.json') 
        self.operations['upload_pif'].run_with(
            pif = all_pifs,
            citrination_client = self.inputs['citrination_client'],
            dsid = self.inputs['dataset_id'],
            json_path = pif_json_path,
            keep_json = self.inputs['keep_pif_json'],
            upload_flag = self.inputs['upload_pif']
            )
        return self.outputs

