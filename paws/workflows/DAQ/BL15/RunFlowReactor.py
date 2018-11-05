import os
import copy
from collections import OrderedDict

import numpy as np

from ...Workflow import Workflow 
from ...IO.BL15.ReadTimeSeries import ReadTimeSeries 
from ...INTEGRATION.Integrate import Integrate 
from ....operations.DAQ.BL15.SetFlowReactor import SetFlowReactor
from ....operations.DAQ.BL15.ReadFlowReactor import ReadFlowReactor
from ....operations.IO.YAML.SaveYAML import SaveYAML
from ....operations.IO.YAML.SaveXRSDSystem import SaveXRSDSystem
from ....operations.DAQ.BL15.MarCCD_SISExpose import MarCCD_SISExpose
from ....operations.IO.FILESYSTEM.SSHCopy import SSHCopy
from ....operations.PROCESSING.BACKGROUND.BgSubtract import BgSubtract 
from ....operations.PROCESSING.FITTING.XRSDFit import XRSDFit 
from ....operations.PACKAGING.PIF.FlowSynthesisPIF import FlowSynthesisPIF
from ....operations.IO.CITRINATION.UploadPIF import UploadPIF

inputs = OrderedDict(
    flow_reactor = None,        #
    spec_infoclient = None,     #
    ssh_client = None,          #
    source_wavelength = None,   #
    experiment_id = 'test',     #
    bg_recipe = {},             #
    rxn_recipe = {},            #
    n_bg_exposures = 1,         #
    n_rxn_exposures = 1,        #
    delay_volume = 0.,          #
    delay_time = 0.,            #
    exposure_time = 10.,        #
    bg_header_dir = None,       #
    bg_image_dir = None,        #
    rxn_header_dir = None,      #
    rxn_image_dir = None,       #
    stop_reactor = True         #
    )

outputs = OrderedDict()

class RunFlowReactor(Workflow):
    
    def __init__(self):
        super(RunFlowReactor,self).__init__(inputs,outputs)
        self.add_operations(
            set_recipe = SetFlowReactor(),          #
            read_flow_reactor = ReadFlowReactor(),  #
            save_recipe = SaveYAML(),               #
            save_header = SaveYAML(),               #
            expose_mar = MarCCD_SISExpose(),        #
            collect_file = SSHCopy()                #
            )

    def run(self):
        freac = self.inputs['flow_reactor']
        rxn_id = self.inputs['experiment_id']
        src_wl = self.inputs['source_wavelength']
        exp_tm = self.inputs['exposure_time']
        # SET BACKGROUND RECIPE, DELAY
        self.operations['set_recipe'].run_with(
            flow_reactor = freac,
            recipe = self.inputs['bg_recipe'],
            delay_time = self.inputs['delay_time'],
            delay_volume = self.inputs['delay_volume']
            )
        # EXPOSE BACKGROUND IMAGES, READ FLOWREACTOR, SAVE HEADER DATA
        nbgx = self.inputs['n_bg_exposures']
        for ibg in range(nbgx):
            bg_fn_root = rxn_id+'_bg{}'.format(ibg) 
            self.operations['expose_mar'].run_with(
                spec_infoclient = self.inputs['spec_infoclient'],
                exposure_time = exp_tm,
                filename = bg_fn_root 
                )
            fr_stat = self.operations['read_flow_reactor'].run_with(flow_reactor=freac)
            bg_header_file = os.path.join(self.inputs['bg_header_dir'],bg_fn_root+'.yml')
            bg_hdr = OrderedDict(exposure_time=exp_tm,source_wavelength=src_wl) 
            bg_hdr.update(self.inputs['bg_recipe']),
            bg_hdr.update(fr_stat['header'])
            self.operations['save_header'].run_with(
                file_path = bg_header_file,
                data = bg_hdr
                )
        # SET REACTION RECIPE, DELAY
        self.operations['set_recipe'].run_with(
            flow_reactor = freac,
            recipe = self.inputs['rxn_recipe'],
            delay_time = self.inputs['delay_time'],
            delay_volume = self.inputs['delay_volume']
            )
        # EXPOSE REACTION IMAGES, READ FLOWREACTOR, SAVE HEADER DATA
        nrxnx = self.inputs['n_rxn_exposures']
        for irx in range(nrxnx):
            rxn_fn_root = rxn_id+'_{}'.format(irx) 
            self.operations['expose_mar'].run_with(
                spec_infoclient = self.inputs['spec_infoclient'],
                exposure_time = exp_tm,
                filename = rxn_fn_root 
                )
            fr_stat = self.operations['read_flow_reactor'].run_with(flow_reactor=freac)
            rxn_header_file = os.path.join(self.inputs['rxn_header_dir'],rxn_fn_root+'.yml')
            rxn_hdr = OrderedDict(exposure_time=exp_tm,source_wavelength=src_wl)
            rxn_hdr.update(self.inputs['rxn_recipe']),
            rxn_hdr.update(fr_stat['header'])
            self.operations['save_header'].run_with(
                file_path = rxn_header_file,
                data = rxn_hdr
                )
        # COLLECT BACKGROUND IMAGES
        for ibg in range(nbgx):
            fn = rxn_id+'_bg{}_0001.tif'.format(ibg)
            mar_path = '/home/data/'+fn
            local_path = os.path.join(self.inputs['bg_image_dir'],fn)
            self.operations['collect_file'].run_with(
                ssh_client = self.inputs['ssh_client'],
                remote_path = mar_path,
                local_path = local_path
                ) 
        # COLLECT REACTION IMAGES
        for irx in range(nrxnx):
            fn = rxn_id+'_{}_0001.tif'.format(irx)
            mar_path = '/home/data/'+fn
            local_path = os.path.join(self.inputs['rxn_image_dir'],fn)
            self.operations['collect_file'].run_with(
                ssh_client = self.inputs['ssh_client'],
                remote_path = mar_path,
                local_path = local_path
                )

        # STOP THE FLOW REACTOR
        if self.inputs['stop_reactor']: freac.stop()
        return self.outputs

