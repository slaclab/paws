from collections import OrderedDict

from ...Operation import Operation

inputs=OrderedDict(
    ssh_file_copier=None,
    remote_dir=None,
    regex='*',
    local_dir=None)
outputs=OrderedDict(
    files_copied=[])

class SSHCopy(Operation):
    """Use SSHFileCopier Plugin to get files from remote filesystem"""

    def __init__(self):
        super(SSHCopy, self).__init__(inputs, outputs)
        self.input_doc['ssh_file_copier'] = 'SSHFileCopier plugin'
        self.input_doc['remote_dir'] = 'remote directory path (file source)'
        self.input_doc['regex'] = 'regular expression for selecting remote files'
        self.input_doc['local_dir'] = 'local directory path (file destination)'
        self.output_doc['files_copied'] = 'full (local) paths to files that were requested' 

    def run(self):
        rdir = self.inputs['remote_dir']
        rx = self.inputs['regex']
        ldir = self.inputs['local_dir']
        self.inputs['ssh_file_copier'].request_copy(rdir,rx,ldir)

