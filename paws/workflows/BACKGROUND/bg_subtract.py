import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('bg_subtract')
wfmgr.load_operations('bg_subtract',
    read_bg = 'IO.NumpyLoad',
    read_data = 'IO.NumpyLoad',
    subtract_bg = 'PROCESSING.BACKGROUND.BgSubtract',
    output_path = 'IO.FILESYSTEM.BuildFilePath',
    write_q_I = 'IO.NumpySave'
    )

wf = wfmgr.workflows['bg_subtract']
# inputs: paths to data and bg files
wf.connect_input('bg_file','read_bg.inputs.file_path')
wf.connect_input('data_file','read_data.inputs.file_path')
# inputs: data and bg data (for skipping file io) 
wf.connect_input('bg_data','read_bg.outputs.data')
wf.connect_input('data','read_data.outputs.data')

wf.connect_output('bg_factor','subtract_bg.outputs.bg_factor')
wf.connect_output('q_I_bgsub','subtract_bg.outputs.q_I_bgsub')

wf.connect('read_data.outputs.data','subtract_bg.inputs.q_I')
wf.connect('read_bg.outputs.data','subtract_bg.inputs.q_I_bg')

wf.connect('read_data.outputs.dir_path','output_path.inputs.dir_path')
wf.connect('read_data.outputs.filename','output_path.inputs.filename')
wf.set_op_input('output_path','suffix','_bgsub')
wf.set_op_input('output_path','extension','dat')

wf.connect('subtract_bg.outputs.q_I_bgsub','write_q_I.inputs.data')
wf.set_op_input('write_q_I','header','q (1/angstrom), Intensity (arb)')
wf.connect('output_path.outputs.file_path','write_q_I.inputs.file_path')

wfmgr.save_to_wfl('bg_subtract',os.path.join(pawstools.sourcedir,'workflows','BACKGROUND','bg_subtract.wfl'))

