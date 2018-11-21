import os

from paws import pawstools
from paws.workflows.WfManager import WfManager

wfmgr = WfManager()

#wfmgr.load_packaged_workflow('read','IO.BL15.read')
wfmgr.load_packaged_wfm('FITTING.BL15.batch_fit')
# replace YAML-based read workflow with legacy version 
wfmgr.load_packaged_workflow('read','IO.BL15.LEGACY.read')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','LEGACY','batch_fit.wfm'))

