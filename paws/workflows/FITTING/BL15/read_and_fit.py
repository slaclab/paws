import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('read_and_fit')
wfmgr.load_operations('read_and_fit',
    read_xrsd='IO.NumpyLoad',
    populations_file='IO.FILESYSTEM.BuildFilePath',
    check_pops_file='IO.FILESYSTEM.CheckFilePath',
    conditional_read='EXECUTION.Conditional',
    read_xrsdfit='IO.YAML.LoadXRSDFit',
    populations_switch='CONTROL.Switch', 
    fixed_params_switch='CONTROL.Switch', 
    param_bounds_switch='CONTROL.Switch', 
    param_constraints_switch='CONTROL.Switch', 
    fit='PROCESSING.FITTING.XRSDFit',
    save_fit='IO.YAML.SaveXRSDFit',
    )

wf = wfmgr.workflows['read_and_fit']

wf.connect_input('source_wavelength','fit.inputs.source_wavelength')
wf.connect_input('filename','populations_file.inputs.filename')
wf.connect_input('data_filepath','read_xrsd.inputs.file_path')
wf.connect_input('populations_dir','populations_file.inputs.dir_path')
wf.connect_input('populations','populations_switch.inputs.else_data')
wf.connect_input('fixed_params','fixed_params_switch.inputs.else_data')
wf.connect_input('param_bounds','param_bounds_switch.inputs.else_data')
wf.connect_input('param_constraints','param_constraints_switch.inputs.else_data')
wf.connect_input('q_range','fit.inputs.q_range')

wf.connect_output('populations','fit.outputs.populations')
wf.connect_output('report','fit.outputs.report')
wf.connect_output('fixed_params','fit.inputs.fixed_params')
wf.connect_output('param_bounds','fit.inputs.param_bounds')
wf.connect_output('param_constraints','fit.inputs.param_constraints')

wf.set_op_input('populations_file','extension','yml')
wf.connect('populations_file.outputs.file_path',
    ['check_pops_file.inputs.file_path',\
    'conditional_read.inputs.inputs.file_path',\
    'save_fit.inputs.file_path'])

wf.connect('check_pops_file.outputs.file_exists',
    ['conditional_read.inputs.condition',
    'populations_switch.inputs.condition',
    'fixed_params_switch.inputs.condition',
    'param_bounds_switch.inputs.condition',
    'param_constraints_switch.inputs.condition']
    )
wf.set_op_input('conditional_read','run_condition',True)
wf.set_op_inputs('populations_switch',truth_condition=True,else_data={})
wf.set_op_inputs('fixed_params_switch',truth_condition=True,else_data={})
wf.set_op_inputs('param_bounds_switch',truth_condition=True,else_data={})
wf.set_op_inputs('param_constraints_switch',truth_condition=True,else_data={})
wf.connect('conditional_read.outputs.outputs.populations','populations_switch.inputs.iftrue_data')
wf.connect('conditional_read.outputs.outputs.fixed_params','fixed_params_switch.inputs.iftrue_data')
wf.connect('conditional_read.outputs.outputs.param_bounds','param_bounds_switch.inputs.iftrue_data')
wf.connect('conditional_read.outputs.outputs.param_constraints','param_constraints_switch.inputs.iftrue_data')

wf.connect('read_xrsdfit','conditional_read.inputs.work_item')
wf.disable_op('read_xrsdfit')

wf.connect('read_xrsd.outputs.data','fit.inputs.q_I')
wf.connect('populations_switch.outputs.data','fit.inputs.populations')
wf.connect('fixed_params_switch.outputs.data','fit.inputs.fixed_params')
wf.connect('param_bounds_switch.outputs.data','fit.inputs.param_bounds')
wf.connect('param_constraints_switch.outputs.data','fit.inputs.param_constraints')

#wf.connect('populations_file.outputs.file_path','save_fit.inputs.file_path')
wf.connect('fit.outputs.populations','save_fit.inputs.populations')
wf.connect('fit.outputs.report','save_fit.inputs.report')
wf.connect('fit.inputs.fixed_params','save_fit.inputs.fixed_params')
wf.connect('fit.inputs.param_bounds','save_fit.inputs.param_bounds')
wf.connect('fit.inputs.param_constraints','save_fit.inputs.param_constraints')

wfmgr.save_to_wfl('read_and_fit',os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','read_and_fit.wfl'))

