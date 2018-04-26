from __future__ import print_function
from collections import OrderedDict
import glob
import copy
import os
import sys
from threading import Thread, Condition
if int(sys.version[0]) == 2:
    import Queue as queue
else:
    import queue 

import paramiko

from .PawsPlugin import PawsPlugin
from .. import pawstools

inputs = OrderedDict(
    username=None,
    hostname=None,
    password=None,
    port=22,
    private_key_file=None,
    timer=None,
    verbose=False)

class SSHFileCopier(PawsPlugin):
    """SSH Client for synchronizing a local directory to a remote one."""

    def __init__(self):
        super(SSHFileCopier,self).__init__(inputs)
        self.input_doc['username'] = 'remote user name'
        self.input_doc['hostname'] = 'remote host name'
        self.input_doc['password'] = 'user password on remote host'
        self.input_doc['port'] = 'port for ssh connection, default 22'
        self.input_doc['private_key_file'] = 'path to private RSA key file'
        self.input_doc['timer'] = 'Timer plugin to trigger activities'
        self.input_doc['verbose'] = 'If True, client prints activities'
        #self.input_doc['source_dir'] = 'path to remote directory to monitor'
        #self.input_doc['dest_dir'] = 'path to local directory to receive new files'
        #self.input_doc['sync_old_files'] = 'If true, copy any files '\
        #    'that are found in `source_dir` and not found in `dest_dir`'
        #self.input_doc['copy_new_files'] = 'If true, copy any files '\
        #    'that arrive in `source_dir` after the client is started'
        self.py_version = int(sys.version[0])
        self.running_lock = Condition()
        self.directory_lock = Condition()
        self.remote_dir = []
        self.local_dir = []
        self.commands = queue.Queue() 
        self.sshcl = None
        self.sftpcl = None
        self.thread_clone = None
        self.proxy = None

    def start(self):
        with self.running_lock:
            self.running = True
        self.thread_clone = self.build_clone()
        self.thread_clone.proxy = self
        th = Thread(target=self.thread_clone.run)
        th.start()
        # wait for notification that the client is connected
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
        vb = self.inputs['verbose']

        self.sshcl = paramiko.SSHClient()
        self.sshcl.load_system_host_keys()
        if pkey_file is not None:
            k = paramiko.RSAKey.from_private_key_file(pkey_file)
            self.sshcl.connect(hostname, port, pkey=k)
        else:
            self.sshcl.connect(hostname, port, username, pw)
        if vb: self.message_callback('SSH client connected to {} port {}'.format(hostname,port))
        with self.running_lock:
            self.run_notify()
        self.sftpcl = paramiko.SFTPClient.from_transport(self.sshcl.get_transport())

        # make initial file list
        #stdin, stdout, stderr = self.sshcl.exec_command('ls {}'.format(src_dir))
        #rdir_list = stdout.read().strip().split(os.linesep.encode())
        #ldir_list = glob.glob(os.path.join(dest_dir,'*'))
        #with self.directory_lock:
        #    self.remote_dir.extend(rdir_list)
        #    self.local_dir.extend(ldir_list)
        #with self.proxy.directory_lock:
        #    self.proxy.remote_dir.extend(copy.deepcopy(rdir_list))
        #    self.proxy.local_dir.extend(copy.deepcopy(ldir_list))

        # continue to check for new files until stopped
        keep_going = True
        while keep_going:
            with self.proxy.inputs['timer'].dt_lock:
                self.proxy.inputs['timer'].dt_lock.wait()
            #if vb: self.message_callback('checking for commands...')
            while self.commands.qsize() > 0: 
                cmd = self.commands.get()
                #if vb: self.message_callback('found command: {}'.format(cmd))
                self.commands.task_done()
                if cmd[0] == 'copy':
                    self.copy_files(cmd[1],cmd[2],cmd[3])
        #    if vb: self.message_callback('checking for new files...')
        #    self.get_new_files()
        #    
            with self.proxy.inputs['timer'].running_lock:
                if not self.proxy.inputs['timer'].running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        self.sshcl.close()

    def request_copy(self,remote_dir,regex,local_dir):
        #if self.inputs['verbose']: self.message_callback('requesting copy...')
        copy_cmd = ['copy',remote_dir,regex,local_dir]
        self.thread_clone.commands.put(copy_cmd)

    def copy_files(self,remote_dir,regex,local_dir):
        vb = self.inputs['verbose']
        rrx = os.path.join(remote_dir,regex)
        if vb: self.message_callback('attempting copy from {}'.format(rrx))
        stdin, stdout, stderr = self.sshcl.exec_command('ls {}'.format(rrx))
        rdir_list = stdout.read().strip().split(os.linesep.encode())
        ldir_list = glob.glob(os.path.join(local_dir,'*'))
        ldir_file_list = [os.path.split(fpath)[1] for fpath in ldir_list]
        #if vb: self.message_callback('current files: {}'.format(rdir_list))
        #print(rdir_list)
        #with self.directory_lock:
        for fpath in rdir_list:
            fn = os.path.split(fpath.decode())[1] 
            if fn in ldir_file_list:
                pass
                #if vb: self.message_callback('file exists locally: skipping {}'.format(fn))
            else:
                #self.remote_dir.append(fn) 
                #with self.proxy.directory_lock:
                #    # update the proxy's directory
                #    self.proxy.remote_dir.append(fn)
                if vb: self.message_callback('copying new file: {}'.format(fn))
                # use sftpcl to move the file over
                #if copy_new: 
                self.sftpcl.get(os.path.join(remote_dir,fn),os.path.join(local_dir,fn))

    def run_notify(self):
        if int(self.py_version) == 2:
            self.running_lock.notifyAll()
        else:
            self.running_lock.notify_all()

    #def get_plugin_content(self):
    #    with self.directory_lock:
    #        ldir = copy.deepcopy(self.local_dir)
    #        rdir = copy.deepcopy(self.remote_dir)
    #    return {'remote_dir':rdir,'local_dir':ldir}


