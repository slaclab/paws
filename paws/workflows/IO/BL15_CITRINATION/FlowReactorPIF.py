import os
import copy
from collections import OrderedDict

import numpy as np

from ...Workflow import Workflow 
from ...IO.BL15.ReadTimeSeries import ReadTimeSeries 
from ...INTEGRATION.Integrate import Integrate 
from ....operations.IO.YAML.SaveYAML import SaveYAML
from ....operations.IO.YAML.SaveXRSDSystem import SaveXRSDSystem
from ....operations.PROCESSING.BACKGROUND.BgSubtract import BgSubtract 
from ....operations.PROCESSING.FITTING.XRSDFit import XRSDFit 
from ....operations.PACKAGING.PIF.FlowSynthesisPIF import FlowSynthesisPIF
from ....operations.IO.CITRINATION.UploadPIF import UploadPIF

inputs = OrderedDict(
    integrator = None,          #
    citrination_client = None,  #
    experiment_id = 'test',     #
    bg_header_dir = None,       #
    bg_image_dir = None,        #
    rxn_header_dir = None,      #
    rxn_image_dir = None,       #
    data_dir = None,            #
    q_min = 0.,                 #
    q_max = 0.6,                #
    xrsd_system = None,         #
    q_range = [0.,float('inf')],#
    source_wavelength = None,   #
    design_goals = {},          #
    dataset_id = None,          #
    upload_pif = False,         #
    keep_pif_json = True        #
    )

outputs = OrderedDict()

