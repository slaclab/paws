from __future__ import print_function
from collections import OrderedDict
import glob
import os
from threading import Condition

import paramiko

from .PawsPlugin import PawsPlugin

inputs = OrderedDict(
    username=None,
    hostname=None,
    password=None,
    port=22,
    private_key_file=None,
    timer=None)

# TODO: handle non-unix hosts

class SSHClient(PawsPlugin):
    """An SSH Client PawsPlugin"""

    def __init__(self):
        super(SSHClient,self).__init__(inputs)
        self.input_doc['username'] = 'remote user name'
        self.input_doc['hostname'] = 'remote host name'
        self.input_doc['password'] = 'user password on remote host'
        self.input_doc['port'] = 'port for ssh connection, default 22'
        self.input_doc['private_key_file'] = 'path to private RSA key file'
        self.input_doc['timer'] = 'Timer plugin to trigger activities'
        self.sshcl = None
        self.sftpcl = None
        self.thread_blocking = True
        self.copy_lock = Condition()
        self.transport_lock = Condition()

    def start(self):
        self.run_clone()
        # block until notification that the clone is running 
        with self.thread_clone.running_lock:
            self.thread_clone.running_lock.wait()

    def run(self):
        # this method is run by self.thread_clone 
        username = self.inputs['username']
        hostname = self.inputs['hostname']
        pw = self.inputs['password']
        port = self.inputs['port']
        pkey_file = self.inputs['private_key_file']
        tmr = self.inputs['timer']
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

        keep_going = True
        while keep_going:
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            #while self.commands.qsize() > 0: 
            #    cmd = self.commands.get()
            #    self.commands.task_done()
            #    if cmd[0] == 'copy':
            #        self.copy_files(cmd[1],cmd[2],cmd[3])
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        if self.verbose: self.message_callback('FINISHED')
        self.sshcl.close()

    #def request_copy(self,remote_dir,regex,local_dir,block=False):
    #    copy_cmd = ['copy',remote_dir,regex,local_dir]
    #    with self.thread_clone.command_lock:
    #        self.thread_clone.commands.put(copy_cmd)
    #    if block:
    #        if self.verbose: self.message_callback('blocking until files are copied')
    #        with self.thread_clone.copy_lock:
    #            self.thread_clone.copy_lock.wait()
    #        if self.verbose: self.message_callback('finished copy- unblocking')

    def copy_file(self,remote_path,local_path):
        keep_trying = True
        #n_tries = 1
        #while keep_trying:
        #    try:
        if self.verbose: self.message_callback('attempting to copy {}'.format(remote_path))
        with self.thread_clone.transport_lock:
            self.thread_clone.sftpcl.get(remote_path,local_path)
        if self.verbose: self.message_callback('finished copying to {}'.format(local_path))
        #    except:
        #        if n_tries > 10:
        #            keep_trying = False
        #        n_tries += 1
        #        if not keep_trying:
        #            raise RuntimeError('failed to copy {} to {}'.format(remote_path,local_path))
        #self.notify_locks([self.copy_lock])

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
