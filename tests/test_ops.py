import unittest

import paws.api

class TestOps(unittest.TestCase):

    def test_activate_ops(self):
        paw = paws.api.start()
        for op_uri in paw._op_manager.list_ops():
            try:
                paw.activate_op(op_uri) 
            except ImportError:
                self.skipTest(u'Caught ImportError: '\
                'Python environment is not ready for {}'\
                .format(op_uri))

if __name__ == '__main__':
    unittest.main()
