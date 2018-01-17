from __future__ import print_function
import os
import glob
from collections import OrderedDict

import numpy as np

import paws
from paws.core import pawstools
from paws.core import operations as ops
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

#def test_load_plugins():
#        from paws.core.plugins.PawsPlugin import PawsPlugin
#        print('loading {} ...'.format(self.plugin_name),end=''); sys.stdout.flush()
#        pgin = self.paw.load_plugin(self.plugin_name)
#        self.assertIsInstance(pgin(),PawsPlugin)
#
#class TestOp(unittest.TestCase):
#
#    def __init__(self,test_name,op_uri,paw):
#        super(TestOp,self).__init__(test_name)
#        self.op_uri = op_uri
#        self.paw = paw
#
#    def test_activate_op(self):
#        print('activating {} ...'.format(self.op_uri),end=''); sys.stdout.flush()
#        try:
#            self.paw.activate_op(self.op_uri) 
#        except ImportError as ex:
#            msg = 'Caught ImportError: '\
#            'may be missing dependencies for {}. '.format(self.op_uri)
#            self.skipTest(msg)            
#
#    def test_op(self):
#        from paws.core.operations.Operation import Operation
#        print('testing {} ...'.format(self.op_uri),end=''); sys.stdout.flush()
#        op = self.paw._op_manager.get_data_from_uri(self.op_uri)
#        op = op()
#        self.assertIsInstance(op,Operation)
#    
#    def test_run(self):
#        print('running {} ...'.format(self.op_uri),end=''); sys.stdout.flush()
#        op = self.paw._op_manager.get_data_from_uri(self.op_uri)
#        op = op()
#        op.load_defaults()
#        op.run() 
#
#class TestWfl(unittest.TestCase):
#
#    def __init__(self,test_name,wfl_uri,paw):
#        super(TestWfl,self).__init__(test_name)
#        self.wfl_uri = wfl_uri
#        self.paw = paw
#        #self.wf_name = 'test_'+self.wf_uri[self.wf_uri.rfind('.')+1:]
#
#    def test_load_wfl(self):
#        import paws.core.workflows as wfs 
#        from paws.core.workflows.Workflow import Workflow
#        print('loading {} ...'.format(self.wfl_uri),end=''); sys.stdout.flush()
#        wfl_mod = importlib.import_module('.'+self.wfl_uri,wfs.__name__)
#        self.paw.load_from_wfl(wfs.wf_modules[self.wfl_uri]+'.wfl')
#        for wf_name in self.paw.list_wf_tags(): 
#            wf = self.paw.get_wf(wf_name)
#            self.assertIsInstance(wf,Workflow)
#
#    def test_run(self):
#        import paws.core.workflows as wfs 
#        print('testing {} ...'.format(self.wfl_uri),end=''); sys.stdout.flush()
#        wfl_mod = importlib.import_module('.'+self.wfl_uri,wfs.__name__)
#        #wfl_mod.test_setup(self.paw)
#        #results = wfl_mod.test_run(self.paw) 
#        #for r in results:
#        #    self.assertIsInstance(r[0],r[1])
#
