import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# specify workflow names: 
wf_names = ['saxs_integrate']
# specify operation names and corresponding modules: 
op_map = OrderedDict()
op_map['read_calibration'] = 'IO.CALIBRATION.ReadPONI'
op_map['build_integrator'] = 'PROCESSING.INTEGRATION.BuildPyFAIIntegrator'
op_map['read_image'] = 'IO.IMAGE.FabIOOpen'
op_map['integrate_to_1d'] = 'PROCESSING.INTEGRATION.ApplyIntegrator1d'
op_map['q_window'] = 'PACKAGING.Window'
op_map['dezinger'] = 'PROCESSING.ZINGERS.EasyZingers1d'
op_map['log_I'] = 'PROCESSING.BASIC.LogY'
op_map['output_CSV'] = 'IO.CSV.WriteArrayCSV'

wfmgr = WfManager()
wfmgr.add_workflow('saxs_integrate')
wf = wfmgr.workflows['saxs_integrate']
for op_name,op_uri in op_map.items():
    op = wfmgr.op_manager.get_operation(op_uri)
    wf.add_operation(op_name,op)

# input 1: path to .nika calibration file
wf.set_op_input('read_calibration','file_path','')
wf.connect_input('poni_file','read_calibration.inputs.file_path')
# input 2: path to image file
wf.set_op_input('read_image','file_path','')
wf.connect_input('file_path','read_image.inputs.file_path')
# inputs 3 and 4: q-range for data windowing
wf.set_op_input('q_window','x_min',0.0)
wf.set_op_input('q_window','x_max',1.0)
wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')
# input 5: path to output directory
wf.set_op_input('output_CSV','dir_path',os.getcwd())
wf.connect_input('output_dir','output_CSV.inputs.dir_path')

### (4) set up the rest of the Operation IO routing
wf.set_op_input('build_integrator','poni_dict','read_calibration.outputs.poni_dict','workflow item')
wf.set_op_input('integrate_to_1d','image_data','read_image.outputs.image_data','workflow item')
wf.set_op_input('integrate_to_1d','integrator','build_integrator.outputs.integrator','workflow item')
wf.set_op_input('q_window','x_y','integrate_to_1d.outputs.q_I','workflow item')
wf.set_op_input('dezinger','q_I','q_window.outputs.x_y_window','workflow item')
wf.set_op_input('log_I','x_y','dezinger.outputs.q_I_dz','workflow item')
wf.set_op_input('output_CSV','array','dezinger.outputs.q_I_dz','workflow item')
wf.set_op_input('output_CSV','headers',['q (1/angstrom)','intensity (arb)'])
wf.set_op_input('output_CSV','filename','read_image.outputs.filename','workflow item')
wf.set_op_input('output_CSV','filetag','_dz')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','saxs_integrate.wfl'),wfmgr)

