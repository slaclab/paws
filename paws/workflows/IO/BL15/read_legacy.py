import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('read')
wfmgr.load_operations('read',
    read_header='IO.BL15.ReadHeader',
    time_temp='PACKAGING.BL15.TimeTempFromHeader',
    image_filepath='IO.FILESYSTEM.BuildFilePath',
    data_filepath='IO.FILESYSTEM.BuildFilePath',
    read_image='IO.IMAGE.FabIOOpen',
    read_q_I='IO.NumpyLoad'
    )

wf = wfmgr.workflows['read']

# input: header file path
wf.connect_input('header_filepath','read_header.inputs.file_path') 
# inputs: keys for getting time and temperature from header dict
wf.connect_input('time_key','time_temp.inputs.time_key') 
wf.connect_input('temperature_key','time_temp.inputs.temperature_key') 
# inputs: directories and suffixes for locating data files 
wf.connect_input('image_dir','image_filepath.inputs.dir_path')
wf.connect_input('data_dir','data_filepath.inputs.dir_path')
wf.connect_input('data_suffix','data_filepath.inputs.suffix')
wf.connect_input('data_ext','data_filepath.inputs.extension')

wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('date_time','time_temp.outputs.date_time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('filename','read_header.outputs.filename')
wf.connect_output('image_filepath','image_filepath.outputs.file_path')
wf.connect_output('data_filepath','data_filepath.outputs.file_path')
wf.connect_output('image_data','read_image.outputs.image_data')
wf.connect_output('q_I','read_q_I.outputs.data')

wf.connect('read_header.outputs.header_dict','time_temp.inputs.header_dict')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('time_temp','temperature_key','TEMP')

wf.connect('read_header.outputs.filename',[\
    'image_filepath.inputs.filename',\
    'data_filepath.inputs.filename'])
wf.set_op_input('image_filepath','extension','tif')
wf.set_op_input('data_filepath','suffix','_dz_bgsub')
wf.set_op_input('data_filepath','extension','dat')
wf.connect('image_filepath.outputs.file_path','read_image.inputs.file_path')
wf.connect('data_filepath.outputs.file_path','read_q_I.inputs.file_path')

wfmgr.save_to_wfl('read',os.path.join(pawstools.sourcedir,'workflows','IO','BL15','read_legacy.wfl'))

