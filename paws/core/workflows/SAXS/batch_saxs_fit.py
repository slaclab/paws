import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools


# specify workflow names: 
wf_names = ['saxs_fit','main']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['spectrum_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['batch'] = 'EXECUTION.Batch'
op_maps['main']['fit_params'] = 'PACKAGING.BATCH.XYDataFromBatch'

op_maps['saxs_fit']['read_spectrum'] = 'IO.NUMPY.Loadtxt_q_I_dI'
op_maps['saxs_fit']['fit_spectrum'] = 'PROCESSING.SAXS.SpectrumFit'
op_maps['saxs_fit']['log_I'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_fit']['log_Ifit'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_fit']['output_CSV'] = 'IO.CSV.WriteArrayCSV'

wfmgr = WfManager()
# add the workflows and activate/add the operations:
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)


wf = wfmgr.workflows['saxs_fit']

# input 0: spectrum file
wf.set_op_input('read_spectrum','file_path',None) 
wf.connect_input('file_path','read_spectrum.inputs.file_path') 

# input 1: populations dict
wf.set_op_input('fit_spectrum','populations',{'guinier_porod':1})
wf.connect_input('populations','fit_spectrum.inputs.populations')

wf.connect_output('filename','read_spectrum.outputs.filename')
wf.connect_output('q_I','read_spectrum.outputs.q_I')
wf.connect_output('q_logI','log_I.outputs.x_logy')
wf.connect_output('q_I_opt','fit_spectrum.outputs.q_I_opt')
wf.connect_output('q_logI_opt','log_Ifit.outputs.x_logy')
wf.connect_output('fit_params','fit_spectrum.outputs.params')

wf.set_op_input('read_spectrum','delimiter',',')
wf.set_op_input('log_I','x_y','read_spectrum.outputs.q_I','workflow item')
wf.set_op_input('fit_spectrum','q_I','read_spectrum.outputs.q_I','workflow item')
wf.set_op_input('log_Ifit','x_y','fit_spectrum.outputs.q_I_opt','workflow item')
wf.set_op_input('output_CSV','array','fit_spectrum.outputs.q_I_opt','workflow item')
wf.set_op_input('output_CSV','headers',['q (1/angstrom)','intensity (arb)'])
wf.set_op_input('output_CSV','dir_path','read_spectrum.outputs.dir_path','workflow item')
wf.set_op_input('output_CSV','filename','read_spectrum.outputs.filename','workflow item')
wf.set_op_input('output_CSV','filetag','_fit')


wf = wfmgr.workflows['main']

# input 0: spectrum file location
wf.set_op_input('spectrum_files','dir_path',None) 
wf.connect_input('data_dir','spectrum_files.inputs.dir_path') 

# input 1: spectrum file regex
wf.set_op_input('spectrum_files','regex','*.csv') 
wf.connect_input('data_regex','spectrum_files.inputs.regex') 

wf.set_op_input('batch','work_item','saxs_fit','entire workflow')
wf.set_op_input('batch','input_arrays',['spectrum_files.outputs.file_list'],'workflow item')
wf.set_op_input('batch','input_keys',['file_path'])

wf.set_op_input('fit_params','batch_outputs','batch.outputs.batch_outputs','workflow item')
wf.set_op_input('fit_params','x_key','filename')
wf.set_op_input('fit_params','y_key','fit_params')


pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','batch_saxs_fit.wfl'),wfmgr)

