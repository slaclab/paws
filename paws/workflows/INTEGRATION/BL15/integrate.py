import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('integrate')
wfmgr.load_operations('integrate',
    read_header = 'IO.YAML.LoadYAML',
    image_path = 'IO.FILESYSTEM.BuildFilePath',
    read_image = 'IO.IMAGE.FabIOOpen',
    integrate = 'PROCESSING.INTEGRATION.Integrate1d',
    q_window = 'PACKAGING.Window',
    dezinger = 'PROCESSING.ZINGERS.EasyZingers1d',
    output_path = 'IO.FILESYSTEM.BuildFilePath',
    output_path_dz = 'IO.FILESYSTEM.BuildFilePath',
    write_q_I = 'IO.NumpySave',
    write_q_I_dz = 'IO.NumpySave'
    )

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('integrator','PyFAIIntegrator')

wf = wfmgr.workflows['integrate']

wf.connect_input('header_file','read_header.inputs.file_path')
wf.connect_output('header_dir','read_header.outputs.dir_path')
wf.connect_output('header_data','read_header.outputs.data')

wf.connect_input('image_dir','image_path.inputs.dir_path')
wf.connect_input('image_ext','image_path.inputs.extension')
wf.set_op_input('image_path','extension','tif')
wf.connect('read_header.outputs.filename','image_path.inputs.filename')
wf.connect_output('image_filename','image_path.inputs.filename')

wf.connect('image_path.outputs.file_path','read_image.inputs.file_path')

wf.connect_input('integrator','integrate.inputs.integrator')
wf.connect_plugin('integrator','integrate.inputs.integrator')
wf.connect('read_image.outputs.image_data','integrate.inputs.image_data')
wf.connect_output('q_I','integrate.outputs.q_I')

wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')
wf.set_op_input('q_window','x_min',0.)
wf.set_op_input('q_window','x_max',1.)
wf.connect('integrate.outputs.q_I','q_window.inputs.x_y')

wf.connect('q_window.outputs.x_y_window','dezinger.inputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')

wf.connect_input('output_dir',['output_path.inputs.dir_path','output_path_dz.inputs.dir_path'])
wf.connect('read_header.outputs.filename',[\
    'output_path.inputs.filename',
    'output_path_dz.inputs.filename']
    )
wf.set_op_input('output_path','extension','dat')
wf.set_op_input('output_path_dz','suffix','_dz')
wf.set_op_input('output_path_dz','extension','dat')

wf.connect('q_window.outputs.x_y_window','write_q_I.inputs.data')
wf.set_op_input('write_q_I','header','q (1/angstrom), Intensity (arb)')
wf.connect('output_path.outputs.file_path','write_q_I.inputs.file_path')
wf.connect_output('q_I_file','output_path.outputs.file_path')

wf.connect('dezinger.outputs.q_I_dz','write_q_I_dz.inputs.data')
wf.set_op_input('write_q_I_dz','header','q (1/angstrom), Intensity (arb)')
wf.connect('output_path_dz.outputs.file_path','write_q_I_dz.inputs.file_path')
wf.connect_output('q_I_dz_file','output_path_dz.outputs.file_path')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','BL15','integrate.wfm'))

