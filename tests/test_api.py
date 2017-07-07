import unittest

class TestAPI(unittest.TestCase):

    def test_start_stop(self):
        print 'testing paws api start/stop'
        import paws.api
        paw = paws.api.start()
        self.assertIsNone(paw._current_wf_name)

if __name__ == '__main__':
    unittest.main()

