import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_workflow('read','IO.BL15.LEGACY.read')
wfmgr.add_workflow('xrsd_pif')
wfmgr.load_operations('xrsd_pif',
    read='EXECUTION.Run',
    make_pif='PACKAGING.PIF.PackXRSDPIF',
    pif_file='IO.FILESYSTEM.BuildFilePath',
    upload_pif='IO.CITRINATION.UploadPIF'
    )
pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('citrination_client','CitrinationClient')

wf = wfmgr.workflows['xrsd_pif']

wf.connect_workflow('read','read.inputs.work_item')
wf.connect_input('header_file','read.inputs.inputs.header_file')
wf.connect_input('q_I_dir','read.inputs.inputs.q_I_dir')
wf.connect_input('q_I_suffix','read.inputs.inputs.q_I_suffix')
wf.connect_input('q_I_ext','read.inputs.inputs.q_I_ext')

wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
wf.connect_input('source_wavelength','make_pif.inputs.source_wavelength')
wf.connect('read.outputs.outputs.q_I_file','make_pif.inputs.q_I_file')
wf.connect('read.outputs.outputs.populations_file','make_pif.inputs.populations_file')
wf.connect('read.outputs.outputs.header_data.TEMP','make_pif.inputs.temperature')
wf.connect('read.outputs.outputs.header_data.t_utc','make_pif.inputs.t_utc')
wf.connect_output('pif','make_pif.outputs.pif')

wf.connect_input('output_dir','pif_file.inputs.dir_path')
wf.connect_input('pif_file_suffix','pif_file.inputs.suffix')
wf.connect('read.outputs.outputs.filename','pif_file.inputs.filename')
wf.connect('read.outputs.outputs.dir_path','pif_file.inputs.dir_path')
wf.set_op_inputs('pif_file',suffix='_pif',extension='json')

wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect_input('keep_json','upload_pif.inputs.keep_json')
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')
wf.connect('make_pif.outputs.pif','upload_pif.inputs.pif')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')
wf.connect('pif_file.outputs.file_path','upload_pif.inputs.json_path')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','CITRINATION','LEGACY','xrsd_pif.wfm'))

