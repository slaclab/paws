import os
import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 
from paws.workflows.IO.BL15.ReadTimeSeries import ReadTimeSeries 
from paws.workflows.INTEGRATION.Integrate import Integrate 
from paws.operations.DAQ.BL15.SetFlowReactor import SetFlowReactor
from paws.operations.DAQ.BL15.ReadFlowReactor import ReadFlowReactor
from paws.operations.IO.YAML.SaveYAML import SaveYAML
from paws.operations.IO.YAML.SaveXRSDSystem import SaveXRSDSystem
from paws.operations.DAQ.BL15.MarCCD_SISExpose import MarCCD_SISExpose
from paws.operations.IO.FILESYSTEM.SSHCopy import SSHCopy
from paws.operations.PROCESSING.BACKGROUND.BgSubtract import BgSubtract 
from paws.operations.PROCESSING.FITTING.XRSDFit import XRSDFit 
from paws.operations.PACKAGING.PIF.FlowSynthesisPIF import FlowSynthesisPIF
from paws.operations.IO.CITRINATION.UploadPIF import UploadPIF

inputs = OrderedDict(
    flow_reactor = None,        #
    spec_infoclient = None,     #
    ssh_client = None,          #
    integrator = None,          #
    citrination_client = None,  #
    experiment_id = 'test',     #
    bg_recipe = {},             #
    rxn_recipe = {},            #
    n_bg_exposures = 1,         #
    n_rxn_exposures = 1,        #
    delay_volume = 0.,          #
    delay_time = 0.,            #
    exposure_time = 10.,        #
    recipe_output_dir = None,   #
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

class RunFlowReactor(Workflow):
    
    def __init__(self):
        super(RunFlowReactor,self).__init__(inputs,outputs)
        self.add_operations(
            set_recipe = SetFlowReactor(),          #
            read_flow_reactor = ReadFlowReactor(),  #
            save_recipe = SaveYAML(),               #
            save_header = SaveYAML(),               #
            expose_mar = MarCCD_SISExpose(),        #
            collect_file = SSHCopy(),               #
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
        freac = self.inputs['flow_reactor']
        rxn_id = self.inputs['experiment_id']
        src_wl = self.inputs['source_wavelength']
        exp_tm = self.inputs['exposure_time']
        # SET BACKGROUND RECIPE, DELAY, READ FLOWREACTOR, SAVE RECIPE DATA
        self.operations['set_recipe'].run_with(
            flow_reactor = freac,
            recipe = self.inputs['bg_recipe'],
            delay_time = self.inputs['delay_time'],
            delay_volume = self.inputs['delay_volume']
            )
        fr_stat = self.operations['read_flow_reactor'].run_with(flow_reactor=freac)
        bg_recipe_file = os.path.join(self.inputs['recipe_output_dir'],rxn_id+'_bg_recipe.yml')
        self.operations['save_recipe'].run_with(
            file_path = bg_recipe_file,
            data = fr_stat['recipe']
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
            bg_hdr.update(fr_stat['header'])
            self.operations['save_header'].run_with(
                file_path = bg_header_file,
                data = bg_hdr
                )
        # SET REACTION RECIPE, DELAY, READ FLOWREACTOR, SAVE RECIPE DATA
        self.operations['set_recipe'].run_with(
            flow_reactor = freac,
            recipe = self.inputs['rxn_recipe'],
            delay_time = self.inputs['delay_time'],
            delay_volume = self.inputs['delay_volume']
            )
        fr_stat = self.operations['read_flow_reactor'].run_with(flow_reactor=freac)
        rxn_recipe_file = os.path.join(self.inputs['recipe_output_dir'],rxn_id+'_recipe.yml')
        self.operations['save_recipe'].run_with(
            file_path = rxn_recipe_file,
            data = fr_stat['recipe']
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
        # COLLECT REACTION IMAGES AND HEADERS
        for irx in range(nrxnx):
            fn = rxn_id+'_{}_0001.tif'.format(irx)
            mar_path = '/home/data/'+fn
            local_path = os.path.join(self.inputs['rxn_image_dir'],fn)
            self.operations['collect_file'].run_with(
                ssh_client = self.inputs['ssh_client'],
                remote_path = mar_path,
                local_path = local_path
                ) 
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
        bg_data_batch['q_I'] = []
        bg_data_batch['q_I_dz'] = []
        for imgd,outfn in zip(bg_data_batch['image_data'],bg_data_batch['filenames']):
            intgtr_outs = self.operations['integrate'].run_with(
                image_data = imgd,
                integrator = self.inputs['integrator'],
                q_min = self.inputs['q_min'],
                q_max = self.inputs['q_max'],
                output_dir = self.inputs['data_dir'],
                output_filename = outfn
                )
            bg_data_batch['q_I'].append(intgtr_outs['q_I'])
            bg_data_batch['q_I_dz'].append(intgtr_outs['q_I_dz'])
        rxn_data_batch['q_I'] = []
        rxn_data_batch['q_I_dz'] = []
        for imgd,outfn in zip(rxn_data_batch['image_data'],rxn_data_batch['filenames']):
            intgtr_outs = self.operations['integrate'].run_with(
                image_data = imgd,
                integrator = self.inputs['integrator'],
                q_min = self.inputs['q_min'],
                q_max = self.inputs['q_max'],
                output_dir = self.inputs['data_dir'],
                output_filename = outfn
                )
            rxn_data_batch['q_I'].append(intgtr_outs['q_I'])
            rxn_data_batch['q_I_dz'].append(intgtr_outs['q_I_dz'])
        # PERFORM BACKGROUND SUBTRACTIONS
        # TODO: BgSubtractBatch
        rxn_data_batch['q_I_dz_bgsub'] = []
        for q_I_rxn, q_I_bg in zip(rxn_data_batch['q_I_dz'],bg_data_batch['q_I_dz']):
            bgsub_data = self.operations['subtract_bg'].run_with(
                q_I = q_I_rxn,
                q_I_bg = q_I_bg
                )
            rxn_data_batch['q_I_dz_bgsub'].append(bgsub_data['q_I_bgsub'])
        # FIT THE PARAMETERS, SAVE THE SYSTEM DEFINITION
        rxn_data_batch['xrsd_system'] = []
        for irxn,q_I_data,fn in zip(range(nrxnx),rxn_data_batch['q_I_dz_bgsub'],rxn_data_batch['filenames']):
            fit_outputs = self.operations['fit_xrsd'].run_with(
                q_I = q_I_data,
                source_wavelength = src_wl,
                system = self.inputs['xrsd_system'],
                error_weighted = True,
                logI_weighted = True,
                q_range = self.inputs['q_range']
                )
            rxn_data_batch['xrsd_system'].append(fit_outputs['system'])
            xrsd_sys_file = os.path.join(self.inputs['data_dir'],rxn_id+'_{}_xrsd_system.yml'.format(irxn))
            self.operations['save_xrsd_system'].run_with(
                file_path = xrsd_sys_file,
                system = fit_outputs['system']
                )
        # DUMP COLLECTED DATA TO REACTION HEADER FILE
        hdr_data = OrderedDict(
            experiment_id = rxn_id,
            t_utc = rxn_data_batch['time'][-1],
            recipe_setpoints = self.inputs['rxn_recipe'],
            )
        hdr_data.update(fr_stat['header'])
        rxn_hdr_path = os.path.join(self.inputs['rxn_header_dir'],rxn_id+'.yml')
        self.operations['save_header'].run_with(
            file_path = rxn_hdr_path,
            data = hdr_data
            )
        # CREATE PIF FOR THIS REACTION
        pif_outputs = self.operations['make_pif'].run_with(
            experiment_id = rxn_id,
            t_utc = rxn_data_batch['time'][-1],
            recipe = self.inputs['rxn_recipe'],
            header_data = fr_stat['header'],
            design_goals = self.inputs['design_goals'],
            q_I = rxn_data_batch['q_I_dz_bgsub'][-1],
            system = rxn_data_batch['xrsd_system'][-1]
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

#wf.connect('read_rxn_recipe.outputs.header','save_header.inputs.data.flow_reactor_header')
#wf.connect('read_rxn_recipe.outputs.recipe',[
#    'save_rxn_recipe.inputs.data',
#    'make_pif.inputs.recipe_readouts']
#    )
#wf.connect('read_bg_recipe.outputs.recipe','save_bg_recipe.inputs.data')
#wf.set_op_inputs('bg_recipe_file',suffix='_bg_recipe',extension='yml')
#wf.set_op_inputs('rxn_recipe_file',suffix='_recipe',extension='yml')
#wf.set_op_inputs('header_file',extension='yml')
#wf.set_op_input('pif_file','suffix','_pif')
#wf.set_op_input('pif_file','extension','json')
#wf.connect('bg_recipe_file.outputs.file_path','save_bg_recipe.inputs.file_path')
#wf.connect('rxn_recipe_file.outputs.file_path','save_rxn_recipe.inputs.file_path')
#wf.connect('header_file.outputs.file_path','save_header.inputs.file_path')

#wf.connect('expose_bg.outputs.batch_outputs.image_file','integrate_bg.inputs.batch_inputs.image_file')
#wf.connect('expose_rxn.outputs.batch_outputs.image_file','integrate_rxn.inputs.batch_inputs.image_file')

#wf.connect_workflow('bg_subtract','bg_subtract.inputs.work_item')
#wf.connect('integrate_rxn.outputs.batch_outputs.q_I_dz','bg_subtract.inputs.batch_inputs.q_I')
#wf.connect('integrate_bg.outputs.batch_outputs.q_I_dz.-1','bg_subtract.inputs.static_inputs.q_I_bg')
#wf.connect('integrate_rxn.outputs.batch_outputs.q_I_dz_filename','bg_subtract.inputs.batch_inputs.output_filename')

#wf.connect('bg_subtract.outputs.batch_outputs.q_I_bgsub','fit.inputs.batch_inputs.q_I')
#wf.connect('bg_subtract.outputs.batch_outputs.q_I_filename','fit.inputs.batch_inputs.output_filename')

#wf.connect('read_rxn_recipe.outputs.header.t_utc','make_pif.inputs.t_utc')

#wf.connect('pif_file.outputs.file_path','conditional_upload.inputs.inputs.json_path')



#wf.connect('header_file.outputs.file_path','make_pif.inputs.header_file')
#wf.connect('rxn_recipe_file.outputs.file_path','make_pif.inputs.recipe_file')
#wf.connect('integrate_rxn.outputs.batch_outputs.q_I_file.-1','make_pif.inputs.q_I_file')
#wf.connect('bg_subtract.outputs.batch_outputs.q_I_file.-1','make_pif.inputs.q_I_file')
#wf.connect('fit.outputs.batch_outputs.output_file.-1','make_pif.inputs.system_file')

#wf.connect('fit.outputs.batch_outputs.system_opt_dict.-1.particle.parameters.I0.value',
#    'check_intensity.inputs.data')
#wf.connect('fit.outputs.batch_outputs.system_opt_dict.-1.fit_report.final_objective',
#    'check_fit_objective.inputs.data')
#wf.set_op_input('check_intensity','comparison_value',min_particle_I0)
#wf.set_op_input('check_fit_objective','comparison_value',max_fit_obj)

#wf.connect_input('bg_recipe','set_bg_recipe.inputs.recipe')
#wf.connect_input('rxn_recipe',[
#    'set_rxn_recipe.inputs.recipe',
#    'make_pif.inputs.recipe_setpoints']
#    )
#wf.connect_input('delay_volume',[
#    'set_bg_recipe.inputs.delay_volume',
#    'set_rxn_recipe.inputs.delay_volume']
#    )
#wf.connect_input('delay_time',[
#    'set_bg_recipe.inputs.delay_time',
#    'set_rxn_recipe.inputs.delay_time']
#    )
#wf.connect_input('recipe_filename',[
#    'bg_recipe_file.inputs.filename',
#    'rxn_recipe_file.inputs.filename',
#    'header_file.inputs.filename',
#    'pif_file.inputs.filename']
#    )
#wf.connect_input('output_dir',[
#    'bg_recipe_file.inputs.dir_path',
#    'rxn_recipe_file.inputs.dir_path',
#    'header_file.inputs.dir_path',
#    'pif_file.inputs.dir_path']
#    )
#wf.connect_input('bg_filenames',[
#    'expose_bg.inputs.batch_inputs.filename',
#    'integrate_bg.inputs.batch_inputs.filename']
#    )
#wf.connect_input('rxn_filenames',[
#    'expose_rxn.inputs.batch_inputs.filename',
#    'integrate_rxn.inputs.batch_inputs.filename']
#    )

#wf.connect_input('exposure_time',[
#    'expose_bg.inputs.static_inputs.exposure_time',
#    'expose_rxn.inputs.static_inputs.exposure_time',
#    'save_header.inputs.data.exposure_time']
#    )
#wf.connect_input('output_dir',[
#    'expose_bg.inputs.static_inputs.output_dir',
#    'expose_rxn.inputs.static_inputs.output_dir']
#    )
#wf.connect_input('source_wavelength',[
#    'fit.inputs.static_inputs.source_wavelength',
#    'save_header.inputs.data.source_wavelength']
#    )
#wf.connect_input('mar_file_suffix',[
#    'expose_bg.inputs.static_inputs.file_suffix',
#    'expose_rxn.inputs.static_inputs.file_suffix']
#    )
#wf.connect_input('q_min',[
#    'integrate_bg.inputs.static_inputs.q_min',
#    'integrate_rxn.inputs.static_inputs.q_min']
#    )
#wf.connect_input('q_max',[
#    'integrate_bg.inputs.static_inputs.q_max',
#    'integrate_rxn.inputs.static_inputs.q_max']
#    )
#wf.connect_input('output_dir',[
#    'integrate_bg.inputs.static_inputs.output_dir',
#    'integrate_rxn.inputs.static_inputs.output_dir']
#    )
#wf.connect_input('output_dir','bg_subtract.inputs.static_inputs.output_dir')
#wf.connect_input('system','fit.inputs.static_inputs.system')
#wf.connect_input('q_range','fit.inputs.static_inputs.q_range')
#wf.connect_input('output_dir','fit.inputs.static_inputs.output_dir')
#wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
#wf.connect_input('design_goals','make_pif.inputs.design_goals')
#wf.connect_input('dataset_id','conditional_upload.inputs.inputs.dsid')
#wf.connect_input('upload_pif_flag','conditional_upload.inputs.inputs.upload_flag')
#wf.connect_input('keep_pif_json','conditional_upload.inputs.inputs.keep_json')
#wf.connect('bg_subtract.outputs.batch_outputs.q_I_bgsub.-1','make_pif.inputs.q_I')
#wf.connect('fit.outputs.batch_outputs.system_opt.-1','make_pif.inputs.system')


#wfmgr.load_operations('flow_reactor_pipeline',
    #header_file = 'IO.FILESYSTEM.BuildFilePath',
    #bg_recipe_file = 'IO.FILESYSTEM.BuildFilePath',
    #expose_bg = 'EXECUTION.Batch',
    #integrate_bg = 'EXECUTION.Batch',
    #rxn_recipe_file = 'IO.FILESYSTEM.BuildFilePath',
    #expose_rxn = 'EXECUTION.Batch',
    #integrate_rxn = 'EXECUTION.Batch',
    #bg_subtract = 'EXECUTION.Batch',
    #fit = 'EXECUTION.Batch',
    #pif_file = 'IO.FILESYSTEM.BuildFilePath',
    #check_intensity = 'PROCESSING.BASIC.Compare',
    #check_fit_objective = 'PROCESSING.BASIC.Compare',
    #conditional_upload = 'EXECUTION.MultiConditional',
#    )

#wf.set_dependency('set_bg_recipe','bg_recipe_file')
#wf.set_dependency('expose_bg','set_bg_recipe')
#wf.set_dependency('read_bg_recipe','expose_bg')
#wf.set_dependency('set_rxn_recipe','integrate_bg')
#wf.set_dependency('expose_rxn','set_rxn_recipe')
#wf.set_dependency('read_rxn_recipe','expose_rxn')
#wf.set_dependency('bg_subtract','expose_rxn')
#wf.set_dependency('fit','bg_subtract')
#wf.set_dependency('save_header','fit')
#wf.set_dependency('make_pif','save_header')

#wf.connect_plugin('flow_reactor',[
#    'set_bg_recipe.inputs.flow_reactor',
#    'set_rxn_recipe.inputs.flow_reactor',
#    'read_bg_recipe.inputs.flow_reactor',
#    'read_rxn_recipe.inputs.flow_reactor']
#    )
#wf.connect_plugin('citrination_client','conditional_upload.inputs.inputs.citrination_client')

#wf.connect('upload_pif','conditional_upload.inputs.work_item')
#wf.disable_op('upload_pif')
#wf.connect('check_intensity.outputs.is_greater','conditional_upload.inputs.conditions.0')
#wf.connect('check_fit_objective.outputs.is_lesser','conditional_upload.inputs.conditions.1')
#wf.set_op_input('conditional_upload.inputs.run_conditions',[True,True])

#wf.connect('make_pif.outputs.pif','conditional_upload.inputs.inputs.pif')

