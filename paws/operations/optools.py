"""Various tools for use in various Operations"""

import glob
import copy
from collections import Iterator
from collections import OrderedDict

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

    def __next__(self):
        return self.next()

