import paws.api

bg_input_dir = '/home/lenson/WORK/saxs/liheng_20161118/ODE/reduced_data/' 
img_input_dir = '/home/lenson/WORK/saxs/liheng_20161118/R5/reduced_data/'
img_output_dir = '/home/lenson/WORK/saxs/liheng_20161118/R5/reduced_data/'

mypaw = paws.api.start()

# Start a workflow, name it
mypaw.add_wf('batch_bg_subtract')

# Instantiate operations, name them, add them to the workflow
mypaw.add_op('bg_read_batch','EXECUTION.BATCH.BatchFromFiles')
mypaw.add_op('read_bg','IO.CSV.CSVToArray')
mypaw.add_op('bg_header_file_path','IO.BuildFilePath')
mypaw.add_op('bg_time_temp','PACKAGING.BL1-5.TimeTempFromHeader')

mypaw.add_op('img_read_batch','EXECUTION.BATCH.BatchFromFiles')
mypaw.add_op('read_img','IO.CSV.CSVToArray')
mypaw.add_op('img_time_temp','PACKAGING.BL1-5.TimeTempFromHeader')

mypaw.add_op('bg_subtract_batch','EXECUTION.BATCH.BatchPostProcess')
mypaw.add_op('bg_subtract','PROCESSING.BACKGROUND.BgSubtractByTemperature')
mypaw.add_op('output_file_path','IO.BuildFilePath')
mypaw.add_op('write_csv','IO.CSV.WriteArrayCSV')

# Set up the input routing: 
mypaw.set_input('read_cal', 'nika_file',
src='filesystem', tp='path', val='/home/lenson/WORK/saxs/liheng_20161118/AgBe.nika')

mypaw.set_input('read_img', 'path', src='batch')

mypaw.set_input('cal_reduce', 'poni_dict',
src='workflow', tp='reference', val='read_cal.outputs.poni_dict')
mypaw.set_input('cal_reduce', 'image_data',
src='workflow', tp='reference', val='read_img.outputs.image_data')

mypaw.set_input('window','x',
src='workflow', tp='reference', val='cal_reduce.outputs.q')
mypaw.set_input('window','y',
src='workflow', tp='reference', val='cal_reduce.outputs.I')
mypaw.set_input('window','x_min', src='text', tp='float', val=0.04)
mypaw.set_input('window','x_max', src='text', tp='float', val=0.6)

mypaw.set_input('write_csv','array',
src='workflow', tp='reference', val='window.outputs.x_y_window')
mypaw.set_input('write_csv','headers',
src='text',tp='string',val=['q (1/Angstrom)','Intensity (counts)'])
mypaw.set_input('write_csv','dir_path',
src='filesystem',tp='path',val=csv_output_dir)
mypaw.set_input('write_csv','filename',
src='workflow',tp='reference',val='read_img.outputs.filename')
#mypaw.set_input('write_csv','filetag',
#src='text',tp='string',val='')

mypaw.set_input('batch','dir_path',
src='filesystem', tp='path', val=tif_input_dir)
mypaw.set_input('batch','regex',
src='text', tp='string', val='*.tif')
mypaw.set_input('batch','input_route',
src='workflow', tp='path', val='read_img.inputs.path')
mypaw.set_input('batch','batch_ops',
src='workflow', tp='path', val=['read_img','cal_reduce','window','write_csv'])
mypaw.set_input('batch','saved_items',
src='workflow', tp='path', val=['window.outputs.x_y_window'])

#mypaw.save_workflow('/home/lenson/WORK/paws/scratch/batch_calreduce.wfl')

mypaw.execute()


