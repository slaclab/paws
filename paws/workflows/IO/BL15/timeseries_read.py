import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_wfm('IO.BL15.batch_read')
wfmgr.load_operations('batch_read',
    t_headers='PACKAGING.BATCH.XYDataFromBatch',
    t_images='PACKAGING.BATCH.XYDataFromBatch',
    t_q_I='PACKAGING.BATCH.XYDataFromBatch',
    t_system='PACKAGING.BATCH.XYDataFromBatch'
    )

wf = wfmgr.workflows['batch_read']

wf.connect('batch.outputs.batch_outputs',[\
    't_headers.inputs.batch_outputs',
    't_images.inputs.batch_outputs',
    't_q_I.inputs.batch_outputs',
    't_system.inputs.batch_outputs'])

wf.set_op_inputs('t_headers',x_key='time',y_key='header_data',x_sort_flag=True,x_shift_flag=True)
wf.set_op_inputs('t_images',x_key='time',y_key='image_data',x_sort_flag=True,x_shift_flag=True)
wf.set_op_inputs('t_q_I',x_key='time',y_key='q_I_data',x_sort_flag=True,x_shift_flag=True)
wf.set_op_inputs('t_system',x_key='time',y_key='system',x_sort_flag=True,x_shift_flag=True)

wf.connect_output('t_headers','t_headers.outputs.x_y')
wf.connect_output('t_images','t_images.outputs.x_y')
wf.connect_output('t_q_I','t_q_I.outputs.x_y')
wf.connect_output('t_system','t_system.outputs.x_y')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15','timeseries_read.wfm'))

