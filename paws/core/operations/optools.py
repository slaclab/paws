"""
Various tools for working with Workflows and Operations
"""

import glob
import copy
from collections import Iterator
from collections import OrderedDict

from . import Operation as opmod 

class FileSystemIterator(Iterator):

    def __init__(self,dirpath,regex,include_existing_files=True):
        self.dirpath = dirpath
        self.rx = regex
        self.paths_done = []
        if not include_existing_files:
            self.paths_done = glob.glob(self.dirpath+'/'+self.rx)
        super(FileSystemIterator,self).__init__()

    def next(self):
        batch_list = glob.glob(self.dirpath+'/'+self.rx)
        for path in batch_list:
            if not path in self.paths_done:
                self.paths_done.append(path)
                return path
        return None

class ExecutionError(Exception):
    def __init__(self,msg):
        super(ExecutionError,self).__init__(self,msg)

def get_uri_from_dict(uri,d):
    keys = uri.split('.')
    itm = d
    for k in keys:
        if not isinstance(itm,dict):
            msg = 'something in {} is not a dict'.format(uri)
            raise KeyError(msg)
        if not k in itm.keys():
            msg = 'did not find uri {} in dict'.format(uri)
            raise KeyError(msg)
        else:
            itm = itm[k]
    return itm

def dict_contains_uri(uri,d):
    keys = uri.split('.')
    itm = d
    for k in keys:
        if not k in itm.keys():
            return False
        else:
            itm = itm[k]
    return True

