import os

import paws.api
from paws.core import pawstools

q_min = 0.04
q_max = 0.6
temperature_key = 'CTEMP'
header_regex = '*.txt'
bg_dir_path = ''
sample_dir_path = ''
nika_file_path = ''
new_files_only = False

paw = paws.api.start()

### (0) Activate all the ops that will be used
#paw.activate_op('IO.CALIBRATION.ReadPONI')
paw.activate_op('IO.CALIBRATION.NikaToPONI')
paw.activate_op('IO.FILESYSTEM.BuildFileList')
paw.activate_op('IO.FILESYSTEM.FileIterator')
paw.activate_op('PROCESSING.INTEGRATION.BuildPyFAIIntegrator')
paw.activate_op('EXECUTION.Batch')
paw.activate_op('EXECUTION.Realtime')
paw.activate_op('IO.BL15.ReadHeader_SSRL15')
paw.activate_op('IO.FILESYSTEM.BuildFilePath')
paw.activate_op('IO.IMAGE.FabIOOpen')
paw.activate_op('PACKAGING.BL15.TimeTempFromHeader')
paw.activate_op('PROCESSING.INTEGRATION.ApplyIntegrator1d')
paw.activate_op('PACKAGING.Window')
paw.activate_op('PROCESSING.BASIC.LogY')
paw.activate_op('PROCESSING.ZINGERS.EasyZingers1d')
paw.activate_op('PROCESSING.BACKGROUND.BgSubtractByTemperature')
paw.activate_op('IO.CSV.WriteArrayCSV')

### (1) Add workflows and name them
paw.add_wf('background_process')
paw.add_wf('sample_process')
paw.add_wf('main')

### (2a) Add operations to main workflow 
paw.select_wf('main')
paw.add_op('read_cal','IO.CALIBRATION.NikaToPONI')
paw.add_op('build_integrator','PROCESSING.INTEGRATION.BuildPyFAIIntegrator')
paw.add_op('background_files','IO.FILESYSTEM.BuildFileList')
paw.add_op('sample_files','IO.FILESYSTEM.FileIterator')
paw.add_op('background_batch','EXECUTION.Batch')
paw.add_op('sample_realtime','EXECUTION.Realtime')

### (2b) connect workflow IO for main workflow
paw.add_wf_input('background_dir','background_files.inputs.dir_path')
paw.set_input('background_files','dir_path',bg_dir_path)
paw.add_wf_input('nika_file','read_cal.inputs.file_path')
paw.set_input('read_cal','file_path',nika_file_path)
paw.add_wf_input('sample_dir','sample_files.inputs.dir_path')
paw.set_input('sample_files','dir_path',sample_dir_path)

### (2c) set up main workflow Operation IO 
paw.set_input('build_integrator','poni_dict','read_cal.outputs.poni_dict','workflow item')
paw.set_input('background_files','regex',header_regex)
paw.set_input('background_batch','work_item','background_process','entire workflow')
paw.set_input('background_batch','input_arrays',['background_files.outputs.file_list'],'workflow item')
paw.set_input('background_batch','input_keys',['header_file'])
paw.set_input('background_batch','static_inputs',['build_integrator.outputs.integrator'],'workflow item')
paw.set_input('background_batch','static_input_keys',['integrator'])
paw.set_input('sample_files','regex',header_regex)
paw.set_input('sample_files','new_files_only',new_files_only)
paw.set_input('sample_realtime','work_item','sample_process','entire workflow')
paw.set_input('sample_realtime','input_generators',['sample_files.outputs.file_iterator'],'workflow item')
paw.set_input('sample_realtime','input_keys',['header_file'])
#paw.set_input('sample_realtime','max_delay',100000)
paw.set_input('sample_realtime','static_inputs',
    ['build_integrator.outputs.integrator',
     'background_batch.outputs.batch_outputs'],
    'workflow item')
paw.set_input('sample_realtime','static_input_keys',
    ['integrator',
     'bg_batch_outputs'])

