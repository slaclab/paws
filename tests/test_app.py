import unittest

import paws

class TestApp(unittest.TestCase):

    def test_start_stop(self):
        print 'testing paws application start/stop'
        
        a=1
        self.assertEqual(a,1)
        # start application
        # stop application
        # assert exit code == 0

if __name__ == '__main__':
    unittest.main()

