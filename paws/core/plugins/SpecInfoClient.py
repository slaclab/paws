from __future__ import print_function
from collections import OrderedDict
import copy
import socket 
import os
import sys
from threading import Thread, Condition
if int(sys.version[0]) == 2:
    import Queue as queue
else:
    import queue 

import tzlocal

from .PawsPlugin import PawsPlugin
from .. import pawstools

inputs = OrderedDict(
    host=None,
    port=None,
    timer=None,
    verbose=False)

class SpecInfoClient(PawsPlugin):

    def __init__(self):
        super(SpecInfoClient,self).__init__(inputs)
        self.input_doc['host'] = 'string representing host name or IP address'
        self.input_doc['port'] = 'integer port number where SpecInfoServer listens' 
        self.input_doc['timer'] = 'Timer plugin for triggering client activities' 
        self.input_doc['verbose'] = 'If True, plugin uses its message_callback' 
        self.n_events = 0
        self.history_lock = Condition()
        self.history = []
        self.commands = queue.Queue() 
        self.running_lock = Condition()
        self.sock = None
        self.content = OrderedDict(history = self.history)
        self.thread_clone = None
        self.proxy = None

    def description(self):
        desc = 'SpecInfoClient Plugin: '\
            'This is a TCP Client used to communicate with SpecInfoServer. '\
            'Startup requires a host name and a port number, '\
            'where SpecInfoServer should be listening.'
        return desc

    def start(self):
        with self.running_lock:
            self.running = True
        hst = self.inputs['host'] 
        prt = self.inputs['port'] 
        tmr = self.inputs['timer'] 
        self.thread_clone = self.build_clone()
        self.thread_clone.proxy = self
        self.thread_clone.sock = socket.create_connection((hst,prt)) 
        th = Thread(target=self.thread_clone.run)
        th.start()

    def run(self):
        vb = self.inputs['verbose']
        # executed by self.thread_clone in its own thread
        cmd = '!rqc'
        with self.proxy.inputs['timer'].dt_lock:
            t_now = float(self.proxy.inputs['timer'].time_points[-1])
        self.send_line(cmd)
        resp = self.receive_line()
        if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd,resp.decode())
        while not resp.decode() == 'client in control.':
            with self.proxy.inputs['timer'].dt_lock:
                self.proxy.inputs['timer'].dt_lock.wait()
            with self.proxy.inputs['timer'].dt_lock:
                t_now = float(self.proxy.inputs['timer'].time_points[-1])
            self.send_line(cmd)
            resp = self.receive_line()
            if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
            with self.proxy.history_lock:
                self.proxy.add_to_history(t_now,cmd,resp.decode())
        #    trial += 1
        #    if trial > 100:
        #        self.proxy.add_to_history('CONTROL DENIED',resp)
        #        raise RuntimeError('SpecInfoServer control denied')
        #if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp))
        keep_going = True
        while keep_going: 
            while self.commands.qsize() > 0:
                cmd = self.commands.get()
                # release self.commands with a task_done()
                self.commands.task_done()
                with self.proxy.inputs['timer'].dt_lock:
                    t_now = float(self.proxy.inputs['timer'].time_points[-1])
                self.send_line(cmd)
                resp = self.receive_line()
                if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
                while resp.decode() in ['','spec is busy!']:
                    with self.proxy.inputs['timer'].dt_lock:
                        self.proxy.inputs['timer'].dt_lock.wait()
                    with self.proxy.inputs['timer'].dt_lock:
                        t_now = float(self.proxy.inputs['timer'].time_points[-1])
                    self.send_line(cmd)
                    resp = self.receive_line()
                    if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
                with self.proxy.history_lock:
                    self.proxy.add_to_history(t_now,cmd,resp.decode())
                #with self.proxy.inputs['timer'].dt_lock:
                #    self.proxy.inputs['timer'].dt_lock.wait()
            with self.proxy.inputs['timer'].dt_lock:
                self.proxy.inputs['timer'].dt_lock.wait()
            with self.proxy.inputs['timer'].running_lock:
                if not self.proxy.inputs['timer'].running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        with self.proxy.inputs['timer'].dt_lock:
            t_now = float(self.proxy.inputs['timer'].time_points[-1])
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd,resp.decode())
            self.proxy.dump_history()
        self.sock.close()

    def dump_history(self):
        dump_path = os.path.join(pawstools.paws_scratch_dir,'ppump_controller_{}.log'.format(self))
        dump_file = open(dump_path,'w')
        dump_file.write('t :: command :: response\n')
        for ev in self.history:
            dump_file.write('{} :: {} :: {}\n'.format(ev['t'],ev['command'],ev['response']))
        dump_file.close()

    def get_plugin_content(self):
        with self.history_lock:
            h = copy.deepcopy(self.history)
        return {'history':h}

    def add_to_history(self,t,cmd,resp):
        self.history.append(self.event(t,cmd,resp))

    def event(self,t,cmd,resp):
        event = OrderedDict(t=t,command=cmd,response=resp)
        return event

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip()
        return bfr
    
    def send_line(self, line):
        self.sock.sendall(bytearray(line.encode('utf-8')))

    def enable_cryocon(self):
        self.thread_clone.commands.put('!cmd ctemp_enable')
        self.thread_clone.commands.put('!cmd ctemp_ctrl_on')
        self.thread_clone.commands.put('!cmd csettemp 20')

    def set_cryocon(self,temperature,ramp=None):
        if ramp is not None:
            self.thread_clone.commands.put('!cmd ctemp_ramp_on')
            self.thread_clone.commands.put('!cmd csetramp {}'.format(ramp))
        self.thread_clone.commands.put('!cmd csettemp {}'.format(temperature))

    def stop_cryocon(self):
        self.thread_clone.commands.put('!cmd ctemp_ctrl_off')
        self.thread_clone.commands.put('!cmd ctemp_disable')

    def read_cryocon(self):
        # !cmd cmeasuretemp     -> reads temperature, saves as CYRO_DEGC
        # !cmd CRYO_DEGC        -> query the CRYO_DEGC variable
        # ?res                  -> gets result of CRYO_DEGC query
        self.thread_clone.commands.put('!cmd cmeasuretemp')

    def mar_enable(self):
        self.thread_clone.commands.put('!cmd mar_enable')
 
    def mar_disable(self):
        self.thread_clone.commands.put('!cmd mar_disable')
 
    def run_loopscan(self,mroot,n_points,exp_time):
        # !cmd loopscan n_points exposure_time sleep_time
        self.thread_clone.commands.put('!cmd mar netroot {}'.format(mroot))
        self.thread_clone.commands.put('!cmd loopscan {} {}'.format(n_points,exp_time))

#------------------------------------------------------------------------------

#    p.addCommand("!cmd slacx_mar_data_path = 'my_mar_data'")
#    p.addCommand("!cmd slacx_pd_filename = 'my_pd_filename'")
#    p.addCommand("!cmd slacx_loopscan_npoints = 2")
#    p.addCommand("!cmd slacx_loopscan_counting_time = 2")
#    p.addCommand("!cmd runme")
#    p.addCommand("?sta")
#
# !rqc                  -> requests control
# !cmd mar_enable       -> enables mar det as a counter
# !cmd pd enable        -> enables pilatus as a counter

# Loop Scanning
# !cmd loopscan n_points exposure_time sleep_time


