import os
import glob
from collections import Iterator
from datetime import datetime as dt

from PySide import QtCore, QtUiTools
from PySide import QtCore

version='0.0.2'

qdir = QtCore.QDir(__file__)
qdir.cdUp()
rootdir = os.path.split( qdir.absolutePath() )[0]#+'/slacx'

class LazyCodeError(Exception):
    def __init__(self,msg):
        super(LazyCodeError,self).__init__(self,msg)

class FileSystemIterator(Iterator):

    def __init__(self,dirpath,regex):
        self.paths_done = []
        self.dirpath = dirpath
        self.rx = regex
        super(FileSystemIterator,self).__init__()

    def next(self):
        #import pdb; pdb.set_trace()
        batch_list = glob.glob(self.dirpath+'/'+self.rx)
        #print 'the batch list: '
        #print batch_list
        #print 'paths done: '
        #print self.paths_done 
        for path in batch_list:
            if not path in self.paths_done:
        #        print 'return [{}]'.format(path)
                self.paths_done.append(path)
                return [path]
        #print 'No paths to run.'
        #print 'the batch list: '
        #print batch_list
        #print 'paths done: '
        #print self.paths_done 
        return [None]

def throw_specific_error(msg):
    msg = 'something specific happened: ' + msg
    raise Exception(msg)

def start_message_ui():
    ui_file = QtCore.QFile(rootdir+"/slacxui/message.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    msg_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    msg_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    msg_ui.setWindowModality(QtCore.Qt.WindowModal)
    #msg_ui.setMaximumHeight(200)
    msg_ui.message_box.setReadOnly(True)
    msg_ui.ok_button.setText('OK')
    msg_ui.ok_button.clicked.connect(msg_ui.close)
    msg_ui.ok_button.clicked.connect(msg_ui.deleteLater)
    msg_ui.ok_button.setDefault(True)
    return msg_ui

def dtstr():
    """Return date and time as a string"""
    return dt.strftime(dt.now(),'%Y %m %d, %H:%M:%S')

def timestr():
    """Return time as a string"""
    return dt.strftime(dt.now(),'%H:%M:%S')




