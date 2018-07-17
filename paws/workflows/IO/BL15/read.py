import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('read')
wfmgr.load_operations('read',
    read_header='IO.YAML.LoadYAML',
    image_file='IO.FILESYSTEM.BuildFilePath',
    q_I_file='IO.FILESYSTEM.BuildFilePath',
    read_image='IO.IMAGE.FabIOOpen',
    read_q_I='IO.NumpyLoad'
    )

wf = wfmgr.workflows['read']

wf.connect_input('header_file','read_header.inputs.file_path') 
wf.connect_output('header_data','read_header.outputs.data') 
#wf.connect_output('time','read_header.outputs.data.t_utc')
#wf.connect_output('temperature','read_header.outputs.data.temperature')
#wf.connect_output('date_time','read_header.outputs.data.time')
wf.connect_output('filename','read_header.outputs.filename')
wf.connect_output('header_file','read_header.inputs.file_path')

wf.connect('read_header.outputs.filename',[\
    'image_file.inputs.filename',\
    'q_I_file.inputs.filename'])

wf.connect_input('image_dir','image_file.inputs.dir_path')
wf.set_op_input('image_file','extension','tif')
wf.connect_output('image_file','image_file.outputs.file_path')

wf.connect_input('q_I_dir','q_I_file.inputs.dir_path')
wf.connect_input('q_I_suffix','q_I_file.inputs.suffix')
wf.connect_input('q_I_ext','q_I_file.inputs.extension')
wf.connect_output('q_I_file','q_I_file.outputs.file_path')
#wf.set_op_input('q_I_file','suffix','_dz_bgsub')
wf.set_op_input('q_I_file','extension','dat')

wf.connect('image_file.outputs.file_path','read_image.inputs.file_path')
wf.connect_output('image_data','read_image.outputs.image_data')

wf.connect('q_I_file.outputs.file_path','read_q_I.inputs.file_path')
wf.connect_output('q_I_data','read_q_I.outputs.data')

wfmgr.save_to_wfl('read',os.path.join(pawstools.sourcedir,'workflows','IO','BL15','read.wfl'))

