import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# specify workflow names: 
wf_names = ['saxs_gp_fit','batch_saxs_gp_fit']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['batch_saxs_gp_fit']['Batch Execution'] = 'EXECUTION.Batch'
op_maps['saxs_gp_fit']['Read Data'] = 'IO.NUMPY.Loadtxt_q_I_dI'
op_maps['saxs_gp_fit']['Q-Window'] = 'PACKAGING.Window'
op_maps['saxs_gp_fit']['Log(I)'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_gp_fit']['Fit Spectrum'] = 'PROCESSING.SAXS.SpectrumFit'
op_maps['saxs_gp_fit']['Log(I_fit)'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_gp_fit']['Output CSV'] = 'IO.CSV.WriteArrayCSV'

wfmgr = WfManager()
# add the workflows and activate/add the operations:
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)

wf = wfmgr.workflows['saxs_gp_fit']

wf.connect_input('file_path','Read Data.inputs.file_path')
wf.set_op_input('Read Data','file_path',None)

wf.set_op_input('Read Data','delimiter',',')
wf.set_op_input('Q-Window','x_y','Read Data.outputs.q_I','workflow item')
wf.set_op_input('Q-Window','x_min',0.02)
wf.set_op_input('Q-Window','x_max',0.5)
wf.set_op_input('Log(I)','x_y','Q-Window.outputs.x_y_window','workflow item')
wf.set_op_input('Fit Spectrum','q_I','Q-Window.outputs.x_y_window','workflow item')
wf.set_op_input('Fit Spectrum','populations',{'guinier_porod':1})
wf.set_op_input('Log(I_fit)','x_y','Fit Spectrum.outputs.q_I_opt','workflow item')
wf.set_op_input('Output CSV','array','Fit Spectrum.outputs.q_I_opt','workflow item')
wf.set_op_input('Output CSV','headers',['q','I'])
wf.set_op_input('Output CSV','dir_path','Read Data.outputs.dir_path','workflow item')
wf.set_op_input('Output CSV','filename','Read Data.outputs.filename','workflow item')
wf.set_op_input('Output CSV','filetag','_fit')

wf.disable_op('Output CSV')

wf = wfmgr.workflows['batch_saxs_gp_fit']

wf.set_op_input('Batch Execution','work_item','saxs_gp_fit','entire workflow')
wf.set_op_input('Batch Execution','input_arrays',None)
wf.set_op_input('Batch Execution','input_keys',['file_path'])

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','XICAM','batch_saxs_gp_fit.wfl'),wfmgr)

