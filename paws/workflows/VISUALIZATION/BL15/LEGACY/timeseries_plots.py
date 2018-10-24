import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_wfm('VISUALIZATION.BL15.timeseries_plots')

# replace the new YAML-based header reader with the old txt-based reader
wfmgr.load_operations('read',
    read_header='IO.BL15.ReadHeader')
# correct the relevant workflow outputs, add an input for temperature_key
wf = wfmgr.workflows['read']
wf.break_input('header_keymap')
wf.connect_input('temperature_key','read_header.inputs.temperature_key')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','VISUALIZATION','BL15','LEGACY','timeseries_plots.wfm'))