class FlowReactorPIF(Workflow):
    
    def __init__(self):
        super(FlowReactorPIF,self).__init__(inputs,outputs)
        self.add_operations(
            read_bgs = ReadTimeSeries(),            #
            read_rxns = ReadTimeSeries(),           #
            integrate = Integrate(),                #
            subtract_bg = BgSubtract(),             #
            fit_xrsd = XRSDFit(),                   #
            save_xrsd_system = SaveXRSDSystem(),    #
            make_pif = FlowSynthesisPIF(),          #
            upload_pif = UploadPIF()                #
            )

    def run(self):
        rxn_id = self.inputs['experiment_id']
        src_wl = self.inputs['source_wavelength']
        # READ WHOLE TIMESERIES OF BACKGROUND IMAGE DATA 
        self.operations['read_bgs'].operations['read_batch'].operations['read'].disable_ops('read_q_I','read_system')
        bg_hdr_rx = rxn_id+'_bg*.yml'
        bg_data_batch = self.operations['read_bgs'].run_with(
            header_dir = self.inputs['bg_header_dir'],
            header_regex = bg_hdr_rx,
            image_dir = self.inputs['bg_image_dir'],
            image_suffix = '_0001' 
            )
        # READ WHOLE TIME SERIES OF REACTION IMAGE DATA
        self.operations['read_rxns'].operations['read_batch'].operations['read'].disable_ops('read_q_I','read_system')
        rxn_hdr_rx = rxn_id+'_*.yml'
        rxn_data_batch = self.operations['read_rxns'].run_with(
            header_dir = self.inputs['rxn_header_dir'],
            header_regex = rxn_hdr_rx,
            image_dir = self.inputs['rxn_image_dir'],
            image_suffix = '_0001' 
            )
        # INTEGRATE AND DE-ZINGER ALL IMAGES
        # TODO: IntegrateBatch
        q_Ibg_all = []
        q_Ibg_dz_all = []
        for imgd,outfn in zip(bg_data_batch['image_data'],bg_data_batch['filenames']):
            intgtr_outs = self.operations['integrate'].run_with(
                image_data = imgd,
                integrator = self.inputs['integrator'],
                q_min = self.inputs['q_min'],
                q_max = self.inputs['q_max'],
                output_dir = self.inputs['data_dir'],
                output_filename = outfn
                )
            q_Ibg_all.append(intgtr_outs['q_I'])
            q_Ibg_dz_all.append(intgtr_outs['q_I_dz'])
        q_Irxn_all = []
        q_Irxn_dz_all = []
        for imgd,outfn in zip(rxn_data_batch['image_data'],rxn_data_batch['filenames']):
            intgtr_outs = self.operations['integrate'].run_with(
                image_data = imgd,
                integrator = self.inputs['integrator'],
                q_min = self.inputs['q_min'],
                q_max = self.inputs['q_max'],
                output_dir = self.inputs['data_dir'],
                output_filename = outfn
                )
            q_Irxn_all.append(intgtr_outs['q_I'])
            q_Irxn_dz_all.append(intgtr_outs['q_I_dz'])
        # AVERAGE BG AND RXN PATTERNS
        # TODO: embed in operation
        self.message_callback('averaging intensities...')
        q_values = q_Ibg_dz_all[-1][:,0]
        Ibg_mean = np.mean(np.array([qIdz[:,1] for qIdz in q_Ibg_dz_all]),axis=0)
        Irxn_mean = np.mean(np.array([qIdz[:,1] for qIdz in q_Irxn_dz_all]),axis=0)
        q_Ibg_mean = np.array([q_values,Ibg_mean]).T
        q_Irxn_mean = np.array([q_values,Irxn_mean]).T
        # PERFORM BACKGROUND SUBTRACTIONS
        bgsub_data = self.operations['subtract_bg'].run_with(q_I = q_Irxn_mean, q_I_bg = q_Ibg_mean)
        q_I_dz_bgsub = bgsub_data['q_I_bgsub']
        # TODO: BgSubtractBatch
        #rxn_data_batch['q_I_dz_bgsub'] = []
        #for q_I_rxn, q_I_bg in zip(rxn_data_batch['q_I_dz'],bg_data_batch['q_I_dz']):
        #    bgsub_data = self.operations['subtract_bg'].run_with(
        #        q_I = q_I_rxn,
        #        q_I_bg = q_I_bg
        #        )
        #    rxn_data_batch['q_I_dz_bgsub'].append(bgsub_data['q_I_bgsub'])
        # FIT THE PARAMETERS, SAVE THE SYSTEM DEFINITION
        fit_outputs = self.operations['fit_xrsd'].run_with(
            q_I = q_I_dz_bgsub, source_wavelength = src_wl, system = self.inputs['xrsd_system'],
            error_weighted = True, logI_weighted = True, q_range = self.inputs['q_range']
            )
        #rxn_data_batch['xrsd_system'] = []
        #for irxn,q_I_data,fn in zip(range(nrxnx),rxn_data_batch['q_I_dz_bgsub'],rxn_data_batch['filenames']):
        #    fit_outputs = self.operations['fit_xrsd'].run_with(
        #        q_I = q_I_data,
        #        source_wavelength = src_wl,
        #        system = self.inputs['xrsd_system'],
        #        error_weighted = True,
        #        logI_weighted = True,
        #        q_range = self.inputs['q_range']
        #        )
        #    rxn_data_batch['xrsd_system'].append(fit_outputs['system'])
        xrsd_sys_file = os.path.join(self.inputs['data_dir'],rxn_id+'_xrsd_system.yml')
        self.operations['save_xrsd_system'].run_with(
            file_path = xrsd_sys_file,
            system = fit_outputs['system']
            )
        # CREATE PIF FOR THIS REACTION
        pif_outputs = self.operations['make_pif'].run_with(
            experiment_id = rxn_id,
            t_utc = rxn_data_batch['time'][-1],
            header_data = rxn_data_batch['header_data'][-1],
            design_goals = self.inputs['design_goals'],
            q_I = q_I_dz_bgsub, 
            system = fit_outputs['system'] 
            )
        # SAVE AND UPLOAD THE PIF
        pif_json_path = os.path.join(self.inputs['data_dir'],rxn_id+'_pif.json') 
        self.operations['upload_pif'].run_with(
            pif = pif_outputs['pif'],
            citrination_client = self.inputs['citrination_client'],
            dsid = self.inputs['dataset_id'],
            json_path = pif_json_path,
            keep_json = self.inputs['keep_pif_json'],
            upload_flag = self.inputs['upload_pif']
            )

        return self.outputs

