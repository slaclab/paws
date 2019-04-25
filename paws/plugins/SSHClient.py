from threading import Condition
import time

import paramiko

from .PawsPlugin import PawsPlugin

# TODO: handle non-unix hosts

class SSHClient(PawsPlugin):
    """An SSH Client PawsPlugin"""

    def __init__(self,username,hostname,port,password='',private_key_file='',verbose=False,log_file=None):
        """Create a SSHClient plugin.

        Parameters
        ----------
        username : str
            user name for account on remote host
        hostname : str
            network id of remote host
        port : int
            port for ssh connection, default 22
        password : str
            user password on remote host
        private_key_file : str
            path to private RSA key file
        verbose : bool
        log_file : str
        """
        super(SSHClient,self).__init__(verbose=verbose,log_file=log_file)
        self.username = username
        self.hostname = hostname
        self.port = port 
        self.password = password
        self.private_key_file = private_key_file
        self.sshcl = None
        self.sftpcl = None
        self.transport_lock = Condition()

    def start(self):
        if self.verbose: self.message_callback('Setting up SSH client...')
        with self.transport_lock:
            self.sshcl = paramiko.SSHClient()
            self.sshcl.load_system_host_keys()
            self.sshcl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.private_key_file:
                k = paramiko.RSAKey.from_private_key_file(self.private_key_file)
                self.sshcl.connect(self.hostname, self.port, pkey=k)
            else:
                self.sshcl.connect(self.hostname, self.port, self.username, self.password)
            self.sftpcl = paramiko.SFTPClient.from_transport(self.sshcl.get_transport())
        if self.verbose: self.message_callback('SSH client connected to {} port {}'.format(self.hostname,self.port))
        super(SSHClient,self).start()

    def stop(self):
        self.close_ssh()
        super(SSHClient,self).stop() 

    def close_ssh(self):
        with self.transport_lock:
            if self.sshcl:
                self.sshcl.close()
                self.sshcl = None

    def copy_file(self,remote_path,local_path):
        if self.verbose: self.message_callback('attempting to copy {}'.format(remote_path))
        try_again = True
        n_tries = 0
        with self.transport_lock:
            while try_again:
                try:
                    self.sftpcl.get(remote_path,local_path)
                    try_again = False
                except:
                    n_tries += 1
                    time.sleep(1.)
                    if n_tries > 100:
                        self.message_callback('failed to copy {}'.format(remote_path))
                        try_again = False
                    else:
                        self.message_callback('attempt {} to copy {}'.format(n_tries,remote_path))
        if self.verbose: self.message_callback('finished copying to {}'.format(local_path))

