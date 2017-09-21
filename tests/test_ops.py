import unittest

import paws.api

class TestAPI(unittest.TestCase):

    def test_activate_ops(self):
        paw = paws.api.start()
        for op_uri in paw._op_manager.list_ops():
            paw.activate_op(op_uri) 

if __name__ == '__main__':
    unittest.main()

