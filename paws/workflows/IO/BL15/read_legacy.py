import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_workflow('read','IO.BL15.read')

# replace the new YAML-based header reader with the old txt-based reader,
# and add an op for extracting time and temperature
wfmgr.load_operations('read',
    read_header='IO.BL15.ReadHeader')
# correct the relevant workflow outputs
wf = wfmgr.workflows['read']
wf.break_output('header_data')
wf.connect_output('header_data','read_header.outputs.header_dict')

wfmgr.save_to_wfl('read',os.path.join(pawstools.sourcedir,'workflows','IO','BL15','read_legacy.wfl'))

