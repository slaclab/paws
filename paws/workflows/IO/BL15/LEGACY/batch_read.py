import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_wfm('IO.BL15.batch_read')
wfmgr.load_packaged_workflow('read','IO.BL15.LEGACY.read')

wfmgr.workflows['batch_read'].connect_workflow('read','batch.inputs.work_item')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15','LEGACY','batch_read.wfm'))

