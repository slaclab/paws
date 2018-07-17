import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('bg_subtract')
wfmgr.load_operations('bg_subtract',
    read_q_I = 'IO.NumpyLoad',
    read_q_I_bg = 'IO.NumpyLoad',
    subtract_bg = 'PROCESSING.BACKGROUND.BgSubtract',
    output_file = 'IO.FILESYSTEM.BuildFilePath',
    write_q_I_bgsub = 'IO.NumpySave'
    )

wf = wfmgr.workflows['bg_subtract']

wf.connect_input('q_I_file','read_q_I.inputs.file_path')
wf.connect_input('q_I_bg_file','read_q_I_bg.inputs.file_path')
wf.connect('read_q_I.outputs.data','subtract_bg.inputs.q_I')
wf.connect('read_q_I_bg.outputs.data','subtract_bg.inputs.q_I_bg')

# connect inputs for bypassing IO
#wf.connect_input('q_I_bg','read_q_I_bg.outputs.data')
#wf.connect_input('q_I','read_q_I.outputs.data')
wf.connect_input('q_I','subtract_bg.inputs.q_I')
wf.connect_input('q_I_bg','subtract_bg.inputs.q_I_bg')
wf.connect_output('bg_factor','subtract_bg.outputs.bg_factor')
wf.connect_output('q_I_bgsub','subtract_bg.outputs.q_I_bgsub')

wf.connect_input('output_dir','output_file.inputs.dir_path')
wf.connect_input('output_filename','output_file.inputs.filename')
wf.connect('read_q_I.outputs.filename','output_file.inputs.filename')
wf.connect('read_q_I.outputs.dir_path','output_file.inputs.dir_path')
wf.set_op_input('output_file','suffix','_bgsub')
wf.set_op_input('output_file','extension','dat')
wf.connect_output('q_I_file','output_file.outputs.file_path')
wf.connect_output('q_I_filename','output_file.outputs.filename')

wf.connect('subtract_bg.outputs.q_I_bgsub','write_q_I_bgsub.inputs.data')
wf.set_op_input('write_q_I_bgsub','header','q (1/angstrom), Intensity (arb)')
wf.connect('output_file.outputs.file_path','write_q_I_bgsub.inputs.file_path')

wfmgr.save_to_wfl('bg_subtract',os.path.join(pawstools.sourcedir,'workflows','BACKGROUND','bg_subtract.wfl'))

