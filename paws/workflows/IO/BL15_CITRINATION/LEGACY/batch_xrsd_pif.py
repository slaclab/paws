import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_wfm('IO.BL15_CITRINATION.LEGACY.xrsd_pif')
pif_wf = wfmgr.workflows['read_to_pif']
#pif_wf.set_input('upload_flag',False)

wfmgr.add_workflow('batch_pif')
wfmgr.load_operations('batch_pif',
    header_files='IO.FILESYSTEM.BuildFileList',
    batch='EXECUTION.Batch',
    output_file='IO.FILESYSTEM.BuildFilePath',
    upload_pif='IO.CITRINATION.UploadPIF'
    )

wf = wfmgr.workflows['batch_pif']

wf.connect_input('header_dir','header_files.inputs.dir_path') 
wf.connect_input('header_regex','header_files.inputs.regex') 

wf.connect_workflow('read_to_pif','batch.inputs.work_item')
wf.connect_input('source_wavelength','batch.inputs.static_inputs.source_wavelength')
wf.connect_input('populations_dir','batch.inputs.static_inputs.populations_dir') 
wf.connect_input('populations_suffix','batch.inputs.static_inputs.populations_suffix') 
wf.connect_input('q_I_dir','batch.inputs.static_inputs.q_I_dir')
wf.connect_input('q_I_suffix','batch.inputs.static_inputs.q_I_suffix') 
wf.connect_input('q_I_ext','batch.inputs.static_inputs.q_I_ext')
wf.connect_input('keep_individual_json','batch.inputs.static_inputs.keep_json')
wf.connect_input('experiment_id',[
    'batch.inputs.static_inputs.experiment_id',
    'output_file.inputs.filename'
    ])
wf.connect('header_files.outputs.file_list','batch.inputs.batch_inputs.header_file')
wf.connect_output('batch_outputs','batch.outputs.batch_outputs')
wf.connect_output('pifs','batch.outputs.batch_outputs.pif')

wf.connect_input('output_dir',[
    'output_file.inputs.dir_path',
    'batch.inputs.static_inputs.output_dir'
    ])
wf.connect_input('output_suffix',[
    'output_file.inputs.suffix',
    'batch.inputs.static_inputs.output_suffix'
    ])
wf.connect_input('output_extension',[
    'output_file.inputs.extension',
    'batch.inputs.static_inputs.output_extension'
    ])
wf.set_op_inputs('output_file',suffix='_pif',extension='json')

wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect_input('keep_json','upload_pif.inputs.keep_json')
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')
wf.connect('batch.outputs.batch_outputs.pif','upload_pif.inputs.pif')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')
wf.connect('output_file.outputs.file_path','upload_pif.inputs.json_path')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15_CITRINATION','LEGACY','batch_xrsd_pif.wfm'))

