import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wf = wfmgr.add_workflow('flow_reactor_pipeline')

wfmgr.load_operations('flow_reactor_pipeline',
    header_file = 'IO.FILESYSTEM.BuildFilePath',
    set_bg_recipe = 'DAQ.BL15.SetFlowReactor',
    bg_recipe_file = 'IO.FILESYSTEM.BuildFilePath',
    expose_bg = 'EXECUTION.Batch',
    read_bg_recipe = 'DAQ.BL15.ReadFlowReactor',
    save_bg_recipe = 'IO.YAML.SaveYAML',
    integrate_bg = 'EXECUTION.Batch',
    set_rxn_recipe = 'DAQ.BL15.SetFlowReactor',
    rxn_recipe_file = 'IO.FILESYSTEM.BuildFilePath',
    save_rxn_recipe = 'IO.YAML.SaveYAML',
    expose_rxn = 'EXECUTION.Batch',
    read_rxn_recipe = 'DAQ.BL15.ReadFlowReactor',
    integrate_rxn = 'EXECUTION.Batch',
    bg_subtract = 'EXECUTION.Batch',
    fit = 'EXECUTION.Batch',
    save_header = 'IO.YAML.SaveYAML',
    pif_file = 'IO.FILESYSTEM.BuildFilePath',
    make_pif = 'PACKAGING.PIF.FlowSynthesisPIF',
    upload_pif = 'IO.CITRINATION.UploadPIF'
    )

wfmgr.load_packaged_wfm('DAQ.BL15.mar_expose')
wfmgr.load_packaged_wfm('INTEGRATION.integrate')
wfmgr.load_packaged_workflow('bg_subtract','BACKGROUND.bg_subtract')
wfmgr.workflows['bg_subtract'].disable_ops('read_q_I','read_q_I_bg')
wfmgr.load_packaged_workflow('fit_xrsd','FITTING.fit_xrsd')
wfmgr.workflows['fit_xrsd'].disable_ops('read_q_I')

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugins(
    timer='Timer',
    cryocon='CryoConController', 
    flow_reactor='FlowReactor',
    citrination_client='CitrinationClient'
    )
pgmgr.connect('timer',[
    'cryocon.inputs.timer',
    'flow_reactor.inputs.timer',
    'spec_infoclient.inputs.timer',
    'mar_ssh_client.inputs.timer']
    )
pgmgr.connect('cryocon','flow_reactor.inputs.cryocon')

wf.set_dependency('set_bg_recipe','bg_recipe_file')
wf.set_dependency('expose_bg','set_bg_recipe')
wf.set_dependency('read_bg_recipe','expose_bg')
wf.set_dependency('set_rxn_recipe','integrate_bg')
wf.set_dependency('expose_rxn','set_rxn_recipe')
wf.set_dependency('read_rxn_recipe','expose_rxn')
wf.set_dependency('bg_subtract','expose_rxn')
wf.set_dependency('fit','bg_subtract')
wf.set_dependency('save_header','fit')
wf.set_dependency('make_pif','save_header')

wf.connect_input('bg_recipe','set_bg_recipe.inputs.recipe')
wf.connect_input('rxn_recipe','set_rxn_recipe.inputs.recipe')
wf.connect_plugin('flow_reactor',[
    'set_bg_recipe.inputs.flow_reactor',
    'set_rxn_recipe.inputs.flow_reactor',
    'read_bg_recipe.inputs.flow_reactor',
    'read_rxn_recipe.inputs.flow_reactor']
    )
wf.connect_input('delay_volume',[
    'set_bg_recipe.inputs.delay_volume',
    'set_rxn_recipe.inputs.delay_volume']
    )
wf.connect_input('delay_time',[
    'set_bg_recipe.inputs.delay_time',
    'set_rxn_recipe.inputs.delay_time']
    )
wf.connect_input('recipe_filename',[
    'bg_recipe_file.inputs.filename',
    'rxn_recipe_file.inputs.filename',
    'header_file.inputs.filename',
    'pif_file.inputs.filename']
    )
wf.connect_input('output_dir',[
    'bg_recipe_file.inputs.dir_path',
    'rxn_recipe_file.inputs.dir_path',
    'header_file.inputs.dir_path',
    'pif_file.inputs.dir_path']
    )

wf.connect('read_rxn_recipe.outputs.header','save_header.inputs.data.flow_reactor_header')
wf.connect('read_rxn_recipe.outputs.recipe','save_rxn_recipe.inputs.data')
wf.connect('read_bg_recipe.outputs.recipe','save_bg_recipe.inputs.data')
wf.set_op_inputs('bg_recipe_file',suffix='_bg_recipe',extension='yml')
wf.set_op_inputs('rxn_recipe_file',suffix='_recipe',extension='yml')
wf.set_op_inputs('header_file',extension='yml')
wf.set_op_input('pif_file','suffix','_pif')
wf.set_op_input('pif_file','extension','json')
wf.connect('bg_recipe_file.outputs.file_path','save_bg_recipe.inputs.file_path')
wf.connect('rxn_recipe_file.outputs.file_path','save_rxn_recipe.inputs.file_path')
wf.connect('header_file.outputs.file_path','save_header.inputs.file_path')

