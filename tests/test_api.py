import unittest

class TestAPI(unittest.TestCase):

    def test_start_stop(self):
        # smoke testing paws api
        import paws.api
        paw = paws.api.start()
        self.assertIsInstance(paw,paws.api.PawsAPI)

if __name__ == '__main__':
    unittest.main()

