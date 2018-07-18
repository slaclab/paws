import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_workflow('read','IO.BL15.read')

# replace the new YAML-based header reader with the old txt-based reader,
# and add an op for extracting time and temperature
wfmgr.load_operations('read',
    read_header='IO.BL15.ReadHeader',
    time_temp='PACKAGING.BL15.TimeTempFromHeader')
# correct the relevant workflow outputs
wf = wfmgr.workflows['read']
wf.break_output('header_data')
wf.connect_output('header_data','read_header.outputs.header_dict')

wf.connect_input('time_key','time_temp.inputs.time_key')
wf.connect_input('temperature_key','time_temp.inputs.temperature_key')
wf.connect('read_header.outputs.header_dict','time_temp.inputs.header_dict')
wf.set_op_inputs('time_temp',time_key='time',temperature_key='TEMP')
wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')

wfmgr.save_to_wfl('read',os.path.join(pawstools.sourcedir,'workflows','IO','BL15','read_legacy.wfl'))