wf.connect_workflow('run_exposure',[
    'expose_bg.inputs.work_item',
    'expose_rxn.inputs.work_item']
    )
wf.connect_input('bg_filenames',[
    'expose_bg.inputs.batch_inputs.filename',
    'integrate_bg.inputs.batch_inputs.filename']
    )
wf.connect_input('rxn_filenames',[
    'expose_rxn.inputs.batch_inputs.filename',
    'integrate_rxn.inputs.batch_inputs.filename']
    )

wf.connect_input('exposure_time',[
    'expose_bg.inputs.static_inputs.exposure_time',
    'expose_rxn.inputs.static_inputs.exposure_time',
    'save_header.inputs.data.exposure_time']
    )
wf.connect_input('output_dir',[
    'expose_bg.inputs.static_inputs.output_dir',
    'expose_rxn.inputs.static_inputs.output_dir']
    )
wf.connect_input('source_wavelength',[
    'fit.inputs.static_inputs.source_wavelength',
    'save_header.inputs.data.source_wavelength']
    )
wf.connect_input('mar_file_suffix',[
    'expose_bg.inputs.static_inputs.file_suffix',
    'expose_rxn.inputs.static_inputs.file_suffix']
    )

wf.connect_workflow('integrate',[
    'integrate_bg.inputs.work_item',
    'integrate_rxn.inputs.work_item']
    )
wf.connect('expose_bg.outputs.batch_outputs.image_file','integrate_bg.inputs.batch_inputs.image_file')
wf.connect('expose_rxn.outputs.batch_outputs.image_file','integrate_rxn.inputs.batch_inputs.image_file')
wf.connect_input('q_min',[
    'integrate_bg.inputs.static_inputs.q_min',
    'integrate_rxn.inputs.static_inputs.q_min']
    )
wf.connect_input('q_max',[
    'integrate_bg.inputs.static_inputs.q_max',
    'integrate_rxn.inputs.static_inputs.q_max']
    )
wf.connect_input('output_dir',[
    'integrate_bg.inputs.static_inputs.output_dir',
    'integrate_rxn.inputs.static_inputs.output_dir']
    )

wf.connect_workflow('bg_subtract','bg_subtract.inputs.work_item')
wf.connect('integrate_rxn.outputs.batch_outputs.q_I_dz','bg_subtract.inputs.batch_inputs.q_I')
wf.connect('integrate_bg.outputs.batch_outputs.q_I_dz.-1','bg_subtract.inputs.static_inputs.q_I_bg')
wf.connect('integrate_rxn.outputs.batch_outputs.q_I_dz_filename','bg_subtract.inputs.batch_inputs.output_filename')
wf.connect_input('output_dir','bg_subtract.inputs.static_inputs.output_dir')

wf.connect_workflow('fit_xrsd','fit.inputs.work_item')
wf.connect('bg_subtract.outputs.batch_outputs.q_I_bgsub','fit.inputs.batch_inputs.q_I')
wf.connect('bg_subtract.outputs.batch_outputs.q_I_filename','fit.inputs.batch_inputs.output_filename')
wf.connect_input('system','fit.inputs.static_inputs.system')
wf.connect_input('q_range','fit.inputs.static_inputs.q_range')
wf.connect_input('output_dir','fit.inputs.static_inputs.output_dir')

wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
wf.connect('header_file.outputs.file_path','make_pif.inputs.header_file')
wf.connect('rxn_recipe_file.outputs.file_path','make_pif.inputs.recipe_file')
#wf.connect('integrate_rxn.outputs.batch_outputs.q_I_file.-1','make_pif.inputs.q_I_file')
wf.connect('bg_subtract.outputs.batch_outputs.q_I_file.-1','make_pif.inputs.q_I_file')
wf.connect('fit.outputs.batch_outputs.output_file.-1','make_pif.inputs.system_file')

wf.connect('make_pif.outputs.pif','upload_pif.inputs.pif')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')
wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect('pif_file.outputs.file_path','upload_pif.inputs.json_path')
wf.connect_input('keep_pif_flag','upload_pif.inputs.keep_json')
wf.connect_input('upload_pif_flag','upload_pif.inputs.upload_flag')
wf.set_op_inputs('upload_pif',keep_json=True,upload_flag=False)

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','flow_reactor_pipeline.wfm'))

