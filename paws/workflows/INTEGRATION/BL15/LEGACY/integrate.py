import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_wfm('INTEGRATION.BL15.integrate')

# replace the new YAML-based header reader with the old txt-based reader
wfmgr.load_operations('integrate',
    read_header='IO.BL15.ReadHeader')
# add an input for temperature_key for legacy headers
wf = wfmgr.workflows['integrate']
wf.connect_input('temperature_key','read_header.inputs.temperature_key')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','BL15','LEGACY','integrate.wfm'))

