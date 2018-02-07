import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# workflow names: 
wf_names = ['background_process','sample_process','run_recipe','main']

op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()

op_maps['main']['background_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['read_calibration'] = 'IO.CALIBRATION.ReadPONI'
op_maps['main']['build_integrator'] = 'PROCESSING.INTEGRATION.BuildPyFAIIntegrator'
op_maps['main']['background_batch'] = 'EXECUTION.Batch'
op_maps['main']['realtime_synthesis'] = 'EXECUTION.Realtime'

#op_maps['run_recipe']['set_recipe'] = 'IO.SPEC.SetPPumps'
#op_maps['run_recipe']['set_temperature'] = 'IO.SPEC.SetCryoCon'
#op_maps['run_recipe']['run_loopscan'] = 'IO.SPEC.LoopScan'
op_maps['run_recipe']['header_files'] = 'IO.FILESYSTEM.FileIterator'
op_maps['run_recipe']['background_data'] = 'PACKAGING.Copy'
op_maps['run_recipe']['build_integrator'] = 'PROCESSING.INTEGRATION.BuildPyFAIIntegrator'
op_maps['run_recipe']['realtime_analysis'] = 'EXECUTION.Realtime'
op_maps['run_recipe']['params_vs_t'] = 'PACKAGING.BATCH.XYDataFromBatch'
#op_maps['run_recipe']['synthesizer_update'] = 'PROCESSING.ML.UpdateNPDesigner'

op_maps['background_process']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['background_process']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['background_process']['image_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['background_process']['read_image'] = 'IO.IMAGE.FabIOOpen'
op_maps['background_process']['integrate'] = 'PROCESSING.INTEGRATION.ApplyIntegrator1d'
op_maps['background_process']['q_window'] = 'PACKAGING.Window'
op_maps['background_process']['dezinger'] = 'PROCESSING.ZINGERS.EasyZingers1d'
#op_maps['background_process']['log_I'] = 'PROCESSING.BASIC.LogY'
#op_maps['background_process']['output_CSV'] = 'IO.CSV.WriteArrayCSV'

op_maps['sample_process']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['sample_process']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['sample_process']['image_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['sample_process']['read_image'] = 'IO.IMAGE.FabIOOpen'
op_maps['sample_process']['integrate'] = 'PROCESSING.INTEGRATION.ApplyIntegrator1d'
op_maps['sample_process']['q_window'] = 'PACKAGING.Window'
op_maps['sample_process']['dezinger'] = 'PROCESSING.ZINGERS.EasyZingers1d'
op_maps['sample_process']['bg_subtract'] = 'PROCESSING.BACKGROUND.BgSubtractByTemperature'
op_maps['sample_process']['fit_spectrum'] = 'PROCESSING.SAXS.SpectrumFit'
#op_maps['sample_process']['output_CSV'] = 'IO.CSV.WriteArrayCSV'

wfmgr = WfManager()
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)

# start plugins for synthesis recipe designer,
# p-pump controllers, SpecInfoClient
#
# plugin np_synth_designer : SynthesisDesigner
#
# plugin spec_info_client : SpecInfoClient
#
# plugin(s) p_pump_[0-N] : MitosPPumpController
#


wf = wfmgr.workflows['main']

# input 0: path to PONI calibration file 
wf.set_op_input('read_calibration','file_path',None)
wf.connect_input('calib_file','read_calibration.inputs.file_path')

# input 1: path to background header files directory
wf.set_op_input('background_files','dir_path',None)
wf.connect_input('background_dir','background_files.inputs.dir_path')

# input 2: regex for background header files 
wf.set_op_input('background_files','regex','*.txt')
wf.connect_input('background_regex','background_files.inputs.regex')

wf.set_op_input('build_integrator','poni_dict','read_calibration.outputs.poni_dict','workflow item')

wf.set_op_input('background_batch','work_item','background_process','entire workflow')
wf.set_op_input('background_batch','input_arrays',['background_files.outputs.file_list'],'workflow item')
wf.set_op_input('background_batch','input_keys',['header_file'])
wf.set_op_input('background_batch','static_inputs',['build_integrator.outputs.integrator'],'workflow item')
wf.set_op_input('background_batch','static_input_keys',['integrator'])

wf.set_op_input('realtime_synthesis','work_item','run_recipe','entire workflow')
wf.set_op_input('realtime_synthesis','input_generators',['np_synth_designer'],'plugin item')
wf.set_op_input('realtime_synthesis','input_keys',['recipe_dict'])
wf.set_op_input('realtime_synthesis','static_inputs',
    ['read_calibration.outputs.poni_dict','background_batch.outputs.batch_outputs'],
    'workflow item')
wf.set_op_input('realtime_synthesis','static_input_keys',
    ['poni_dict','background_data'])
wf.set_op_input('realtime_synthesis','delay',1000)
#wf.set_op_input('realtime_synthesis','max_delay',1000000)
#wf.set_op_input('realtime_synthesis','max_iter','np_synth_designer.max_iter','plugin item')



wf = wfmgr.workflows['run_recipe']

# input 0: recipe dict 
wf.connect_input('recipe_dict','set_recipe.inputs.recipe_dict')
wf.set_op_input('set_recipe','recipe_dict',{})

# input 1: temperature set point 
wf.connect_input('temperature','set_temperature.inputs.T_set')
wf.set_op_input('set_temperature','T_set',25.)

# input 2: loop scan delay
wf.connect_input('scan_delay','run_loopscan.inputs.delay')
wf.set_op_input('run_loopscan','delay',10.)

# input 3: loop scan exposure time
wf.connect_input('exposure_time','run_loopscan.inputs.exposure_time')
wf.set_op_input('run_loopscan','exposure_time',10.)

# input 4: number of scans
wf.connect_input('n_scan',
    ['run_loopscan.inputs.n_scan','realtime_analysis.inputs.max_exec'])
wf.set_op_input('run_loopscan','n_scan',10)

# input 5: path to directory for header files 
wf.connect_input('header_dir',
    ['run_loopscan.inputs.header_dir','header_files.inputs.dir_path'])
wf.set_op_input('header_files','dir_path',None)

# input 6: calibration parameters 
wf.connect_input('poni_dict','build_integrator.inputs.poni_dict')
wf.set_op_input('build_integrator','poni_dict',None)

# input 7: background spectra data 
wf.connect_input('background_data','background_data.inputs.data')
wf.set_op_input('background_data','data',None)

wf.set_op_input('header_files','regex','*.txt')
wf.set_op_input('header_files','new_files_only',True)
wf.set_op_input('realtime_analysis','work_item','sample_process','entire workflow')
wf.set_op_input('realtime_analysis','input_generators',
    ['header_files.outputs.file_iterator'],'workflow item')
wf.set_op_input('realtime_analysis','input_keys',['header_file'])
wf.set_op_input('realtime_analysis','static_inputs',
    ['build_integrator.outputs.integrator',
     'background_data.outputs.data'],
    'workflow item')
wf.set_op_input('realtime_analysis','static_input_keys',
    ['integrator','background_data'])




wf = wfmgr.workflows['background_process']

# input 0: path to header file
wf.set_op_input('read_header','file_path',None)
wf.connect_input('header_file','read_header.inputs.file_path')

# input 1: image directory, in case separate from headers
wf.set_op_input('image_path','dir_path',None)
wf.connect_input('image_dir','image_path.inputs.dir_path')

# inputs 2 and 3: q-range for data windowing
# TODO: copy down from parent wf 
wf.set_op_input('q_window','x_min',0.0)
wf.set_op_input('q_window','x_max',1.0)
wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')

# input 4: key for fetching temperature from header dictionary 
wf.set_op_input('time_temp','temp_key','CTEMP')
wf.connect_input('temp_key','time_temp.inputs.temp_key')

# input 5: pyfai.AzimuthalIntegrator
# AzimthalIntegrators are not serializable,
# so specify this input as 'runtime' type
wf.set_op_input('integrate','integrator',None,'runtime')
wf.connect_input('integrator','integrate.inputs.integrator')

wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('q_I','integrate.outputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')

wf.set_op_input('image_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('image_path','ext','tif')
wf.set_op_input('read_image','file_path','image_path.outputs.file_path','workflow item')
wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('integrate','image_data','read_image.outputs.image_data','workflow item')
wf.set_op_input('q_window','x_y','integrate.outputs.q_I','workflow item')
wf.set_op_input('dezinger','q_I','q_window.outputs.x_y_window','workflow item')




wf = wfmgr.workflows['sample_process']

# input 0: path to header file
wf.set_op_input('read_header','file_path',None)
wf.connect_input('header_file','read_header.inputs.file_path')

# input 1: image directory, in case separate from headers
wf.set_op_input('image_path','dir_path',None)
wf.connect_input('image_dir','image_path.inputs.dir_path')

# inputs 2 and 3: q-range for data windowing
# TODO: copy down from parent wf 
wf.set_op_input('q_window','x_min',0.0)
wf.set_op_input('q_window','x_max',1.0)
wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')

# input 4: key for fetching temperature from header dictionary 
wf.set_op_input('time_temp','temp_key','CTEMP')
wf.connect_input('temp_key','time_temp.inputs.temp_key')

# input 5: pyfai.AzimuthalIntegrator
# AzimthalIntegrators are not serializable,
# so specify this input as 'runtime' type
wf.set_op_input('integrate','integrator',None,'runtime')
wf.connect_input('integrator','integrate.inputs.integrator')

# input 6: the outputs of the background batch 
wf.connect_input('background_data','bg_subtract.inputs.bg_batch_outputs')
wf.set_op_input('bg_subtract','bg_batch_outputs',None)

wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('q_I','integrate.outputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')
wf.connect_output('params','fit_spectrum.outputs.params')

wf.set_op_input('image_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('image_path','ext','tif')
wf.set_op_input('read_image','file_path','image_path.outputs.file_path','workflow item')
wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('integrate','image_data','read_image.outputs.image_data','workflow item')
wf.set_op_input('q_window','x_y','integrate.outputs.q_I','workflow item')
wf.set_op_input('dezinger','q_I','q_window.outputs.x_y_window','workflow item')
wf.set_op_input('bg_subtract','q_I_meas','dezinger.outputs.q_I_dz','workflow item')
wf.set_op_input('bg_subtract','T_meas','time_temp.outputs.temperature','workflow item')
wf.set_op_input('bg_subtract','q_I_bg_key','q_I_dz')
wf.set_op_input('bg_subtract','T_bg_key','temperature')
wf.set_op_input('fit_spectrum','q_I','bg_subtract.outputs.q_I_bgsub','workflow item')
wf.set_op_input('fit_spectrum','populations',{'guinier_porod':1,'spherical_normal':1})
#wf.set_op_input('fit_spectrum','params',None)
#wf.set_op_input('fit_spectrum','fixed_params',None)

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','BL15','ppump_np_synthesis.wfl'),wfmgr)

