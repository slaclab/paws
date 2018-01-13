import os

import paws.api
from paws.core import pawstools

saxs_dir_path = '/scratch/2017_noel_saxs/all_data/'
data_rx = '*.sub'
#window_xmin = 0.04
#window_xmax = 0.6

paw = paws.api.start()

# Activate all the ops that will be used
paw.activate_op('EXECUTION.BATCH.BatchFromDirectory')
paw.activate_op('PACKAGING.Window')
paw.activate_op('PACKAGING.BATCH.XYDataFromBatch')
paw.activate_op('IO.NUMPY.Loadtxt_q_I_dI')
paw.activate_op('PROCESSING.BASIC.LogY')
paw.activate_op('PROCESSING.SAXS.SpectrumFit')

# Add workflows and name them
paw.add_wf('saxs_fit')
paw.add_wf('main')

paw.select_wf('saxs_fit')
paw.add_op('read','IO.NUMPY.Loadtxt_q_I_dI')
paw.add_op('window','PACKAGING.Window')
paw.add_op('logI','PROCESSING.BASIC.LogY')
paw.add_op('fit','PROCESSING.SAXS.SpectrumFit')
paw.add_op('logI_fit','PROCESSING.BASIC.LogY')

paw.set_input('read','file_path',None,'runtime')
paw.set_input('window','x_y','read.outputs.q_I','workflow item')
paw.set_input('window','x_min',0.02)
paw.set_input('window','x_max',0.35)
paw.set_input('logI','x_y','window.outputs.x_y_window','workflow item')
paw.set_input('fit','q_I','window.outputs.x_y_window','workflow item')
paw.set_input('fit','populations',{'guinier_porod':1})
paw.set_input('logI_fit','x_y','fit.outputs.q_I_opt','workflow item')

paw.add_wf_input('file_path','read.inputs.file_path')
paw.add_wf_output('q_I','read.outputs.q_I')
paw.add_wf_output('q_logI','logI.outputs.x_logy')
paw.add_wf_output('q_I_opt','fit.outputs.q_I_opt')
paw.add_wf_output('q_logI_opt','logI_fit.outputs.x_logy')


paw.select_wf('main')
paw.add_op('batch','EXECUTION.BATCH.BatchFromDirectory')
#paw.add_op('window','PACKAGING.Window')
#paw.add_op('write_csv','IO.CSV.WriteArrayCSV')

paw.set_input('batch','dir_path',saxs_dir_path)
paw.set_input('batch','regex',data_rx)
paw.set_input('batch','workflow','saxs_fit','entire workflow')
paw.set_input('batch','input_name','file_path')

# set up operation input-output routing
paw.save_to_wfl('/u/qb/lenson/WORK/paws/scratch/batch_gp_fit.wfl')
paw.execute()

