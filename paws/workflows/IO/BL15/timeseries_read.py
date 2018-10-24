import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_wfm('IO.BL15.batch_read')
wfmgr.load_operations('batch_read',
    t_headers='PACKAGING.BATCH.XYDataFromBatch',
    t_images='PACKAGING.BATCH.XYDataFromBatch',
    t_q_I='PACKAGING.BATCH.XYDataFromBatch',
    t_systems='PACKAGING.BATCH.XYDataFromBatch'
    )

wf = wfmgr.workflows['batch_read']

wf.connect('batch.outputs.batch_outputs',[\
    't_headers.inputs.batch_outputs',
    't_images.inputs.batch_outputs',
    't_q_I.inputs.batch_outputs',
    't_systems.inputs.batch_outputs'])

wf.set_op_inputs('t_headers',x_key='time',y_key='header_data',x_sort_flag=True,x_shift_flag=True)
wf.set_op_inputs('t_images',x_key='time',y_key='image_data',x_sort_flag=True,x_shift_flag=True)
wf.set_op_inputs('t_q_I',x_key='time',y_key='q_I',x_sort_flag=True,x_shift_flag=True)
wf.set_op_inputs('t_systems',x_key='time',y_key='system',x_sort_flag=True,x_shift_flag=True)
# workflow inputs: lower and upper indices to read
wf.connect_input('lower_index',['t_headers.inputs.lower_index',\
    't_images.inputs.lower_index','t_q_I.inputs.lower_index',\
    't_systems.inputs.lower_index'])
wf.connect_input('upper_index',['t_headers.inputs.upper_index',\
    't_images.inputs.upper_index','t_q_I.inputs.upper_index',\
    't_systems.inputs.upper_index'])

#wf.connect_output('t_headers','t_headers.outputs.x_y')
#wf.connect_output('t_images','t_images.outputs.x_y')
#wf.connect_output('t_q_I','t_q_I.outputs.x_y')
#wf.connect_output('t_systems','t_systems.outputs.x_y')
wf.connect_output('ordered_headers','t_headers.outputs.y')
wf.connect_output('ordered_images','t_images.outputs.y')
wf.connect_output('ordered_q_I','t_q_I.outputs.y')
wf.connect_output('ordered_systems','t_systems.outputs.y')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15','timeseries_read.wfm'))

