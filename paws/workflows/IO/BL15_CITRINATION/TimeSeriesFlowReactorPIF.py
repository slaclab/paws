import os
import copy
from collections import OrderedDict

import numpy as np

from ...Workflow import Workflow 
from ...IO.BL15.ReadTimeSeries import ReadTimeSeries 
from ....operations.PACKAGING.PIF.FlowSynthesisPIF import FlowSynthesisPIF
from ....operations.IO.CITRINATION.UploadPIF import UploadPIF

inputs = OrderedDict(
    citrination_client = None,
    experiment_id = 'test',
    source_wavelength = None,
    header_dir = None,
    header_suffix = None,
    header_regex = None,
    data_dir = None,
    q_I_suffix = None,
    system_suffix = None,
    #design_goals = {},
    dataset_id = None,
    upload_pif = False,
    keep_pif_json = True
    )

outputs = OrderedDict()

class TimeSeriesFlowReactorPIF(Workflow):
    
    def __init__(self):
        super(TimeSeriesFlowReactorPIF,self).__init__(inputs,outputs)
        self.add_operations(
            read = ReadTimeSeries(),
            make_pif = FlowSynthesisPIF(),
            upload_pif = UploadPIF()
            )

    def run(self):
        expt_id = self.inputs['experiment_id']
        src_wl = self.inputs['source_wavelength']
        # READ THE TIMESERIES 
        self.operations['read'].operations['read_batch'].operations['read'].disable_ops('read_image')
        ts_data = self.operations['read'].run_with(
            header_dir = self.inputs['header_dir'],
            q_I_dir = self.inputs['data_dir'], 
            system_dir = self.inputs['data_dir'], 
            header_regex = self.inputs['header_regex'],
            header_suffix = self.inputs['header_suffix'],
            q_I_suffix = self.inputs['q_I_suffix'],
            system_suffix = self.inputs['system_suffix']
            )
        # CREATE TIMESERIES OF PIFS
        all_pifs = []
        ts = ts_data['time']
        hdrs = ts_data['header_data']
        syss = ts_data['system']
        q_Is = ts_data['q_I']
        for ii, t_utc, hdr_data, sys, q_I in zip(range(len(ts)),ts,hdrs,syss,q_Is): 
            pif_outputs = self.operations['make_pif'].run_with(
                experiment_id = expt_id+'_{}'.format(ii),
                source_wavelength = src_wl,
                t_utc = t_utc,
                header_data = hdr_data,
                #design_goals = self.inputs['design_goals'],
                q_I = q_I, 
                system = sys 
                )
            all_pifs.append(pif_outputs['pif'])
        # SAVE AND UPLOAD THE PIFS
        pif_json_path = os.path.join(self.inputs['data_dir'],expt_id+'_pif.json') 
        self.operations['upload_pif'].run_with(
            pif = all_pifs,
            citrination_client = self.inputs['citrination_client'],
            dsid = self.inputs['dataset_id'],
            json_path = pif_json_path,
            keep_json = self.inputs['keep_pif_json'],
            upload_flag = self.inputs['upload_pif']
            )
        return self.outputs

