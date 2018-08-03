import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('integrate')
wfmgr.load_operations('integrate',
    read_header = 'IO.BL15.ReadHeader',
    image_path = 'IO.FILESYSTEM.BuildFilePath',
    read_image = 'IO.IMAGE.FabIOOpen',
    integrate = 'PROCESSING.INTEGRATION.Integrate1d',
    q_window = 'PACKAGING.Window',
    dezinger = 'PROCESSING.ZINGERS.EasyZingers1d',
    output_path = 'IO.FILESYSTEM.BuildFilePath',
    write_q_I = 'IO.NumpySave'
    )

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('integrator','PyFAIIntegrator')

wf = wfmgr.workflows['integrate']
# input: path to header file
wf.connect_input('header_file','read_header.inputs.file_path')
# input: path to image files directory 
#
# TODO: set up a CONTROL.Switch to fall back on read_header.inputs.dir_path
wf.connect_input('sample_dir','image_path.inputs.dir_path')
#
wf.connect_input('image_ext','image_path.inputs.extension')
wf.set_op_input('image_path','extension','tif')
# inputs: q-range for data windowing
wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')
wf.set_op_input('q_window','x_min',0.)
wf.set_op_input('q_window','x_max',1.)
# input: key for fetching temperature from header dictionary 
wf.connect_input('temperature_key','read_header.inputs.temperature_key')
# input: pyfai.AzimuthalIntegrator
wf.connect_input('integrator','integrate.inputs.integrator')
wf.connect_plugin('integrator','integrate.inputs.integrator')

wf.connect_output('time','read_header.outputs.data.t_utc')
wf.connect_output('temperature','read_header.outputs.data.temperature')
wf.connect_output('q_I','integrate.outputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')

wf.connect('read_header.outputs.filename','image_path.inputs.filename')
wf.connect('image_path.outputs.file_path','read_image.inputs.file_path')
wf.connect('read_image.outputs.image_data','integrate.inputs.image_data')
wf.connect('integrate.outputs.q_I','q_window.inputs.x_y')
wf.connect('q_window.outputs.x_y_window','dezinger.inputs.q_I')

wf.connect('image_path.inputs.dir_path','output_path.inputs.dir_path')
wf.connect('image_path.inputs.filename','output_path.inputs.filename')
wf.set_op_input('output_path','suffix','_dz')
wf.set_op_input('output_path','extension','dat')

wf.connect('dezinger.outputs.q_I_dz','write_q_I.inputs.data')
wf.set_op_input('write_q_I','header','q (1/angstrom), Intensity (arb)')
wf.connect('output_path.outputs.file_path','write_q_I.inputs.file_path')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','BL15','integrate_legacy.wfm'))

