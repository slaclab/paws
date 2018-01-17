from __future__ import print_function
import os
import glob
from collections import OrderedDict

import numpy as np

import paws
from paws.core import pawstools
from paws.core import plugins
from paws.core import operations
from paws.core import workflows 
from paws.core.plugins.PawsPlugin import PawsPlugin
from paws.core.workflows.WfManager import WfManager
from paws.core.workflows.Workflow import Workflow 
from paws.core.operations.Operation import Operation

def test_init():
    wf_manager = WfManager() 

def test_add_wf():
    wf_manager = WfManager() 
    wf_manager.add_workflow('test')
    assert isinstance(wf_manager.workflows['test'],Workflow)

def test_add_op():
    wf_manager = WfManager() 
    wf_test = wf_manager.add_workflow('test')
    test_listprimes = wf_manager.op_manager.get_operation('TESTS.ListPrimes')
    wf_test.add_operation('listprimes',test_listprimes)
    assert isinstance(test_listprimes,Operation)

def test_execute():
    wf_manager = WfManager() 
    wf_test = wf_manager.add_workflow('test')
    test_listprimes = wf_manager.op_manager.get_operation('TESTS.ListPrimes')
    wf_test.add_operation('listprimes',test_listprimes)
    wf_manager.run_workflow('test') 

def test_save():
    wf_manager = WfManager() 
    wf_test = wf_manager.add_workflow('test')
    test_listprimes = wf_manager.op_manager.get_operation('TESTS.ListPrimes')
    wf_test.add_operation('listprimes',test_listprimes)
    wfl_path = os.path.join(pawstools.paws_scratch_dir,'test.wfl')
    pawstools.save_to_wfl(wfl_path,wf_manager)

def test_load():
    wf_manager = WfManager()
    wfl_path = os.path.join(pawstools.paws_scratch_dir,'test.wfl') 
    pawstools.load_wfl(wfl_path,wf_manager)
    wf_manager.run_workflow('test') 

def test_get_output():
    wf_manager = WfManager()
    wfl_path = os.path.join(pawstools.paws_scratch_dir,'test.wfl') 
    pawstools.load_wfl(wfl_path,wf_manager)
    wf_manager.workflows['test'].connect_output('primes','listprimes.outputs.primes_list')
    wf_manager.run_workflow('test')
    p = wf_manager.workflows['test'].get_wf_output('primes')
    print(p)

def test_load_plugins():
    wf_manager = WfManager()
    for i,plugin_name in enumerate(plugins.plugin_name_list):
        print('loading {} ...'.format(plugin_name))
        pgin = wf_manager.plugin_manager.get_plugin(plugin_name)
        wf_manager.plugin_manager.add_plugin('plugin_'+str(i),plugin_name)
        assert isinstance(pgin,PawsPlugin)

def test_load_operations():
    wf_manager = WfManager()
    for op_module in wf_manager.op_manager.list_operations():
        print('loading {} ...'.format(op_module))
        op = wf_manager.op_manager.get_operation(op_module)
        assert isinstance(op,Operation)

def test_run_operations():
    wf_manager = WfManager()
    runnable_ops = dict.fromkeys(wf_manager.op_manager.list_operations())
    for op_module in wf_manager.op_manager.list_operations():
        print('running {} ...'.format(op_module))
        op = wf_manager.op_manager.get_operation(op_module)
        try:
            op.run()
        except Exception as ex:
            runnable_ops[op_module] = False
        runnable_ops[op_module] = True 
    return runnable_ops

def test_load_wfls():
    for wf_mod in workflows.wf_modules:
        wf_manager = WfManager()
        print('loading {} ...'.format(wf_mod))
        pawstools.load_packaged_wfl(wf_mod,wf_manager)

