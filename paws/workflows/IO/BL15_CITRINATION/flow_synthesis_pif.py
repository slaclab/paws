import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_workflow('read','IO.BL15.read')
wfmgr.load_operations('read',
    recipe_file='IO.FILESYSTEM.BuildFilePath',
    read_recipe='IO.YAML.LoadYAML'
    )
read_wf = wfmgr.workflows['read']
read_wf.disable_op('read_image')
read_wf.enable_op('read_system')

read_wf.connect_input('recipe_dir','recipe_file.inputs.dir_path')
read_wf.connect_input('recipe_suffix','recipe_file.inputs.suffix')
read_wf.connect_input('recipe_ext','recipe_file.inputs.extension')
read_wf.connect('read_header.outputs.filename','recipe_file.inputs.filename')
read_wf.connect_output('recipe_file','recipe_file.outputs.file_path')
read_wf.set_op_input('recipe_file','extension','yml')

read_wf.connect('recipe_file.outputs.file_path','read_recipe.inputs.file_path')
read_wf.connect_output('recipe','read_recipe.outputs.data')

wfmgr.add_workflow('pif')
wfmgr.load_operations('pif',
    read='EXECUTION.Run',
    make_pif='PACKAGING.PIF.FlowSynthesisPIF',
    pif_file='IO.FILESYSTEM.BuildFilePath',
    upload_pif='IO.CITRINATION.UploadPIF'
    )
pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('citrination_client','CitrinationClient')

wf = wfmgr.workflows['pif']

wf.connect_input('header_file','read.inputs.inputs.header_file')
wf.connect_workflow('read','read.inputs.work_item')

wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
wf.connect('read.outputs.outputs.recipe','make_pif.inputs.recipe')
wf.connect('read.outputs.outputs.header_data','make_pif.inputs.header_data')
wf.connect('read.outputs.outputs.q_I','make_pif.inputs.q_I')
wf.connect('read.outputs.outputs.system','make_pif.inputs.system')
wf.connect_output('pif','make_pif.outputs.pif')

wf.connect_input('output_dir','pif_file.inputs.dir_path')
wf.connect_input('output_filename','pif_file.inputs.filename')
wf.set_op_inputs('pif_file',suffix='_pif',extension='json')

wf.connect('make_pif.outputs.pif','upload_pif.inputs.pif')
wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')
wf.connect('pif_file.outputs.file_path','upload_pif.inputs.json_path')
wf.connect_input('keep_json','upload_pif.inputs.keep_json')
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15_CITRINATION','flow_synthesis_pif.wfm'))

