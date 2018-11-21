from __future__ import print_function
from collections import OrderedDict
import socket 
import copy
from threading import Condition

from .PawsPlugin import PawsPlugin
from .. import pawstools

content = OrderedDict(
    host=None,
    port=None,
    channels={},
    timer=None)

class CryoConController(PawsPlugin):

    def __init__(self):
        super(CryoConController,self).__init__(content)
        self.thread_blocking = True
        self.content_doc['host'] = 'string representing host name or IP address assigned to the CryoCon'
        self.content_doc['port'] = 'integer port number for CryoCon connection' 
        self.content_doc['channels'] = 'dict mapping channel selection (strings "A"-"D") '\
            'to control loop indices (integers 1-4 or None): all channels will be read, '\
            'and any with integer control loops will be controlled. '
        self.content_doc['timer'] = 'Timer plugin for triggering client activities' 
        self.socket_lock = Condition()
        self.sock = None
        self.state_lock = Condition()
        self.state = {} 

    def description(self):
        desc = 'CryoConController Plugin: '\
            'This is a TCP Client used to communicate with a CryoCon. '\
            'Startup requires a host name and a port number, '\
            'which should match the network configuration of the CryoCon device.'
        return desc

    def start(self):
        super(CryoConController,self).start()

    def run(self):
        # executed by self.thread_clone in its own thread
        hst = self.content['host'] 
        prt = self.content['port'] 
        with self.socket_lock:
            self.sock = socket.create_connection((hst,prt)) 
        tmr = self.content['timer'] 
        self.run_cmd('*idn?')
        keep_going = True

        self.update_status()

        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            #while self.commands.qsize() > 0:
            #    with self.command_lock:
            #        cmd = self.commands.get()
            #        self.commands.task_done()
            #
            #    self.run_cmd(cmd)
            self.update_status()
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        if self.verbose: self.message_callback('FINISHED')
        self.run_cmd('stop')
        with self.socket_lock:
            self.sock.close()

    def read_status(self):
        for chan in self.content['channels'].keys():
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
        with self.content['timer'].dt_lock:
            t_now = float(self.content['timer'].dt_utc())
        with self.socket_lock:
            self.send_line(cmd)
            resp = self.receive_line()
        if self.verbose: self.message_callback('{}: {}'.format(t_now,cmd+' '+resp))
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd+' '+resp)
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
        cmd = 'loop {}:source {};type {}'.format(self.content['channels'][channel],channel,control_type)
        self.thread_clone.run_cmd(cmd)
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put(cmd)

    def set_temperature(self,channel,T_set):
        cmd = 'loop {}:setpt {}'.format(self.content['channels'][channel],T_set)
        self.thread_clone.run_cmd(cmd)
        with self.thread_clone.state_lock:
            self.thread_clone.state['T_set_{}'.format(channel)] = T_set 
        #with self.thread_clone.command_lock:
        #    self.thread_clone.commands.put(cmd)

    def set_ramp_rate(self,channel,T_ramp):
        cmd = 'loop {}:rate {}'.format(self.content['channels'][channel],T_ramp)
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
 
