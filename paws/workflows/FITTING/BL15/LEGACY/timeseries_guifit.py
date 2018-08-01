import os

from paws import pawstools
from paws.workflows.WfManager import WfManager

wfmgr = WfManager()

wfmgr.load_packaged_wfm('FITTING.BL15.LEGACY.batch_fit')

wf = wfmgr.workflows['main']

# replace XRSDFit with XRSDFitGUI
wfmgr.load_operations('read_and_fit',
    fit='PROCESSING.FITTING.XRSDFitGUI'
    )

wf.set_op_inputs('t_filenames',x_sort_flag=True)
wf.set_op_inputs('t_q_I_files',x_sort_flag=True)
wf.set_op_inputs('t_populations_files',x_sort_flag=True)
wf.set_op_input('batch_fit','serial_params',
    {'populations':'populations','param_bounds':'param_bounds',
    'fixed_params':'fixed_params','param_constraints':'param_constraints'})

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','LEGACY','timeseries_guifit.wfm'))

