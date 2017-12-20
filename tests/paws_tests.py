from __future__ import print_function
import importlib
import unittest
import sys
import os

class TestAPI(unittest.TestCase):

    def __init__(self,methodname,paw=None):
        super(TestAPI,self).__init__(methodname)
        self.paw = paw

    def test_start_stop(self):
        import paws.api
        paw = paws.api.start()
        self.assertIsInstance(paw,paws.api.PawsAPI)

    def test_add_wf(self):
        from paws.core.workflows.Workflow import Workflow
        self.paw.add_wf('test')
        self.assertIsInstance(self.paw.get_wf('test'),Workflow)

    def test_add_op(self):
        from paws.core.operations.Operation import Operation
        self.paw.add_op('listprimes','TESTS.ListPrimes','test')
        self.assertIsInstance(self.paw.get_op('listprimes','test'),Operation)

    def test_execute(self):
        self.paw.execute('test')
        self.assertIsNotNone(self.paw.get_output('listprimes','primes_list','test'))
        print(self.paw.get_output('listprimes','primes_list'))

    def test_save(self):
        from paws.core import pawstools
        self.paw.save_to_wfl(os.path.join(pawstools.paws_scratch_dir,'test.wfl'))

    def test_load(self):
        from paws.core import pawstools
        self.paw.load_from_wfl(os.path.join(pawstools.paws_scratch_dir,'test.wfl'))


class TestPlugin(unittest.TestCase):

    def __init__(self,test_name,plugin_name,paw):
        super(TestPlugin,self).__init__(test_name)
        self.plugin_name = plugin_name 
        self.paw = paw

    def test_load(self):
        from paws.core.plugins.PawsPlugin import PawsPlugin
        print('loading {} ...'.format(self.plugin_name),end=''); sys.stdout.flush()
        pgin = self.paw.load_plugin(self.plugin_name)
        self.assertIsInstance(pgin(),PawsPlugin)

class TestOp(unittest.TestCase):

    def __init__(self,test_name,op_uri,paw):
        super(TestOp,self).__init__(test_name)
        self.op_uri = op_uri
        self.paw = paw

    def test_activate_op(self):
        print('activating {} ...'.format(self.op_uri),end=''); sys.stdout.flush()
        try:
            self.paw.activate_op(self.op_uri) 
        except ImportError as ex:
            msg = 'Caught ImportError: '\
            'may be missing dependencies for {}. '.format(self.op_uri)
            self.skipTest(msg)            

    def test_op(self):
        from paws.core.operations.Operation import Operation
        print('testing {} ...'.format(self.op_uri),end=''); sys.stdout.flush()
        op = self.paw._op_manager.get_data_from_uri(self.op_uri)
        op = op()
        self.assertIsInstance(op,Operation)
    
    def test_run(self):
        print('running {} ...'.format(self.op_uri),end=''); sys.stdout.flush()
        op = self.paw._op_manager.get_data_from_uri(self.op_uri)
        op = op()
        op.load_defaults()
        op.run() 

class TestWfl(unittest.TestCase):

    def __init__(self,test_name,wfl_uri,paw):
        super(TestWfl,self).__init__(test_name)
        self.wfl_uri = wfl_uri
        self.paw = paw
        #self.wf_name = 'test_'+self.wf_uri[self.wf_uri.rfind('.')+1:]

    def test_load_wfl(self):
        import paws.core.workflows as wfs 
        from paws.core.workflows.Workflow import Workflow
        print('loading {} ...'.format(self.wfl_uri),end=''); sys.stdout.flush()
        wfl_mod = importlib.import_module('.'+self.wfl_uri,wfs.__name__)
        self.paw.load_from_wfl(wfs.wfl_modules[self.wfl_uri]+'.wfl')
        for wf_name in wfl_mod.wf_names:
            wf = self.paw.get_wf(wf_name)
            self.assertIsInstance(wf,Workflow)

    def test_run(self):
        import paws.core.workflows as wfs 
        print('testing {} ...'.format(self.wfl_uri),end=''); sys.stdout.flush()
        wfl_mod = importlib.import_module('.'+self.wfl_uri,wfs.__name__)
        wfl_mod.test_setup(self.paw)
        results = wfl_mod.test_run(self.paw) 
        for r in results:
            self.assertIsInstance(r[0],r[1])

