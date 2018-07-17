import os

from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()
wfmgr.add_workflow('run_exposure')
wfmgr.load_operations('run_exposure',
    mar_expose='DAQ.PLUGINS.MarCCD_SISExpose',
    mar_image_file='IO.FILESYSTEM.BuildFilePath',
    local_image_file='IO.FILESYSTEM.BuildFilePath',
    collect_image='IO.FILESYSTEM.SSHCopy',
    )

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugins(
    timer='Timer',
    spec_infoclient='SpecInfoClient',
    mar_ssh_client='SSHClient'
    )

pgmgr.connect('timer',[
    'spec_infoclient.inputs.timer',
    'mar_ssh_client.inputs.timer'])

wf = wfmgr.workflows['run_exposure']

wf.connect_input('exposure_time','mar_expose.inputs.exposure_time')
wf.connect_plugin('spec_infoclient','mar_expose.inputs.spec_infoclient')
wf.connect_input('filename',[
    'mar_expose.inputs.filename',
    'mar_image_file.inputs.filename',
    'local_image_file.inputs.filename']
    )
wf.connect_input('file_suffix',[\
    'mar_image_file.inputs.suffix',
    'local_image_file.inputs.suffix'])
wf.connect_input('output_dir','local_image_file.inputs.dir_path')
wf.set_op_inputs('mar_image_file',dir_path='/home/data',extension='tif')
wf.set_op_inputs('local_image_file',extension='tif')

wf.connect_plugin('mar_ssh_client','collect_image.inputs.ssh_client')
wf.connect('mar_image_file.outputs.file_path','collect_image.inputs.remote_path')
wf.connect('local_image_file.outputs.file_path','collect_image.inputs.local_path')

wf.connect_output('image_file','local_image_file.outputs.file_path')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','mar_expose.wfm'))

