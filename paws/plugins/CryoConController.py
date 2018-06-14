from __future__ import print_function
from collections import OrderedDict
import socket 
from threading import Condition

from .PawsPlugin import PawsPlugin
from .. import pawstools

inputs = OrderedDict(
    host=None,
    port=None,
    timer=None,
    verbose=False)

class CryoConController(PawsPlugin):

    def __init__(self):
        super(CryoConController,self).__init__(inputs)
        self.input_doc['host'] = 'string representing host name or IP address'
        self.input_doc['port'] = 'integer port number where SpecInfoServer listens' 
        self.input_doc['timer'] = 'Timer plugin for triggering client activities' 
        self.input_doc['verbose'] = 'If True, plugin uses its message_callback' 
        self.sock = None
        self.thread_blocking = True

    def description(self):
        desc = 'CryoConController Plugin: '\
            'This is a TCP Client used to communicate with a CryoCon. '\
            'Startup requires a host name and a port number, '\
            'which should match the network configuration of the CryoCon device.'
        return desc

    def start(self):
        self.run_clone()

    def run(self):
        # executed by self.thread_clone in its own thread
        hst = self.inputs['host'] 
        prt = self.inputs['port'] 
        self.sock = socket.create_connection((hst,prt)) 
        vb = self.inputs['verbose']
        tmr = self.inputs['timer'] 
        self.run_cmd('*idn?')
        keep_going = True
        while keep_going: 
            while self.commands.qsize() > 0:
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                self.run_cmd(cmd)
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        self.sock.close()
        if vb: self.message_callback('CryoConController FINISHED')

    def run_cmd(self,cmd):
        with self.inputs['timer'].dt_lock:
            t_now = float(self.inputs['timer'].dt_utc())
        self.send_line(cmd)
        resp = self.receive_line()
        if self.inputs['verbose']: self.message_callback('{}: {}'.format(t_now,cmd+' '+resp))
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd+' '+resp)

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip().decode()
        return bfr

    def set_units(self,channel_str,unit_str):
        with self.thread_clone.command_lock:
            cmd = 'input {}: units {}'.format(channel_str,unit_str)
            self.thread_clone.commands.put(cmd)

    def loop_setup(self,loop_idx,channel_str,control_type='PID'):
        with self.thread_clone.command_lock:
            cmd = 'loop {}: source {}; type {}'.format(loop_idx,channel_str,control_type)
            self.thread_clone.commands.put(cmd)

    def set_temperature(self,loop_idx,T_set):
        with self.thread_clone.command_lock:
            cmd = 'loop {}: setpt {}'.format(loop_idx,T_set)
            self.thread_clone.commands.put(cmd)

    def start_control(self,loop_idx):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('control')
 
    def send_line(self, line):
        self.sock.sendall(bytearray((line+'\n').encode('utf-8')))

