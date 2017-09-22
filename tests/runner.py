import unittest

import paws.api
import test_api
import test_op

suite = unittest.TestSuite()
paw = paws.api.start()

for op_uri in paw._op_manager.list_ops():
    suite.addTest(test_op.TestOp('test_activate_op',op_uri))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)


