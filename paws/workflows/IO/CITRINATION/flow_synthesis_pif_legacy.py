import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('make_pif')
wfmgr.load_operations('make_pif',
    read_recipe='IO.YAML.LoadYAML',
    header_file='IO.FILESYSTEM.BuildFilePath', 
    read_header='IO.BL15.ReadHeader',
    time_temp='PACKAGING.BL15.TimeTempFromHeader',
    data_file='IO.FILESYSTEM.BuildFilePath',
    read_q_I='IO.NumpyLoad',
    populations_file='IO.FILESYSTEM.BuildFilePath',
    read_populations='IO.YAML.LoadXRSDFit',
    make_pif='PACKAGING.PIF.FlowSynthesisPIF',
    output_file='IO.FILESYSTEM.BuildFilePath',
    save_pif='IO.CITRINATION.SavePIF'
    )

wf = wfmgr.workflows['make_pif']

wf.connect_input('experiment_id','make_pif.inputs.experiment_id')
wf.connect_input('source_wavelength','make_pif.inputs.source_wavelength')
wf.connect_input('recipe_path','read_recipe.inputs.file_path')
wf.connect_input('header_dir','header_file.inputs.dir_path')
wf.connect_input('header_suffix','header_file.inputs.suffix')
wf.connect_input('header_ext','header_file.inputs.extension')
wf.set_input('header_ext','txt')
wf.connect_input('data_dir','data_file.inputs.dir_path')
wf.connect_input('data_suffix','data_file.inputs.suffix')
wf.connect_input('data_ext','data_file.inputs.extension')
wf.set_input('data_ext','dat')
wf.connect_input('populations_dir','populations_file.inputs.dir_path')
wf.connect_input('populations_suffix','populations_file.inputs.suffix')
wf.connect_input('populations_ext','populations_file.inputs.extension')
wf.set_input('populations_ext','yml')
wf.connect_input('output_dir','output_file.inputs.dir_path')
wf.connect_input('output_suffix','output_file.inputs.suffix')
wf.connect_input('output_ext','output_file.inputs.extension')
wf.set_input('output_suffix','_PIF')
wf.set_input('output_ext','json')

wf.connect_output('pif','make_pif.outputs.pif')

wf.connect('read_recipe.outputs.filename',[\
    'header_file.inputs.filename',\
    'data_file.inputs.filename',\
    'populations_file.inputs.filename',\
    'output_file.inputs.filename'])

wf.connect('header_file.outputs.file_path','read_header.inputs.file_path')
wf.connect('read_header.outputs.header_dict','time_temp.inputs.header_dict')
wf.set_op_inputs('time_temp',time_key='time',temperature_key='TEMP')

wf.connect('data_file.outputs.file_path','read_q_I.inputs.file_path')
wf.connect('populations_file.outputs.file_path','read_populations.inputs.file_path')

wf.connect('read_recipe.outputs.data','make_pif.inputs.recipe')
wf.connect('time_temp.outputs.time','make_pif.inputs.t_utc')
wf.connect('read_q_I.outputs.data','make_pif.inputs.q_I')
wf.connect('read_populations.outputs.populations','make_pif.inputs.populations')
wf.connect('output_file.outputs.file_path','save_pif.inputs.file_path')
wf.connect('make_pif.outputs.pif','save_pif.inputs.pif')

wfmgr.save_to_wfl('make_pif',os.path.join(pawstools.sourcedir,'workflows','CITRINATION','BL15','flow_synthesis_pif_legacy.wfl'))

