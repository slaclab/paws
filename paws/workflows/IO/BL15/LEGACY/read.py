import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_workflow('read','IO.BL15.read')

# replace the new YAML-based header reader with the old txt-based reader
wfmgr.load_operations('read',
    read_header='IO.BL15.ReadHeader')
# correct the relevant workflow outputs, add an input for temperature_key
wf = wfmgr.workflows['read']
wf.break_output('header_data')
wf.connect_output('header_data','read_header.outputs.header_dict')
wf.connect_input('temperature_key','read_header.inputs.temperature_key')

wfmgr.save_to_wfl('read',os.path.join(pawstools.sourcedir,'workflows','IO','BL15','LEGACY','read.wfl'))

