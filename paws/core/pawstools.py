import glob
import os
from collections import Iterator
from datetime import datetime as dt

from PySide import QtCore

# TODO: Make scratch directory and other cfg'ables into a cfg file

qdir = QtCore.QDir(__file__)
qdir.cdUp()
qdir.cdUp()
rootdir = qdir.absolutePath() 
qdir.cdUp()
sourcedir = qdir.absolutePath()
if not os.path.exists(os.path.join(qdir.absolutePath(),'scratch')):
    os.mkdir(os.path.join(qdir.absolutePath(),'scratch'))
qdir.cd('scratch')
scratchdir = qdir.absolutePath()
#print '[{}]: source directory sourcedir = {}'.format(__name__,sourcedir)
#print '[{}]: root directory rootdir = {}'.format(__name__,rootdir)
#print '[{}]: scratch directory scratchdir = {}'.format(__name__,scratchdir)

# Get the code version from the paws_config.py file, store as __version__
with open(os.path.join(sourcedir,'paws_config.py')) as f: 
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

def update_file(filename,d):
    """
    Save the items in dict d into filename,
    without removing members not included in d.
    """
    if os.path.exists(filename):
        f_old = open(filename,'r')
        d_old = yaml.load(f_old)
        f_old.close()
        d_old.update(d)
        d = d_old
    f = open(filename, 'w')
    yaml.dump(d, f)
    f.close()


