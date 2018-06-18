import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('read_and_integrate')
wfmgr.load_operations('read_and_integrate',
    read_header = 'IO.BL15.ReadHeader_SSRL15',
    time_temp = 'PACKAGING.BL15.TimeTempFromHeader',
    image_path = 'IO.FILESYSTEM.BuildFilePath',
    read_image = 'IO.IMAGE.FabIOOpen',
    integrate = 'PROCESSING.INTEGRATION.ApplyIntegrator1d',
    q_window = 'PACKAGING.Window',
    dezinger = 'PROCESSING.ZINGERS.EasyZingers1d',
    output_CSV = 'IO.CSV.WriteArrayCSV'
    )

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('integrator','PyFAIIntegrator')

wf = wfmgr.workflows['read_and_integrate']
# input: path to header file
wf.connect_input('header_file_path','read_header.inputs.file_path')
# input: path to image files directory 
wf.connect_input('sample_dir','image_path.inputs.dir_path')
wf.connect_input('image_ext','image_path.inputs.ext')
wf.set_op_input('image_path','ext','tif')
# inputs: q-range for data windowing
wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')
wf.set_op_input('q_min',0.)
wf.set_op_input('q_max',1.)
# inputs: keys for fetching time,temperature from header dictionary 
wf.connect_input('temperature_key','time_temp.inputs.temperature_key')
wf.connect_input('time_key','time_temp.inputs.time_key')
# input 5: pyfai.AzimuthalIntegrator
wf.connect_plugin('integrator','integrate.inputs.integrator')

wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('q_I','integrate.outputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')

wf.connect('read_header.outputs.filename','image_path.inputs.filename')
wf.connect('image_path.outputs.file_path','read_image.inputs.file_path')
wf.connect('read_header.outputs.header_dict','time_temp.inputs.header_dict')
wf.connect('read_image.outputs.image_data','integrate.inputs.image_data')
wf.connect('integrate.outputs.q_I','q_window.inputs.x_y')
wf.connect('q_window.outputs.x_y_window','dezinger.inputs.q_I')
wf.connect('dezinger.outputs.q_I_dz','output_CSV.inputs.array')
wf.connect('image_path.inputs.dir_path','output_CSV.inputs.dir_path')
wf.connect('image_path.inputs.filename','output_CSV.inputs.filename')
wf.set_op_input('output_CSV','headers',['q (1/angstrom)','intensity (arb)'])
wf.set_op_input('output_CSV','filetag','_dz')


wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','BL15','integrate.wfm'),wfmgr)

