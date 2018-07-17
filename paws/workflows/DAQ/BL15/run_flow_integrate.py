import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.add_workflow('main')

wfmgr.load_packaged_wfm('DAQ.BL15.run_flow_reactor')
wfmgr.load_packaged_wfm('INTEGRATION.BL15.integrate')

wfmgr.load_operations('main',
    run_recipe = 'EXECUTION.Run',
    run_integrate = 'EXECUTION.Run')

wf = wfmgr.workflows['main']
wf.connect_workflow('run_reactor','run_recipe.inputs.work_item')
wf.connect_input('recipe','run_recipe.inputs.inputs.recipe')
wf.connect_input('delay','run_recipe.inputs.inputs.delay')
wf.connect_input('filename_root','run_recipe.inputs.inputs.filename_root')
wf.connect_input('exposure_time','run_recipe.inputs.inputs.exposure_time')
wf.connect_input('source_wavelength','run_recipe.inputs.inputs.source_wavelength')
wf.connect_input('output_dir','run_recipe.inputs.inputs.output_dir')

#wf.connect_input('calib_file','run_integrate.inputs.inputs.calib_file')
wf.connect_workflow('integrate','run_integrate.inputs.work_item')
wf.connect('run_recipe.outputs.outputs.header_file','run_integrate.inputs.inputs.header_file')
#wf.set_dependency('run_integrate','run_recipe')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','run_flow_integrate.wfm'))

