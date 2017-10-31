import unittest

class TestAPI(unittest.TestCase):

    def __init__(self,methodname,paw=None):
        super(TestAPI,self).__init__(methodname)
        self.paw = paw

    def test_start_stop(self):
        # smoke testing paws api
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
        import os
        from paws.core import pawstools
        self.paw.save_to_wfl(os.path.join(pawstools.paws_scratch_dir,'test.wfl'))

    def test_load(self):
        import os
        from paws.core import pawstools
        self.paw.load_from_wfl(os.path.join(pawstools.paws_scratch_dir,'test.wfl'))

if __name__ == '__main__':
    unittest.main()

