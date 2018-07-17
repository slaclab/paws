import os

from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()
wfmgr.add_workflow('run_reactor')
wfmgr.load_operations('run_reactor',

    set_recipe='DAQ.PLUGINS.SetFlowReactor',
    mar_expose='DAQ.PLUGINS.MarCCD_SISExpose',

    mar_image_path='IO.FILESYSTEM.BuildFilePath',
    collect_image='IO.FILESYSTEM.SSHCopy',

    local_image_path='IO.FILESYSTEM.BuildFilePath',
    header_file='IO.FILESYSTEM.BuildFilePath',
    recipe_file='IO.FILESYSTEM.BuildFilePath',

    get_reaction_data='DAQ.PLUGINS.ReadFlowReactor',
    get_T_sample='PACKAGING.GetValue',

    save_recipe='IO.YAML.SaveYAML',
    save_header='IO.YAML.SaveYAML',

    stop_reactor='DAQ.PLUGINS.StopFlowReactor')

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugins(
    timer='Timer',
    spec_infoclient='SpecInfoClient',
    cryocon='CryoConController', 
    flow_reactor='FlowReactor',
    mar_ssh_client='SSHClient'
    )

pgmgr.connect('timer',[\
    'cryocon.inputs.timer',\
    'flow_reactor.inputs.timer',\
    'spec_infoclient.inputs.timer',\
    'mar_ssh_client.inputs.timer'])
pgmgr.connect('cryocon','flow_reactor.inputs.cryocon')

wf = wfmgr.workflows['run_reactor']

wf.connect_input('recipe','set_recipe.inputs.recipe')
wf.connect_input('delay_time','set_recipe.inputs.delay_time')
wf.connect_input('delay_volume','set_recipe.inputs.delay_volume')
wf.connect_plugin('flow_reactor','set_recipe.inputs.flow_reactor')

wf.connect_input('filename_root',[\
    'mar_expose.inputs.filename',\
    'mar_image_path.inputs.filename'])
wf.connect_input('exposure_time',[\
    'mar_expose.inputs.exposure_time',
    'save_header.inputs.data.exposure_time']
    )
wf.connect_plugin('spec_infoclient','mar_expose.inputs.spec_infoclient')
wf.set_dependency('mar_expose','set_recipe')
wf.set_input('exposure_time',10)

wf.set_op_inputs('mar_image_path',
    dir_path='/home/data',
    suffix='_0001',
    extension='tif')
wf.set_op_inputs('local_image_path',extension='tif')

wf.connect_input('output_dir',[\
    'local_image_path.inputs.dir_path',
    'header_file.inputs.dir_path',
    'recipe_file.inputs.dir_path']
    )
wf.connect('mar_image_path.outputs.filename',[\
    'local_image_path.inputs.filename',
    'header_file.inputs.filename',
    'recipe_file.inputs.filename']
    )

wf.connect_plugin('mar_ssh_client','collect_image.inputs.ssh_client')
wf.connect('mar_image_path.outputs.file_path','collect_image.inputs.remote_path')
wf.connect('local_image_path.outputs.file_path','collect_image.inputs.local_path')
wf.connect_output('image_path','local_image_path.outputs.file_path')

wf.connect_plugin('flow_reactor','get_reaction_data.inputs.flow_reactor')
wf.connect_output('header_data','get_reaction_data.outputs.header')

wf.connect_input('T_sample_key','get_T_sample.inputs.key')
wf.connect('get_reaction_data.outputs.header','get_T_sample.inputs.data')
wf.connect_output('T_sample','get_T_sample.outputs.value')

wf.set_op_input('recipe_file','suffix','_recipe')
wf.set_op_input('header_file','suffix','')
wf.set_op_input('recipe_file','extension','yml')
wf.set_op_input('header_file','extension','yml')
wf.connect_output('recipe_file','recipe_file.outputs.file_path')
wf.connect_output('header_file','header_file.outputs.file_path')

wf.connect('get_reaction_data.outputs.recipe','save_recipe.inputs.data')
wf.connect('recipe_file.outputs.file_path','save_recipe.inputs.file_path')

wf.connect('get_reaction_data.outputs.header','save_header.inputs.data')
wf.connect('header_file.outputs.file_path','save_header.inputs.file_path')
wf.connect_input('source_wavelength','save_header.inputs.data.source_wavelength')
wf.set_dependency('get_reaction_data','mar_expose')

wf.connect_plugin('flow_reactor','stop_reactor.inputs.flow_reactor')
wf.set_dependency('stop_reactor',['save_recipe','save_header'])

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','run_flow_reactor.wfm'))

