import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_wfm('IO.BL15_CITRINATION.flow_synthesis_pif')
wfmgr.workflows['pif'].disable_op('pif_file')
wfmgr.workflows['pif'].disable_op('upload_pif')

wfmgr.add_workflow('batch_pif')
wfmgr.load_operations('batch_pif',
    header_files='IO.FILESYSTEM.BuildFileList',
    batch='EXECUTION.Batch',
    pif_file='IO.FILESYSTEM.BuildFilePath',
    upload_pif='IO.CITRINATION.UploadPIF'
    )

wf = wfmgr.workflows['batch_pif']

wf.connect_input('header_dir','header_files.inputs.dir_path') 
wf.connect_input('header_regex','header_files.inputs.regex') 

wf.connect_input('experiment_id','batch.inputs.static_inputs.experiment_id')
wf.connect_workflow('pif','batch.inputs.work_item')
wf.connect('header_files.outputs.file_list','batch.inputs.batch_inputs.header_file')

wf.connect_input('output_dir','pif_file.inputs.dir_path')
wf.connect_input('output_filename','pif_file.inputs.filename')
wf.set_op_inputs('pif_file',suffix='_pif',extension='json')

wf.connect_input('keep_json','upload_pif.inputs.keep_json')
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')
wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect('pif_file.outputs.file_path','upload_pif.inputs.json_path')
wf.connect('batch.outputs.batch_outputs.pif','upload_pif.inputs.pif')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15_CITRINATION','batch_flow_synthesis_pif.wfm'))

