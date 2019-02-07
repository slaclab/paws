from __future__ import print_function
from collections import OrderedDict
import socket 
import copy
from threading import Condition

from .PawsPlugin import PawsPlugin
from .. import pawstools

class CryoConController(PawsPlugin):

    def __init__(self,timer,host,port,channels,verbose=False,log_file=None):
        """Create a CryoConController.

        Parameters
        ----------
        timer : paws.plugins.Timer.Timer
            Timer plugin for triggering activities
            and initiating thread-safe data exchanges 
        host : str
            host name or IP address assigned to the CryoCon
        port : int
            integer port number for CryoCon connection 
        channels : dict
            dict mapping channel selection (strings "A"-"D")
            to control loop indices (integers 1-4 or None). 
            All channels will be read at each timer signal,
            and any channels assigned to control loops will be controlled.
        verbose : bool
        log_file : str
        """
        super(CryoConController,self).__init__(thread_blocking=True,verbose=verbose,log_file=log_file)
        self.timer = timer
        self.host = host
        self.port = port
        self.channels = channels
        self.socket_lock = Condition()
        self.sock = None
        self.state_lock = Condition()
        self.state = {} 

    @classmethod
    def clone(cls,timer,host,port,channels,verbose,log_file):
        return cls(timer,host,port,channels,verbose,log_file)

    def build_clone(self):
        cln = self.clone(self.timer,self.host,self.port,self.channels,self.verbose,self.log_file)
        return cln

    def start(self):
        super(CryoConController,self).start()

    def run(self):
        # executed by self.thread_clone in its own thread
        with self.socket_lock:
            self.sock = socket.create_connection((self.host,self.port)) 
        self.run_cmd('*idn?')
        keep_going = True

        self.update_status()

        while keep_going: 
            with self.timer.dt_lock:
                self.timer.dt_lock.wait()
            self.update_status()
            with self.timer.running_lock:
                if not self.timer.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        if self.verbose: self.message_callback('FINISHED')
        self.run_cmd('stop')
        with self.socket_lock:
            self.sock.close()

    def read_status(self):
        for chan in self.channels.keys():
            resp = self.run_cmd('input {}:temp?'.format(chan))
            with self.state_lock:
                self.state['T_read_{}'.format(chan)] = float(resp)

    def update_status(self):
        with self.state_lock:
            self.read_status()
        with self.proxy.state_lock:
            self.proxy.state = copy.deepcopy(self.state)
        #if self.verbose: self.message_callback('T_read: {}'.format(self.state['T_read']))

    def run_cmd(self,cmd):
        with self.socket_lock:
            self.send_line(cmd)
            resp = self.receive_line()
        if self.verbose: self.message_callback('{}: {}'.format(cmd,resp))
        #with self.proxy.history_lock:
        self.proxy.add_to_history(cmd+' '+resp)
        return resp

    def send_line(self, line):
        self.sock.sendall(bytearray((line+'\n').encode('utf-8')))

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip().decode()
        return bfr

    def set_units(self,channel,unit_str):
        cmd = 'input {}:units {}'.format(channel,unit_str)
        self.thread_clone.run_cmd(cmd)
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put(cmd)

    def loop_setup(self,channel,control_type='PID'):
        cmd = 'loop {}:source {};type {}'.format(self.channels[channel],channel,control_type)
        self.thread_clone.run_cmd(cmd)
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put(cmd)

    def set_temperature(self,channel,T_set):
        cmd = 'loop {}:setpt {}'.format(self.channels[channel],T_set)
        self.thread_clone.run_cmd(cmd)
        with self.thread_clone.state_lock:
            self.thread_clone.state['T_set_{}'.format(channel)] = T_set 
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put(cmd)

    def set_ramp_rate(self,channel,T_ramp):
        cmd = 'loop {}:rate {}'.format(self.channels[channel],T_ramp)
        self.thread_clone.run_cmd(cmd)
        with self.thread_clone.state_lock:
            self.thread_clone.state['T_ramp_{}'.format(channel)] = T_ramp 
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put(cmd)

    def start_control(self):
        self.thread_clone.run_cmd('control')
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put('control')
 
    def stop_control(self):
        with self.thread_clone.running_lock:
            self.thread_clone.run_cmd('stop')
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put('stop')
 
