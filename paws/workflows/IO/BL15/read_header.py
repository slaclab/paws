import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('read_header')
wfmgr.load_operations('read_header',
    read_header='IO.BL15.ReadHeader',
    time_temp='PACKAGING.BL15.TimeTempFromHeader',
    image_filepath='IO.FILESYSTEM.BuildFilePath',
    data_filepath='IO.FILESYSTEM.BuildFilePath'
    )

wf = wfmgr.workflows['read_header']

# input: header file path
wf.connect_input('header_filepath','read_header.inputs.file_path') 
# inputs: keys for getting time and temperature from header dict
wf.connect_input('time_key','time_temp.inputs.time_key') 
wf.connect_input('temperature_key','time_temp.inputs.temperature_key') 
wf.connect_input('image_dir','image_filepath.inputs.dir_path')
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

wf.connect('read_header.outputs.header_dict','time_temp.inputs.header_dict')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('time_temp','temperature_key','TEMP')

wf.connect('read_header.outputs.filename',[\
    'image_filepath.inputs.filename',\
    'data_filepath.inputs.filename'])
wf.set_op_input('image_filepath','extension','tif')
wf.set_op_input('data_filepath','suffix','_dz_bgsub')
wf.set_op_input('data_filepath','extension','dat')

wfmgr.save_to_wfl('read_header',os.path.join(pawstools.sourcedir,'workflows','IO','BL15','read_header.wfl'))

