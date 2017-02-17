import unittest

import paws

class TestApp(unittest.TestCase):

    def test_start_stop(self):
        print 'testing paws application start/stop'
        
        a=1
        self.assertEqual(a,1)
        # start application
        # stop application
        # assert exit code == ???
        #self.assertEqual('foo'.upper(), 'FOO')

    #def test_isupper(self):
    #    self.assertTrue('FOO'.isupper())
    #    self.assertFalse('Foo'.isupper())

    #def test_split(self):
    #    s = 'hello world'
    #    self.assertEqual(s.split(), ['hello', 'world'])
    #    # check that s.split fails when the separator is not a string
    #    with self.assertRaises(TypeError):
    #        s.split(2)

if __name__ == '__main__':
    unittest.main()
