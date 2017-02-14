import glob
import os
from collections import Iterator
from datetime import datetime as dt

from PySide import QtCore
from operations.operation import Operation

# TODO: Make scratch directory and other cfg'ables into a cfg file

qdir = QtCore.QDir(__file__)
qdir.cdUp()
qdir.cdUp()
rootdir = qdir.path() 
qdir.cdUp()
sourcedir = qdir.path()
if not os.path.exists(os.path.join(qdir.path(),'scratch')):
    os.mkdir(os.path.join(qdir.path(),'scratch'))
qdir.cd('scratch')
scratchdir = qdir.path()
print '[{}]: source directory sourcedir = {}'.format(__name__,sourcedir)
print '[{}]: root directory rootdir = {}'.format(__name__,rootdir)
print '[{}]: scratch directory scratchdir = {}'.format(__name__,scratchdir)

# Get the code version from the version.py file, store as __version__
with open(os.path.join(sourcedir,'version.py')) as f: 
    exec(f.read())
version=__version__

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

