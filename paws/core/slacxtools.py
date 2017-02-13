import glob
import os.path
from collections import Iterator
from datetime import datetime as dt

from PySide import QtCore
from operations.slacxop import Operation

# TODO: Make scratch directory and other cfg'ables into a cfg file

version='0.4.0'

qdir = QtCore.QDir(__file__)
qdir.cdUp()
qdir.cdUp()
rootdir = qdir.path() 
qdir.cdUp()
if not os.path.exists(qdir.path()+'/scratch/'):
    os.mkdir(qdir.path()+'/scratch/')
qdir.cd('scratch')
scratchdir = qdir.path()
print '[slacxtools] scratch directory: {}'.format(scratchdir)
print '[slacxtools] root directory: {}'.format(rootdir)

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
        batch_list = glob.glob(self.dirpath+'/'+self.rx)
        for path in batch_list:
            if not path in self.paths_done:
                self.paths_done.append(path)
                return [path]
        return [None]

def dtstr():
    """Return date and time as a string"""
    return dt.strftime(dt.now(),'%Y %m %d, %H:%M:%S')

def timestr():
    """Return time as a string"""
    return dt.strftime(dt.now(),'%H:%M:%S')

