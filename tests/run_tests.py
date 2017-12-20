from __future__ import print_function
import unittest
import os

import paws.api
from paws.core import workflows as wfs
from paws.core import plugins 
import paws_tests as pt

runner = unittest.TextTestRunner(verbosity=3)

print('--- testing paws.api ---'+os.linesep)
api_tests = unittest.TestSuite()
api_tests.addTest(pt.TestAPI('test_start_stop'))
runner.run(api_tests)

# Start an API to use in subsequent tests
paw = paws.api.start()

print('--- testing activation of operations ---'+os.linesep)
activate_op_tests = unittest.TestSuite()
for op_uri in paw._op_manager.list_ops():
    activate_op_tests.addTest(pt.TestOp('test_activate_op',op_uri,paw))
activate_op_result = runner.run(activate_op_tests)

# Make a list of the Operations that could be activated
ops_skipped = [t[0].op_uri for t in activate_op_result.skipped]
ops_active = [opname for opname in paw._op_manager.list_ops() if opname not in ops_skipped]

print('--- testing active Operations ---'+os.linesep)
# Test instantiation for all active Operations
op_tests = unittest.TestSuite()
for op_uri in ops_active:
    op_tests.addTest(pt.TestOp('test_op',op_uri,paw))
runner.run(op_tests)

print('--- testing activation of PawsPlugins ---'+os.linesep)
plugin_tests = unittest.TestSuite()
for pgin_name in plugins.plugin_name_list:
    plugin_tests.addTest(pt.TestPlugin('test_load',pgin_name,paw))
runner.run(plugin_tests)

print('--- testing api for workflows ---'+os.linesep)
api_tests = unittest.TestSuite()
api_tests.addTest(pt.TestAPI('test_add_wf',paw))
api_tests.addTest(pt.TestAPI('test_add_op',paw))
api_tests.addTest(pt.TestAPI('test_execute',paw))
api_tests.addTest(pt.TestAPI('test_save',paw))
api_tests.addTest(pt.TestAPI('test_load',paw))
runner.run(api_tests)

print('--- testing packaged workflows ---'+os.linesep)
wfl_tests = unittest.TestSuite()
for wfl_uri,wfl_path in wfs.wfl_modules.items():
    wfl_tests.addTest(pt.TestWfl('test_load_wfl',wfl_uri,paw))
runner.run(wfl_tests)

wfl_run_tests = unittest.TestSuite()
for wfl_uri,wfl_path in wfs.wfl_modules.items():
    wfl_run_tests.addTest(pt.TestWfl('test_run',wfl_uri,paw))
runner.run(wfl_run_tests)