### (3a) add Operations to background_process workflow
paw.select_wf('background_process')
paw.add_op('read_header','IO.BL15.ReadHeader_SSRL15')
paw.add_op('image_file','IO.FILESYSTEM.BuildFilePath')
paw.add_op('read_image','IO.IMAGE.FabIOOpen')
paw.add_op('time_temp','PACKAGING.BL15.TimeTempFromHeader')
paw.add_op('integrate','PROCESSING.INTEGRATION.ApplyIntegrator1d')
paw.add_op('window','PACKAGING.Window')
paw.add_op('dezinger','PROCESSING.ZINGERS.EasyZingers1d')
paw.add_op('logI','PROCESSING.BASIC.LogY')
paw.add_op('write_csv','IO.CSV.WriteArrayCSV')

### (3b) connect workflow IO for background_process workflow
# path to header file
paw.add_wf_input('header_file','read_header.inputs.file_path')
paw.set_input('read_header','file_path',None)
# pyfai.AzimuthalIntegrator for integration operations:
# AzimthalIntegrators are not serializable,
# so specify this input to be loaded at runtime
paw.add_wf_input('integrator','integrate.inputs.integrator')
paw.set_input('integrate','integrator',None,'runtime')
# q-range for data windowing
paw.add_wf_input('q_min','window.inputs.x_min')
paw.add_wf_input('q_max','window.inputs.x_max')
paw.set_input('window','x_min',q_min)
paw.set_input('window','x_max',q_max)
# output directory
paw.add_wf_input('output_dir','write_csv.inputs.dir_path')
paw.set_input('write_csv','dir_path',bg_dir_path)
# key for getting temperature from header files
paw.add_wf_input('temperature_key','time_temp.inputs.temp_key')
paw.set_input('time_temp','temp_key',temperature_key)
# add workflow outputs for all relevant Operation outputs
paw.add_wf_output('temperature','time_temp.outputs.temperature')
paw.add_wf_output('q_I','integrate.outputs.q_I')
paw.add_wf_output('q_I_dz','dezinger.outputs.q_I_dz')
paw.add_wf_output('q_logI_dz','logI.outputs.x_logy')

### (3c) connect Operation IO for background_process workflow
paw.set_input('image_file','dir_path',bg_dir_path)
paw.set_input('image_file','filename','read_header.outputs.filename','workflow item')
paw.set_input('image_file','ext','tif')
paw.set_input('read_image','file_path','image_file.outputs.file_path','workflow item')
paw.set_input('time_temp','image_header','read_header.outputs.header_dict','workflow item')
paw.set_input('time_temp','time_key','time')
paw.set_input('integrate','image_data','read_image.outputs.image_data','workflow item')
paw.set_input('window','x_y','integrate.outputs.q_I','workflow item')
paw.set_input('dezinger','q_I','window.outputs.x_y_window','workflow item')
paw.set_input('logI','x_y','dezinger.outputs.q_I_dz','workflow item')
paw.set_input('write_csv','array','dezinger.outputs.q_I_dz','workflow item')
paw.set_input('write_csv','headers',['q (1/angstrom)','intensity (arb)'])
paw.set_input('write_csv','filename','read_image.outputs.filename','workflow item')
paw.set_input('write_csv','filetag','_dz')

### (4a) Add operations to sample_process workflow 
paw.select_wf('sample_process')
paw.add_op('read_header','IO.BL15.ReadHeader_SSRL15')
paw.add_op('image_file','IO.FILESYSTEM.BuildFilePath')
paw.add_op('read_image','IO.IMAGE.FabIOOpen')
paw.add_op('time_temp','PACKAGING.BL15.TimeTempFromHeader')
paw.add_op('integrate','PROCESSING.INTEGRATION.ApplyIntegrator1d')
paw.add_op('window','PACKAGING.Window')
paw.add_op('dezinger','PROCESSING.ZINGERS.EasyZingers1d')
paw.add_op('subtract_bg','PROCESSING.BACKGROUND.BgSubtractByTemperature')
paw.add_op('logI','PROCESSING.BASIC.LogY')
paw.add_op('write_csv','IO.CSV.WriteArrayCSV')
#paw.add_op('profile','PROCESSING.SAXS.SpectrumProfiler')
#paw.add_op('parameterize','PROCESSING.SAXS.SpectrumParameterization')
#paw.add_op('fit','PROCESSING.SAXS.SpectrumFit')
#paw.add_op('make_pif','PACKAGING.PIF.PifNPSolutionSAXS')

