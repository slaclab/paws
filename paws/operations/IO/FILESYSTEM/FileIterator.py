from collections import OrderedDict
import glob

from ...Operation import Operation

inputs=OrderedDict(
    dir_path=None,
    regex='*',
    new_files_only=False)
outputs=OrderedDict(file_iterator=None)

class FileIterator(Operation):
    """Iterate over files matching a regex in a directory"""

    def __init__(self):
        super(FileIterator,self).__init__(inputs,outputs)
        self.input_doc['dir_path'] = 'path to directory containing files'
        self.input_doc['regex'] = 'regular expression to select files'
        self.input_doc['new_files_only'] = 'regular expression to select files'

    def run(self):
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        process_existing_files = not self.inputs['new_files_only']
        it = FileSystemIterator(dirpath,rx,process_existing_files) 
        self.outputs['file_iterator'] = it

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


