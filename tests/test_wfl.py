from __future__ import print_function
import importlib
import unittest
import sys

import paws.api
import paws.core.workflows as wfs 
from paws.core.workflows.Workflow import Workflow

class TestWfl(unittest.TestCase):

    def __init__(self,test_name,wfl_uri,paw):
        super(TestWfl,self).__init__(test_name)
        self.wfl_uri = wfl_uri
        self.paw = paw
        #self.wf_name = 'test_'+self.wf_uri[self.wf_uri.rfind('.')+1:]

    def test_load_wfl(self):
        print('loading {} ...'.format(self.wfl_uri),end=''); sys.stdout.flush()
        wfl_mod = importlib.import_module('.'+self.wfl_uri,wfs.__name__)
        self.paw.load_from_wfl(wfs.wfl_modules[self.wfl_uri]+'.wfl')
        for wf_name in wfl_mod.wf_names:
            wf = self.paw.get_wf(wf_name)
            self.assertIsInstance(wf,Workflow)

    def test_run(self):
        print('testing {} ...'.format(self.wfl_uri),end=''); sys.stdout.flush()
        wfl_mod = importlib.import_module('.'+self.wfl_uri,wfs.__name__)
        wfl_mod.test_setup(self.paw)
        results = wfl_mod.test_run(self.paw) 
        for r in results:
            self.assertIsInstance(r[0],r[1])

