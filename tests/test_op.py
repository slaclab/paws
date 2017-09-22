import unittest

import paws.api
from paws.core.operations.Operation import Operation

class TestOp(unittest.TestCase):

    def __init__(self,test_name,op_uri,paw):
        super(TestOp,self).__init__(test_name)
        self.op_uri = op_uri
        self.paw = paw

    def test_activate_op(self):
        try:
            self.paw.activate_op(self.op_uri) 
        except ImportError as ex:
            msg = 'Caught ImportError: '\
            'missing packages for {}. '.format(self.op_uri)
            self.skipTest(msg)            

    def test_op(self):
        op = self.paw._op_manager.get_data_from_uri(self.op_uri)
        op = op()
        self.assertIsInstance(op,Operation)
    

