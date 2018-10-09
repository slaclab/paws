import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('main')

wfmgr.load_packaged_wfm('DAQ.BL15.run_flow_reactor')
wfmgr.load_packaged_wfm('INTEGRATION.BL15.integrate')
wfmgr.load_packaged_workflow('bg_subtract','BACKGROUND.bg_subtract')
wfmgr.load_packaged_workflow('fit','FITTING.BL15.read_and_fit')

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugins(citrination_client='CitrinationClient')

wfmgr.load_operations('main',
    run_recipe = 'EXECUTION.Run',
    run_integrate = 'EXECUTION.Run',
    select_bg = 'PACKAGING.NearestYValue',
    run_bgsub = 'EXECUTION.Run',
    system_file = 'IO.FILESYSTEM.BuildFilePath',
    run_fit = 'EXECUTION.Run',
    make_pif = 'PACKAGING.PIF.FlowSynthesisPIF',
    pif_file = 'IO.FILESYSTEM.BuildFilePath',
    upload_pif = 'IO.CITRINATION.UploadPIF')

wf = wfmgr.workflows['main']
wf.connect_workflow('run_reactor','run_recipe.inputs.work_item')
wf.connect_input('recipe','run_recipe.inputs.inputs.recipe')
wf.connect_input('delay_volume','run_recipe.inputs.inputs.delay_volume')
wf.connect_input('delay_time','run_recipe.inputs.inputs.delay_time')
wf.connect_input('filename_root',[\
    'run_recipe.inputs.inputs.filename_root',
    'system_file.inputs.filename',
    'pif_file.inputs.filename']
    )
wf.connect_input('exposure_time','run_recipe.inputs.inputs.exposure_time')
wf.connect_input('source_wavelength',[\
    'run_recipe.inputs.inputs.source_wavelength',
    'run_fit.inputs.inputs.source_wavelength']
    )
wf.connect_input('output_dir',[\
    'run_recipe.inputs.inputs.output_dir',
    'system_file.inputs.dir_path',
    'pif_file.inputs.dir_path']
    )

#wf.connect_input('calib_file','run_integrate.inputs.inputs.calib_file')
wf.connect_workflow('integrate','run_integrate.inputs.work_item')
wf.connect('run_recipe.outputs.outputs.header_file','run_integrate.inputs.inputs.header_file')
#wf.set_dependency('run_integrate','run_recipe')

wf.connect_input('bg_files_vs_T','select_bg.inputs.x_y')
wf.connect('run_recipe.outputs.outputs.T_sample','select_bg.inputs.x_value')
#wf.connect_input('x_value','run_recipe.outputs.outputs.T_sample')
# direct connection to bg file for skipping nearest-y approach
#wf.connect_input('q_I_bg','select_bg.outputs.nearest_y')

wf.connect_workflow('bg_subtract','run_bgsub.inputs.work_item')
wf.connect('select_bg.outputs.nearest_y','run_bgsub.inputs.inputs.bg_file')
wf.connect('run_integrate.outputs.outputs.q_I_dz_file','run_bgsub.inputs.inputs.data_file')

wf.set_op_input('system_file','suffix','_sys')
wf.set_op_input('system_file','extension','yml')

wf.connect_workflow('fit','run_fit.inputs.work_item')
wf.connect('system_file.outputs.file_path','run_fit.inputs.inputs.system_file')

wf.connect('run_bgsub.outputs.outputs.q_I_file','run_fit.inputs.inputs.data_filepath')

wf.connect_input('system','run_fit.inputs.inputs.system')

wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
wf.connect('run_recipe.outputs.outputs.header_file','make_pif.inputs.header_file')
wf.connect('run_recipe.outputs.outputs.recipe_file','make_pif.inputs.recipe_file')
wf.connect('run_bgsub.outputs.outputs.q_I_file','make_pif.inputs.q_I_file')
wf.connect('run_fit.outputs.outputs.system_file','make_pif.inputs.system_file')

wf.set_op_inputs('pif_file',suffix='_pif',extension='json')

wf.connect('make_pif.outputs.pif','upload_pif.inputs.pif')
wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')
wf.connect('pif_file.outputs.file_path','upload_pif.inputs.json_path')
wf.connect_input('save_pif_flag','upload_pif.inputs.keep_json')
wf.set_op_inputs('upload_pif',keep_json=True,upload_flag=True)
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','run_flow_integrate_bgsub_fit_pif.wfm'))


