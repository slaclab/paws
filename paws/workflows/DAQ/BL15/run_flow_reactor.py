import os

from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()
wfmgr.add_workflow('main')
wfmgr.load_operations('main',
    set_rxn='CONTROL.PLUGINS.SetFlowReactor',
    stop_pumps='CONTROL.PLUGINS.StopPPumps')

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugins(
    timer='Timer',
    flow_reactor='FlowReactor',
    cryocon='CryoConController'
    )

pgmgr.connect('timer',['cryocon.inputs.timer','flow_reactor.inputs.timer'])
pgmgr.connect('cryocon','flow_reactor.inputs.cryocon')

wf = wfmgr.workflows['main']
wf.connect_input('recipe','set_rxn.inputs.recipe')
wf.connect_input('delay','set_rxn.inputs.delay')
wf.connect_plugin('flow_reactor','set_rxn.inputs.flow_reactor')
wf.connect_plugin('flow_reactor.inputs.ppumps','stop_pumps.inputs.ppumps')
wf.set_dependency('stop_pumps','set_rxn')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','run_flow_reactor.wfm'))

