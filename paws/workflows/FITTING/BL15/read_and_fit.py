import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('read_and_fit')
wfmgr.load_operations('read_and_fit',
    read_xrsd='IO.NumpyLoad',
    fit='PROCESSING.FITTING.XRSDFit',
    save_fit='IO.YAML.SaveXRSDFit',
    )

wf = wfmgr.workflows['read_and_fit']

wf.connect_input('data_filepath','read_xrsd.inputs.file_path')

wf.connect_input('populations_file','save_fit.inputs.file_path')
wf.connect_output('populations_file','save_fit.inputs.file_path')

wf.connect_input('populations','fit.inputs.populations')
wf.connect_input('fixed_params','fit.inputs.fixed_params')
wf.connect_input('param_bounds','fit.inputs.param_bounds')
wf.connect_input('param_constraints','fit.inputs.param_constraints')
wf.connect('read_xrsd.outputs.data','fit.inputs.q_I')
wf.connect_input('source_wavelength','fit.inputs.source_wavelength')
wf.connect_input('q_range','fit.inputs.q_range')
wf.connect('fit.outputs.populations','save_fit.inputs.populations')
wf.connect('fit.outputs.report','save_fit.inputs.report')
wf.connect('fit.inputs.fixed_params','save_fit.inputs.fixed_params')
wf.connect('fit.inputs.param_bounds','save_fit.inputs.param_bounds')
wf.connect('fit.inputs.param_constraints','save_fit.inputs.param_constraints')
wf.connect_output('populations','fit.outputs.populations')
wf.connect_output('report','fit.outputs.report')
wf.connect_output('fixed_params','fit.inputs.fixed_params')
wf.connect_output('param_bounds','fit.inputs.param_bounds')
wf.connect_output('param_constraints','fit.inputs.param_constraints')

wfmgr.save_to_wfl('read_and_fit',os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','read_and_fit.wfl'))

