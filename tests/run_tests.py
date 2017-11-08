from __future__ import print_function
import unittest
import os

import paws.api
import test_api
import test_op
import test_wfl
from paws.core import workflows as wfs

runner = unittest.TextTestRunner(verbosity=3)

print('======================================================================')
print('--- testing paws.api ---'+os.linesep)
api_tests = unittest.TestSuite()
api_tests.addTest(test_api.TestAPI('test_start_stop'))
runner.run(api_tests)
print(os.linesep+'--- done testing paws.api ---')
print('======================================================================')

# Start an API to use in subsequent tests
paw = paws.api.start()

print('======================================================================')
print('--- testing activation of operations ---'+os.linesep)
# Test paw.activate_op for all Operations
activate_op_tests = unittest.TestSuite()
for op_uri in paw._op_manager.list_ops():
    activate_op_tests.addTest(test_op.TestOp('test_activate_op',op_uri,paw))
activate_op_result = runner.run(activate_op_tests)
print(os.linesep+'--- done testing activation of operations ---')
print('======================================================================')

# Make a list of the Operations that could be activated
ops_skipped = [t[0].op_uri for t in activate_op_result.skipped]
ops_active = [opname for opname in paw._op_manager.list_ops() if opname not in ops_skipped]

print('======================================================================')
print('--- testing active Operations ---'+os.linesep)
# Test instantiation for all active Operations
op_tests = unittest.TestSuite()
for op_uri in ops_active:
    op_tests.addTest(test_op.TestOp('test_op',op_uri,paw))
op_result = runner.run(op_tests)
#
#print('======================================================================')
#op_run_tests = unittest.TestSuite()
#for op_uri in ops_active:
#    op_run_tests.addTest(test_op.TestOp('test_run',op_uri,paw))
#op_run_result = runner.run(op_run_tests)
#
print(os.linesep+'--- done testing active Operations ---')
print('======================================================================')

# TODO: Test plugins

print('======================================================================')
print('--- testing api for workflows ---'+os.linesep)
api_tests = unittest.TestSuite()
api_tests.addTest(test_api.TestAPI('test_add_wf',paw))
api_tests.addTest(test_api.TestAPI('test_add_op',paw))
api_tests.addTest(test_api.TestAPI('test_execute',paw))
api_tests.addTest(test_api.TestAPI('test_save',paw))
api_tests.addTest(test_api.TestAPI('test_load',paw))
runner.run(api_tests)
print(os.linesep+'--- done testing api for workflows ---')
print('======================================================================')

print('======================================================================')
print('--- testing packaged workflows ---'+os.linesep)
wfl_tests = unittest.TestSuite()
for wfl_uri,wfl_path in wfs.wfl_modules.items():
    wfl_tests.addTest(test_wfl.TestWfl('test_load_wfl',wfl_uri,paw))
runner.run(wfl_tests)
print('======================================================================')
wfl_run_tests = unittest.TestSuite()
for wfl_uri,wfl_path in wfs.wfl_modules.items():
    wfl_run_tests.addTest(test_wfl.TestWfl('test_run',wfl_uri,paw))
runner.run(wfl_run_tests)
print(os.linesep+'--- done testing packaged workflows ---')
print('======================================================================')

