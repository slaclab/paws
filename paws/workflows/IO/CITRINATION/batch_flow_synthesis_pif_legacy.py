import os

from paws import pawstools
from paws.workflows.WfManager import WfManager

wfmgr = WfManager()
wfmgr.add_workflow('pif_batch')
wfmgr.load_operations('pif_batch',
    recipe_files='IO.FILESYSTEM.BuildFileList',
    pif_batch='EXECUTION.Batch',
    collect_pifs='PACKAGING.BATCH.ListFromBatch',
    output_file='IO.FILESYSTEM.BuildFilePath',
    upload_pif='IO.CITRINATION.UploadPIF'
    )

wfmgr.load_packaged_workflow('make_pif','CITRINATION.BL15.flow_synthesis_pif')
wfmgr.workflows['make_pif'].disable_op('save_pif')

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('citrination_client','CitrinationClient')

wf = wfmgr.workflows['pif_batch']

# input: header files location and regex
wf.connect_input('recipe_dir','recipe_files.inputs.dir_path') 
wf.connect_input('recipe_regex','recipe_files.inputs.regex') 
wf.connect_input('recipe_filter','recipe_files.inputs.filter_regex') 
# inputs: directories for finding image and data files 
#wf.connect_input('header_dir','pif_batch.inputs.static_inputs.header_dir')
#wf.connect_input('header_ext','pif_batch.inputs.static_inputs.header_ext')
#wf.connect_input('header_suffix','pif_batch.inputs.static_inputs.header_suffix')
#wf.connect_input('data_dir','pif_batch.inputs.static_inputs.data_dir')
#wf.connect_input('data_ext','pif_batch.inputs.static_inputs.data_ext')
#wf.connect_input('data_suffix','pif_batch.inputs.static_inputs.data_suffix')
#wf.connect_input('populations_dir','pif_batch.inputs.static_inputs.populations_dir')
#wf.connect_input('populations_ext','pif_batch.inputs.static_inputs.populations_ext')
#wf.connect_input('populations_suffix','pif_batch.inputs.static_inputs.populations_suffix')
wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect_input('keep_json','upload_pif.inputs.keep_json')
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')
wf.connect_input('output_dir','output_file.inputs.dir_path')
wf.connect_input('output_filename','output_file.inputs.filename')
wf.connect_output('pif','collect_pifs.outputs.data_list')

wf.connect_workflow('make_pif','pif_batch.inputs.work_item')
wf.connect('recipe_files.outputs.file_list','pif_batch.inputs.batch_inputs.recipe_path')

wf.connect('pif_batch.outputs.batch_outputs','collect_pifs.inputs.batch_outputs')
wf.set_op_inputs('collect_pifs',output_key='pif')

wf.set_op_inputs('output_file',extension='json',suffix='_PIF')
wf.connect('recipe_files.inputs.dir_path','output_file.inputs.dir_path')
wf.connect('collect_pifs.outputs.data_list','upload_pif.inputs.pif')
wf.connect('output_file.outputs.file_path','upload_pif.inputs.json_path')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','CITRINATION','batch_flow_synthesis_pif_legacy.wfm'))

