from collections import OrderedDict

from ...Operation import Operation

inputs=OrderedDict(
    ssh_client=None,
    remote_path=None,
    local_path=None)
outputs=OrderedDict()

class SSHCopy(Operation):
    """Use SSHClient Plugin to get a file from remote filesystem"""

    def __init__(self):
        super(SSHCopy, self).__init__(inputs, outputs)
        self.input_doc['ssh_client'] = 'SSHClient plugin'
        self.input_doc['remote_path'] = 'remote file path (file source)'
        self.input_doc['local_path'] = 'local file path (file destination)'

    def run(self):
        rp = self.inputs['remote_path']
        lp = self.inputs['local_path']
        self.inputs['ssh_client'].copy_file(rp,lp)
        #self.inputs['ssh_client'].request_copy(rdir,rx,ldir,blk)

