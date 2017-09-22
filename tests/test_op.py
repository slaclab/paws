import unittest

import paws.api

class TestOp(unittest.TestCase):

    def __init__(self,test_name,op_uri):
        super(TestOp,self).__init__(test_name)
        self.op_uri = op_uri

    def test_activate_op(self):
        paw = paws.api.start()
        paw.activate_op(self.op_uri) 
        
