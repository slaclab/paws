import os

from paws.workflows.INTEGRATION.Integrate import Integrate 
from paws.plugins.PluginManager import PluginManager
from paws import pawstools

tdd = os.path.join(pawstools.rootdir,'tests','test_data')

def test():
    pgmgr = PluginManager()
    pgmgr.add_plugin('integrator','PyFAIIntegrator')
    wf = Integrate()
    outs = wf.run_with(
        image_file = os.path.join(tdd,'images','test1.tif'),
        integrator = pgmgr.plugins['integrator'],
        n_points = 30,
        polz_factor = 0.9,
        calib_file = os.path.join(tdd,'calib','test.nika'),
        output_dir = os.path.join(tdd,'outputs')
        )
    return True

