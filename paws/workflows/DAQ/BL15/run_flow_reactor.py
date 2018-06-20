import os

from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()
wfmgr.add_workflow('main')
wfmgr.load_operations('main',
    run_rxn='CONTROL.PLUGINS.SetFlowReactor',
    stop_cryo='CONTROL.PLUGINS.StopCryoCon',
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
wf.connect_input('recipe','run_rxn.inputs.recipe')
wf.connect_input('delay','run_rxn.inputs.delay')
wf.connect_plugin('flow_reactor','run_rxn.inputs.flow_reactor')
wf.connect_plugin('flow_reactor.inputs.ppumps','stop_pumps.inputs.ppumps')
wf.connect_plugin('cryocon','stop_cryo.inputs.cryocon')
wf.set_dependency('stop_pumps','run_rxn')
wf.set_dependency('stop_cryo','run_rxn')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','run_flow_reactor.wfm'))

