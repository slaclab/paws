import unittest

from PySide import QtCore

import paws.api

class TestApp(unittest.TestCase):

    def test_start_stop(self):
        print 'testing paws application start/stop'
        paw = paws.api.start()
        t = QtCore.QTimer()
        t.setSingleShot(True)
        t.timeout.connect(paw._app.quit)
        t.start(0)
        excode = paw._app.exec_()
        self.assertEqual(excode,0)

if __name__ == '__main__':
    unittest.main()

