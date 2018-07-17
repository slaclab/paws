import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.load_packaged_wfm('INTEGRATION.BL15.integrate')
wfmgr.add_workflow('integrate_bgsub')
wfmgr.load_operations('integrate_bgsub',
    run_integrate = 'EXECUTION.Run',
    read_bg = 'IO.NumpyLoad',
    bg_subtract = 'PROCESSING.BACKGROUND.BgSubtract',
    output_path = 'IO.FILESYSTEM.BuildFilePath',
    write_q_I = 'IO.NumpySave'
    )

pgmgr = wfmgr.plugin_manager

wf = wfmgr.workflows['integrate_bgsub']
wf.connect_input('header_file','run_integrate.inputs.inputs.header_file')
wf.connect_workflow('integrate','run_integrate.inputs.work_item')
wf.connect_output('q_I','run_integrate.outputs.outputs.q_I')

wf.connect_input('bg_file_path','read_bg.inputs.file_path')
wf.connect('read_bg.outputs.data','bg_subtract.inputs.q_I_bg')
wf.connect('run_integrate.outputs.outputs.q_I_dz','bg_subtract.inputs.q_I')
wf.connect_output('q_I_bgsub','bg_subtract.outputs.q_I_bgsub')

wf.connect('run_integrate.outputs.outputs.image_dir','output_path.inputs.dir_path')
wf.connect('run_integrate.outputs.outputs.image_filename','output_path.inputs.filename')
wf.set_op_input('output_path','suffix','_dz_bgsub')
wf.connect_output('output_path','output_path.outputs.file_path')

wf.connect('output_path.outputs.file_path','write_q_I.inputs.file_path')
wf.set_op_input('write_q_I','header','q (1/angstrom), Intensity (arb)')
wf.connect('bg_subtract.outputs.q_I_bgsub','write_q_I.inputs.data')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','BL15','integrate_bgsub.wfm'))

