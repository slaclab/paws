import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('make_pif')
wfmgr.load_operations('make_pif',
    make_pif='PACKAGING.PIF.FlowSynthesisPIF',
    pif_file='IO.FILESYSTEM.BuildFilePath',
    upload_pif='IO.CITRINATION.UploadPIF'
    )
pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('citrination_client','CitrinationClient')

wf = wfmgr.workflows['make_pif']

wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
wf.connect_input('recipe_file','make_pif.inputs.recipe_file')
wf.connect_input('header_file','make_pif.inputs.header_file')
wf.connect_input('q_I_file','make_pif.inputs.q_I_file')
wf.connect_input('populations_file','make_pif.inputs.populations_file')
wf.connect_output('pif','make_pif.outputs.pif')

wf.connect_input('output_dir','pif_file.inputs.dir_path')
wf.connect_input('output_filename','pif_file.inputs.filename')
wf.connect('make_pif.outputs.header_dir_path','pif_file.inputs.dir_path')
wf.connect('make_pif.outputs.header_filename','pif_file.inputs.filename')
wf.set_op_inputs('pif_file',suffix='_pif',extension='json')

wf.connect('make_pif.outputs.pif','upload_pif.inputs.pif')
wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')
wf.connect('pif_file.outputs.file_path','upload_pif.inputs.json_path')
wf.connect_input('keep_json','upload_pif.inputs.keep_json')
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','CITRINATION','flow_synthesis_pif.wfm'))