### (4b) connect workflow IO for sample_process workflow
# path to image file
paw.add_wf_input('header_file','read_header.inputs.file_path')
paw.set_input('read_header','file_path',None)
# pyfai.AzimuthalIntegrator for integration operations:
# AzimthalIntegrators are not serializable,
# so specify this input to be loaded at runtime
paw.add_wf_input('integrator','integrate.inputs.integrator')
paw.set_input('integrate','integrator',None,'runtime')
# q-range for data windowing
paw.add_wf_input('q_min','window.inputs.x_min')
paw.add_wf_input('q_max','window.inputs.x_max')
paw.set_input('window','x_min',q_min)
paw.set_input('window','x_max',q_max)
# outputs of the background_batch 
paw.add_wf_input('bg_batch_outputs','subtract_bg.inputs.bg_batch_outputs')
paw.set_input('subtract_bg','bg_batch_outputs',None)
paw.add_wf_input('output_dir','write_csv.inputs.dir_path')
paw.set_input('write_csv','dir_path',sample_dir_path)
# key for getting temperature from header files
paw.add_wf_input('temperature_key','time_temp.inputs.temp_key')
paw.set_input('time_temp','temp_key',temperature_key)
# add workflow outputs for all relevant Operation outputs
paw.add_wf_output('temperature','time_temp.outputs.temperature')
paw.add_wf_output('q_I','integrate.outputs.q_I')
paw.add_wf_output('q_I_dz','dezinger.outputs.q_I_dz')
paw.add_wf_output('q_I_dz_bgsub','subtract_bg.outputs.q_I_bgsub')
paw.add_wf_output('q_logI_dz_bgsub','logI.outputs.x_logy')
paw.add_wf_output('time','time_temp.outputs.time')

### (4c) connect Operation IO for sample_process workflow
paw.set_input('image_file','dir_path',sample_dir_path)
paw.set_input('image_file','filename','read_header.outputs.filename','workflow item')
paw.set_input('image_file','ext','tif')
paw.set_input('read_image','file_path','image_file.outputs.file_path','workflow item')
paw.set_input('time_temp','image_header','read_header.outputs.header_dict','workflow item')
paw.set_input('time_temp','time_key','time')
paw.set_input('time_temp','temp_key',temperature_key)
paw.set_input('integrate','image_data','read_image.outputs.image_data','workflow item')
paw.set_input('window','x_y','integrate.outputs.q_I','workflow item')
paw.set_input('dezinger','q_I','window.outputs.x_y_window','workflow item')
paw.set_input('subtract_bg','q_I_meas','dezinger.outputs.q_I_dz','workflow item')
paw.set_input('subtract_bg','T_meas','time_temp.outputs.temperature','workflow item')
paw.set_input('subtract_bg','q_I_bg_key','q_I_dz')
paw.set_input('subtract_bg','T_bg_key','temperature')
paw.set_input('logI','x_y','subtract_bg.outputs.q_I_bgsub','workflow item')
paw.set_input('write_csv','array','subtract_bg.outputs.q_I_bgsub','workflow item')
paw.set_input('write_csv','headers',['q (1/angstrom)','intensity (arb)'])
paw.set_input('write_csv','filename','read_image.outputs.filename','workflow item')
paw.set_input('write_csv','filetag','_dz_bgsub')

paw.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','saxs_realtime_ssrl15.wfl'))

