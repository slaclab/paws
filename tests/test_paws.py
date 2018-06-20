from __future__ import print_function
import os
import glob
from collections import OrderedDict

import numpy as np

import paws
from paws import pawstools
from paws import plugins
from paws import operations
from paws import workflows 
from paws.plugins.PawsPlugin import PawsPlugin
from paws.workflows.WfManager import WfManager
from paws.workflows.Workflow import Workflow 
from paws.operations.Operation import Operation

def test_init():
    wf_manager = WfManager() 

def test_add_wf():
    wf_manager = WfManager() 
    wf_manager.add_workflow('test')

def test_add_op():
    wf_manager = WfManager() 
    wf_manager.add_workflow('test')
    wf_manager.load_operation('test','listprimes','TESTS.ListPrimes')

def test_execute():
    wf_manager = WfManager() 
    wf_manager.add_workflow('test')
    wf_manager.load_operation('test','listprimes','TESTS.ListPrimes')
    wf_manager.run_workflow('test') 

def test_save():
    wf_manager = WfManager() 
    wf_test = wf_manager.add_workflow('test')
    wf_manager.load_operation('test','listprimes','TESTS.ListPrimes')
    wfm_path = os.path.join(pawstools.paws_scratch_dir,'test.wfm')
    wf_manager.save_to_wfm(wfm_path)

def test_load():
    wf_manager = WfManager()
    wfm_path = os.path.join(pawstools.paws_scratch_dir,'test.wfm') 
    wf_manager.load_wfm(wfm_path)
    wf_manager.run_workflow('test') 

def test_get_output():
    wf_manager = WfManager()
    wfm_path = os.path.join(pawstools.paws_scratch_dir,'test.wfm') 
    wf_manager.load_wfm(wfm_path)
    wf_manager.workflows['test'].connect_output('primes','listprimes.outputs.primes_list')
    wf_manager.run_workflow('test')
    p = wf_manager.workflows['test'].get_output('primes')
    print('list of primes: {}'.format(p))

def test_load_plugins():
    wf_manager = WfManager()
    for i,plugin_name in enumerate(plugins.plugin_name_list):
        print('loading {} ...'.format(plugin_name))
        wf_manager.plugin_manager.add_plugin('test_'+plugin_name,plugin_name)

def test_load_operations():
    wf_manager = WfManager()
    for op_module in wf_manager.op_manager.list_operations():
        print('loading {} ...'.format(op_module))
        op = wf_manager.op_manager.get_operation(op_module)
        assert isinstance(op,Operation)

def test_run_operations():
    # TODO: build default inputs for Operations
    wf_manager = WfManager()
    runnable_ops = dict.fromkeys(wf_manager.op_manager.list_operations())
    for op_module in wf_manager.op_manager.list_operations():
        op = wf_manager.op_manager.get_operation(op_module)
        try:
            print('running {} ...'.format(op_module))
            op.run()
            runnable_ops[op_module] = True 
        except Exception as ex:
            runnable_ops[op_module] = False
            print('{} does not run.'.format(op_module))
    return runnable_ops

# TODO: automate loading of wf module list
wfl_modules = [\
    'FITTING.BL15.read_and_fit',
    'IO.BL15.read_header']
wfm_modules = ['FITTING.BL15.timeseries_fit']
def test_load_wfms():
    #for wf_mod in workflows.wf_modules:
    for iw,wm in enumerate(wfl_modules):
        wf_manager = WfManager()
        print('loading {} ...'.format(wm))
        wf_manager.load_packaged_workflow('test_wf_{}'.format(iw),wm)
    for wm in wfm_modules:
        wf_manager = WfManager()
        print('loading {} ...'.format(wm))
        wf_manager.load_packaged_wfm(wm)

