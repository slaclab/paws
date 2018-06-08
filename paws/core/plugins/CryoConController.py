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
        cmd = '*idn?'
        with tmr.dt_lock:
            t_now = float(tmr.dt_utc())
        self.send_line(cmd)
        resp = self.receive_line()
        if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd,resp.decode())
        # TODO: some kind of loop to check for control before proceeding
        keep_going = True
        while keep_going: 
            while self.commands.qsize() > 0:
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                with tmr.dt_lock:
                    t_now = float(tmr.dt_utc())
                self.send_line(cmd)
                resp = self.receive_line()
                if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
                with self.proxy.history_lock:
                    self.proxy.add_to_history(t_now,cmd,resp.decode())
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        self.sock.close()

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip()
        return bfr
    
    def send_line(self, line):
        self.sock.sendall(bytearray(line.encode('utf-8')))


