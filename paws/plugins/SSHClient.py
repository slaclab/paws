from __future__ import print_function
from collections import OrderedDict
import glob
import os
from threading import Condition

import paramiko

from .PawsPlugin import PawsPlugin

content = OrderedDict(
    username=None,
    hostname=None,
    password=None,
    port=22,
    private_key_file=None)

# TODO: handle non-unix hosts

class SSHClient(PawsPlugin):
    """An SSH Client PawsPlugin"""

    def __init__(self):
        super(SSHClient,self).__init__(content)
        self.content_doc['username'] = 'remote user name'
        self.content_doc['hostname'] = 'remote host name'
        self.content_doc['password'] = 'user password on remote host'
        self.content_doc['port'] = 'port for ssh connection, default 22'
        self.content_doc['private_key_file'] = 'path to private RSA key file'
        self.sshcl = None
        self.sftpcl = None
        self.thread_blocking = True
        #self.copy_lock = Condition()
        self.transport_lock = Condition()

    def start(self):
        super(SSHClient,self).start()
        # block until notification that the clone is running 
        with self.thread_clone.running_lock:
            self.thread_clone.running_lock.wait()

    def run(self):
        # this method is run by self.thread_clone 
        username = self.content['username']
        hostname = self.content['hostname']
        pw = self.content['password']
        port = self.content['port']
        pkey_file = self.content['private_key_file']
        with self.transport_lock:
            self.sshcl = paramiko.SSHClient()
            self.sshcl.load_system_host_keys()
            if pkey_file is not None:
                k = paramiko.RSAKey.from_private_key_file(pkey_file)
                self.sshcl.connect(hostname, port, pkey=k)
            else:
                self.sshcl.connect(hostname, port, username, pw)
            self.sftpcl = paramiko.SFTPClient.from_transport(self.sshcl.get_transport())
        if self.verbose: self.message_callback('SSH client connected to {} port {}'.format(hostname,port))
        self.run_notify()

    def stop(self):
        super(SSHClient,self).stop() 
        if self.thread_clone:
            self.thread_clone.close_ssh()

    def close_ssh(self):
        with self.transport_lock:
            if self.sshcl:
                self.sshcl.close()
                self.sshcl = None

    def copy_file(self,remote_path,local_path):
        if self.verbose: self.message_callback('attempting to copy {}'.format(remote_path))
        try_again = True
        n_tries = 0
        with self.thread_clone.transport_lock:
            while try_again:
                try:
                    self.thread_clone.sftpcl.get(remote_path,local_path)
                    try_again = False
                except:
                    n_tries += 1
                    if n_tries > 10:
                        self.message_callback('failed to copy {}'.format(remote_path))
                        try_again = False
                    else:
                        self.message_callback('attempt {} to copy {}'.format(n_tries,remote_path))
        if self.verbose: self.message_callback('finished copying to {}'.format(local_path))

#    def sync_files(self,remote_dir,regex,local_dir,overwrite=False):
#        rrx = os.path.join(remote_dir,regex)
#        if self.verbose: self.message_callback('attempting copy from {}'.format(rrx))
#        stdin, stdout, stderr = self.sshcl.exec_command('ls {}'.format(rrx))
#        rdir_list = stdout.read().strip().split(os.linesep.encode())
#        ldir_list = glob.glob(os.path.join(local_dir,'*'))
#        ldir_file_list = [os.path.split(fpath)[1] for fpath in ldir_list]
#        #if self.verbose: self.message_callback('current files: {}'.format(rdir_list))
#        #print(rdir_list)
#        #with self.directory_lock:
#        for fpath in rdir_list:
#            fn = os.path.split(fpath.decode())[1] 
#            if fn in ldir_file_list:
#                if overwrite:
#                    if self.verbose: self.message_callback('overwriting file: {}'.format(fn))
#                    self.sftpcl.get(os.path.join(remote_dir,fn),os.path.join(local_dir,fn))
#                else:
#                    if self.verbose: self.message_callback('{} exists locally: skipping copy'.format(fn))
#            else:
#                #self.remote_dir.append(fn) 
#                #with self.proxy.directory_lock:
#                #    # update the proxy's directory
#                #    self.proxy.remote_dir.append(fn)
#                if self.verbose: self.message_callback('copying new file: {}'.format(fn))
#                self.sftpcl.get(os.path.join(remote_dir,fn),os.path.join(local_dir,fn))
#        self.notify_locks([self.copy_lock])
#
