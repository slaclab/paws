import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# workflow names: 
wf_names = ['run_recipe','main']

op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()

op_maps['main']['batch_synthesis'] = 'EXECUTION.Realtime'

op_maps['run_recipe']['set_recipe'] = 'IO.SPEC.SetPPumps'

wfmgr = WfManager()
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)

# start plugins for synthesis recipe designer,
# p-pump controllers, SpecInfoClient
#
# plugin(s) p_pump_[0-N] : MitosPPumpController
#
pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('ppump1','MitosPPumpController')
pgmgr.add_plugin('ppump2','MitosPPumpController')

pgmgr.set_input('ppump1','serial_device','/dev/ttyUSB0')
pgmgr.set_input('ppump2','serial_device','/dev/ttyUSB1')

pgmgr.start_plugin('ppump1')
pgmgr.start_plugin('ppump2')

wf = wfmgr.workflows['main']
wf.set_op_input('batch_synthesis','work_item','run_recipe','entire workflow')
wf.set_op_input(
    'batch_synthesis','input_arrays',[
    [100,500],
    [500,100]
    ])
wf.set_op_input('batch_synthesis','input_keys',['recipe'])

wf = wfmgr.workflows['run_recipe']
# input 0: recipe (list of flow rates) 
wf.connect_input('recipe','set_recipe.inputs.set_points')
wf.set_op_input('set_recipe','set_points',None)
wf.set_op_input('set_recipe','pump_controllers',['ppump1.controller','ppump2.controller'],'plugin item')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','TESTS','test_ppumps.wfl'),wfmgr)
wfmgr.run_workflow('main')

