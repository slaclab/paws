import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('make_plot')
wfmgr.load_operations('make_plot',
    read_q_I='IO.NumpyLoad',
    plot='PLOTTING.MakePlot'
    )

wf = wfmgr.workflows['make_plot']

wf.connect_input('q_I_file','read_q_I.inputs.file_path')

wf.connect('read_q_I.outputs.data','plot.inputs.x_y_data')
wf.connect_input('log_y_flag','plot.inputs.logy')
wf.connect_input('log_x_flag','plot.inputs.logx')

wfmgr.save_to_wfl('make_plot',os.path.join(pawstools.sourcedir,'workflows','VISUALIZATION','plot_q_I.wfl'))

