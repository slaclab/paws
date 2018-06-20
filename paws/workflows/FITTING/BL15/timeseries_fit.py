import os

from paws import pawstools
from paws.workflows.WfManager import WfManager

wfmgr = WfManager()
wfmgr.add_workflow('main')
wfmgr.load_operations('main',
    header_files='IO.FILESYSTEM.BuildFileList',
    header_batch='EXECUTION.Batch',
    t_filepaths='PACKAGING.BATCH.XYDataFromBatch',
    t_filenames='PACKAGING.BATCH.XYDataFromBatch',
    batch_fit='EXECUTION.Batch'
    )

wfmgr.load_packaged_wfm('FITTING.BL15.batch_fit')

wf = wfmgr.workflows['main']

wf.set_op_inputs('t_filenames','x_sort_flag',True)
wf.set_op_inputs('t_filepaths','x_sort_flag',True)
wf.connect('t_filenames.outputs.y','batch_fit.inputs.batch_inputs.filename')
wf.connect('t_filepaths.outputs.y','batch_fit.inputs.batch_inputs.data_filepath')
wf.set_op_input('batch_fit','serial_params',
    {'populations':'populations','param_bounds':'param_bounds',
    'fixed_params':'fixed_params','param_constraints':'param_constraints'})

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','timeseries_fit.wfm'))

