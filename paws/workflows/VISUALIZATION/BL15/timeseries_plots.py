import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()
wfmgr.load_packaged_wfm('IO.BL15.timeseries_read')
wf = wfmgr.add_workflow('timeseries_plots')
wfmgr.load_operations('timeseries_plots',
    read_files='EXECUTION.Run',
    make_plots='EXECUTION.Batch',
    plot='VISUALIZATION.XRSDPlot'
    )
wf.disable_op('plot')

wf.connect_workflow('batch_read','read_files.inputs.work_item')
wf.connect('plot','make_plots.inputs.work_item')
wf.connect('read_files.outputs.outputs.ordered_q_I','make_plots.inputs.batch_inputs.q_I')
wf.connect('read_files.outputs.outputs.ordered_systems','make_plots.inputs.batch_inputs.system')
wf.connect_input('show_plots','make_plots.inputs.static_inputs.show_plot')
wf.connect_input('source_wavelength','make_plots.inputs.static_inputs.source_wavelength')
wf.connect_input('lower_index','read_files.inputs.inputs.lower_index')
wf.connect_input('upper_index','read_files.inputs.inputs.upper_index')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','VISUALIZATION','BL15','timeseries_plots.wfm'))

