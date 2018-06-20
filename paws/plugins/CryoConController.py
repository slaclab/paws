from __future__ import print_function
from collections import OrderedDict
import socket 
import copy
from threading import Condition

from .PawsPlugin import PawsPlugin
from .. import pawstools

inputs = OrderedDict(
    host=None,
    port=None,
    loop_idx=1,
    timer=None,
    verbose=False)

class CryoConController(PawsPlugin):

    def __init__(self):
        super(CryoConController,self).__init__(inputs)
        self.thread_blocking = True
        self.input_doc['host'] = 'string representing host name or IP address'
        self.input_doc['port'] = 'integer port number where SpecInfoServer listens' 
        self.input_doc['loop_idx'] = 'Control loop selection (1, 2, 3, 4)' 
        self.input_doc['channel_str'] = 'Channel selection (A, B, C, D)' 
        self.input_doc['timer'] = 'Timer plugin for triggering client activities' 
        self.input_doc['verbose'] = 'If True, plugin uses its message_callback' 
        self.sock = None
        self.state_lock = Condition()
        self.state = dict(T_read = None)

    def description(self):
        desc = 'CryoConController Plugin: '\
            'This is a TCP Client used to communicate with a CryoCon. '\
            'Startup requires a host name and a port number, '\
            'which should match the network configuration of the CryoCon device.'
        return desc

    def start(self):
        self.channel_str = self.inputs['channel_str']
        self.loop_idx = self.inputs['loop_idx']
        self.run_clone()

    def run(self):
        # executed by self.thread_clone in its own thread
        hst = self.inputs['host'] 
        prt = self.inputs['port'] 
        self.sock = socket.create_connection((hst,prt)) 
        self.channel_str = self.inputs['channel_str']
        self.loop_idx = self.inputs['loop_idx']
        vb = self.inputs['verbose']
        tmr = self.inputs['timer'] 
        self.run_cmd('*idn?')
        keep_going = True
        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            while self.commands.qsize() > 0:
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                self.run_cmd(cmd)
            with self.state_lock:
                self.read_status()
            with self.proxy.state_lock:
                self.proxy.state = copy.deepcopy(self.state)
            #if vb: self.message_callback(self.print_status())
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        self.run_cmd('stop')
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
        return resp

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip().decode()
        return bfr

    def set_units(self,unit_str):
        with self.thread_clone.command_lock:
            cmd = 'input {}:units {}'.format(self.channel_str,unit_str)
            self.thread_clone.commands.put(cmd)

    def loop_setup(self,control_type='PID'):
        with self.thread_clone.command_lock:
            cmd = 'loop {}:source {};type {}'.format(self.loop_idx,self.channel_str,control_type)
            self.thread_clone.commands.put(cmd)

    def read_status(self):
        resp = self.run_cmd('input {}:temp?'.format(self.channel_str))
        with self.state_lock:
            self.state['T_read'] = float(resp)

    def set_temperature(self,T_set):
        with self.thread_clone.command_lock:
            cmd = 'loop {}:setpt {}'.format(self.loop_idx,T_set)
            self.thread_clone.commands.put(cmd)

    def set_ramp_rate(self,T_ramp):
        with self.thread_clone.command_lock:
            cmd = 'loop {}:rate {}'.format(self.loop_idx,T_ramp)
            self.thread_clone.commands.put(cmd)

    def start_control(self):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('control')
 
    def stop_control(self):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('stop')
 
    def send_line(self, line):
        self.sock.sendall(bytearray((line+'\n').encode('utf-8')))

