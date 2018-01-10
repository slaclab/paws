import os
from collections import OrderedDict

import paws.api
from paws.core import pawstools

paw = paws.api.start()
# name the workflows:
wf_names = ['saxs_gp_fit','batch_saxs_gp_fit']
# name the operations:
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
# name ops for batch workflow:
op_maps['batch_saxs_gp_fit']['Batch Execution'] = 'EXECUTION.Batch'
# name ops for processing workflow:
op_maps['saxs_gp_fit']['Read Data'] = 'IO.NUMPY.Loadtxt_q_I_dI'
op_maps['saxs_gp_fit']['Q-Window'] = 'PACKAGING.Window'
op_maps['saxs_gp_fit']['Log(I)'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_gp_fit']['Fit Spectrum'] = 'PROCESSING.SAXS.SpectrumFit'
op_maps['saxs_gp_fit']['Log(I_fit)'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_gp_fit']['Output CSV'] = 'IO.CSV.WriteArrayCSV'
# add the workflows and activate the operations:
for wf_name,op_map in op_maps.items():
    paw.add_wf(wf_name)
    for op_name,op_uri in op_map.items():
        paw.activate_op(op_uri)       

paw.select_wf('saxs_gp_fit')
for op_name,op_uri in op_maps['saxs_gp_fit'].items(): 
    paw.add_op(op_name,op_uri)

paw.set_input('Read Data','file_path',None)
paw.set_input('Read Data','delimiter',',')
paw.set_input('Q-Window','x_y','Read Data.outputs.q_I','workflow item')
paw.set_input('Q-Window','x_min',0.02)
paw.set_input('Q-Window','x_max',0.5)
paw.set_input('Log(I)','x_y','Q-Window.outputs.x_y_window','workflow item')
paw.set_input('Fit Spectrum','q_I','Q-Window.outputs.x_y_window','workflow item')
paw.set_input('Fit Spectrum','populations',{'guinier_porod':1})
paw.set_input('Log(I_fit)','x_y','Fit Spectrum.outputs.q_I_opt','workflow item')
paw.set_input('Output CSV','array','Fit Spectrum.outputs.q_I_opt','workflow item')
paw.set_input('Output CSV','headers',['q','I'])
paw.set_input('Output CSV','dir_path','Read Data.outputs.dir_path','workflow item')
paw.set_input('Output CSV','filename','Read Data.outputs.filename','workflow item')
paw.set_input('Output CSV','filetag','_fit')
# By default, deactivate the output operations
paw.disable_op('Output CSV')
# One workflow input is needed, for the file paths
paw.add_wf_input('file_path','Read Data.inputs.file_path')

paw.select_wf('batch_saxs_gp_fit')
for op_name,op_uri in op_maps['batch_saxs_gp_fit'].items(): 
    paw.add_op(op_name,op_uri)

paw.set_input('Batch Execution','work_item','saxs_gp_fit','entire workflow')
paw.set_input('Batch Execution','input_keys',['file_path'])
# The input array (list of file paths) will be loaded by Xi-cam at runtime
paw.set_input('Batch Execution','input_arrays',None)

paw.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','XICAM','batch_saxs_gp_fit.wfl'))

