import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('integrate')
wfmgr.load_operations('integrate',
    read_image = 'IO.IMAGE.FabIOOpen',
    integrate = 'PROCESSING.INTEGRATION.Integrate1d',
    q_window = 'PACKAGING.Window',
    dezinger = 'PROCESSING.ZINGERS.EasyZingers1d',
    output_file = 'IO.FILESYSTEM.BuildFilePath',
    output_file_dz = 'IO.FILESYSTEM.BuildFilePath',
    write_q_I = 'IO.NumpySave',
    write_q_I_dz = 'IO.NumpySave'
    )

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('integrator','PyFAIIntegrator')

wf = wfmgr.workflows['integrate']

wf.connect_input('image_file','read_image.inputs.file_path')

wf.connect_plugin('integrator','integrate.inputs.integrator')
wf.connect('read_image.outputs.image_data','integrate.inputs.image_data')
wf.connect_input('image_data','integrate.inputs.image_data')
wf.connect_output('q_I','integrate.outputs.q_I')

wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')
wf.set_op_input('q_window','x_min',0.)
wf.set_op_input('q_window','x_max',1.)
wf.connect('integrate.outputs.q_I','q_window.inputs.x_y')

wf.connect('q_window.outputs.x_y_window','dezinger.inputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')

wf.connect_input('output_dir',[\
    'output_file.inputs.dir_path',
    'output_file_dz.inputs.dir_path']
    )
wf.connect_input('filename',[\
    'output_file.inputs.filename',
    'output_file_dz.inputs.filename']
    )
wf.connect('read_image.outputs.filename',[
    'output_file.inputs.filename',
    'output_file_dz.inputs.filename']
    )
wf.connect('read_image.outputs.dir_path',[
    'output_file.inputs.dir_path',
    'output_file_dz.inputs.dir_path']
    )
wf.set_op_input('output_file','extension','dat')
wf.set_op_input('output_file_dz','suffix','_dz')
wf.set_op_input('output_file_dz','extension','dat')

wf.connect('q_window.outputs.x_y_window','write_q_I.inputs.data')
wf.set_op_input('write_q_I','header','q (1/angstrom), Intensity (arb)')
wf.connect('output_file.outputs.file_path','write_q_I.inputs.file_path')
wf.connect_output('q_I_file','output_file.outputs.file_path')

wf.connect('dezinger.outputs.q_I_dz','write_q_I_dz.inputs.data')
wf.set_op_input('write_q_I_dz','header','q (1/angstrom), Intensity (arb)')
wf.connect('output_file_dz.outputs.file_path','write_q_I_dz.inputs.file_path')
wf.connect_output('q_I_dz_file','output_file_dz.outputs.file_path')
wf.connect_output('q_I_dz_filename','output_file_dz.outputs.filename')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','integrate.wfm'))

