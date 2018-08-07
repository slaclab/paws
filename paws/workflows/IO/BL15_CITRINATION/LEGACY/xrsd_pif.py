import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_workflow('read_to_pif','IO.BL15.LEGACY.read')
wfmgr.load_operations('read_to_pif',
    make_pif='PACKAGING.PIF.PackXRSDPIF',
    output_file='IO.FILESYSTEM.BuildFilePath',
    upload_pif='IO.CITRINATION.UploadPIF'
    ) 

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('citrination_client','CitrinationClient')

wf = wfmgr.workflows['read_to_pif']
wf.disable_op('read_image')
wf.enable_op('read_populations')
wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
wf.connect_input('source_wavelength','make_pif.inputs.source_wavelength')
wf.connect('read_q_I.outputs.data','make_pif.inputs.q_I')
wf.connect('read_populations.outputs.populations','make_pif.inputs.populations')
wf.connect('read_populations.outputs.fixed_params','make_pif.inputs.fixed_params')
wf.connect('read_populations.outputs.param_bounds','make_pif.inputs.param_bounds')
wf.connect('read_populations.outputs.param_constraints','make_pif.inputs.param_constraints')
wf.connect('read_header.outputs.data.temperature','make_pif.inputs.temperature')
wf.connect('read_header.outputs.data.t_utc','make_pif.inputs.t_utc')
wf.connect_output('pif','make_pif.outputs.pif')

wf.connect_input('output_dir','output_file.inputs.dir_path')
wf.connect_input('output_suffix','output_file.inputs.suffix')
wf.connect_input('output_extension','output_file.inputs.extension')
wf.set_op_inputs('output_file',suffix='_pif',extension='json')
wf.connect('read_header.outputs.filename','output_file.inputs.filename')
wf.connect('read_header.outputs.dir_path','output_file.inputs.dir_path')

wf.connect_input('dataset_id','upload_pif.inputs.dsid')
wf.connect_input('keep_json','upload_pif.inputs.keep_json')
wf.connect_input('upload_flag','upload_pif.inputs.upload_flag')
wf.connect('make_pif.outputs.pif','upload_pif.inputs.pif')
wf.connect_plugin('citrination_client','upload_pif.inputs.citrination_client')
wf.connect('output_file.outputs.file_path','upload_pif.inputs.json_path')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15_CITRINATION','LEGACY','xrsd_pif.wfm'))

