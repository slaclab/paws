from __future__ import print_function
from collections import OrderedDict
import copy
import time
import socket 
import datetime
import os
import sys
if int(sys.version[0]) == 2:
    import Queue as queue
else:
    import queue 

import tzlocal

from .PawsPlugin import PawsPlugin
from .. import pawstools

inputs = OrderedDict(
    host = None,
    port = None,
    timer = None)
    #dt = 1.,
    #dt_busy = 0.01)

class SpecInfoClient(PawsPlugin):

    def __init__(self):
        super(SpecInfoClient,self).__init__(inputs)
        self.input_doc['host'] = 'string representing host name or IP address'
        self.input_doc['port'] = 'integer port number where SpecInfoServer listens' 
        self.input_doc['timer'] = 'Timer plugin for triggering concurrent events' 
        #self.input_doc['dt'] = 'seconds to wait between checking the queue for new commands' 
        #self.input_doc['dt_busy'] = 'seconds to wait between querying SpecInfoServer when it is busy' 
        self.n_events = 0
        self.history = []
        self.commands = queue.Queue() 
        self.sock = None
        self.content = OrderedDict(history = self.history)
        self.clone = self.build_clone()

    def description(self):
        desc = 'SpecInfoClient Plugin: '\
            'This is a TCP Client used to communicate with SpecInfoServer. '\
            'Startup requires a host name and a port number, '\
            'where SpecInfoServer should be listening.'
        return desc

    def start(self):
        hst = self.inputs['host'] 
        prt = self.inputs['port'] 
        tmr = self.inputs['timer'] 
        self.clone.tz = tzlocal.get_localzone()
        self.clone.t_0 = datetime.datetime.now(self.tz)
        t_utc = time.mktime(self.t_0.timetuple())
        cmd='clock started'
        resp='t_0 = {}'.format(t_utc)
        self.add_to_history(cmd,resp)
        self.sock = socket.create_connection((hst,prt)) 
        #if self.data_callback:
        #    self.data_callback('content.socket',self.sock)
        #cmd='socket opened'
        #self.add_to_history(cmd,'')
        #cmd = '!rqc'
        #self.send_line(cmd)
        #resp = self.receive_line()
        #trial = 0
        while not str(resp) == 'client in control.':
            time.sleep(self.inputs['dt'])
            cmd = '!rqc'
            self.send_line(cmd)
            resp = self.receive_line()
            trial += 1
            if trial > 100:
                self.add_to_history('CONTROL DENIED',resp)
                raise RuntimeError('SpecInfoServer control denied')
        self.add_to_history(cmd,resp)
        self.running = True
        self.message_callback('SpecInfoClient started!')
        while self.running:
            while self.commands.qsize() > 0:
                cmd = copy.deepcopy(self.commands.get())
                # release self.commands with a task_done()
                self.commands.task_done()
                self.send_line(cmd)
                resp = str(self.receive_line())
                while resp in ['','spec is busy!']:
                    time.sleep(self.inputs['dt_busy'])
                    self.send_line(cmd)
                    resp = str(self.receive_line())
                self.add_to_history(cmd,resp)
                self.message_callback('\n[SpecInfoClient] \ncmd: {} \nresp: {}'.format(cmd,resp))
            time.sleep(self.inputs['dt']) 
        self.sock.close()
        cmd='socket closed'
        self.add_to_history(cmd,'')
        self.message_callback('SpecInfoClient finished.')
        self.dump_history()

    def add_to_history(self,cmd,resp):
        self.history.append(self.event(cmd,resp))
        if self.data_callback:
            self.data_callback('content.history.{}'.format(self.n_events),
                copy.deepcopy(self.history[self.n_events]))
        self.n_events += 1

    def dump_history(self):
        dump_path = os.path.join(pawstools.paws_scratch_dir,'spec_infoclient_{}.log'.format(self))
        dump_file = open(dump_path,'w')
        dump_file.write('t \tcommand \tresponse\n')
        for ev in self.history:
            dump_file.write('{} \t{} \t{}\n'.format(ev['t'],ev['command'],ev['response']))

    def event(self,cmd,resp):
        t = (datetime.datetime.now(self.tz) - self.t_0).total_seconds()
        event = OrderedDict(t=t,command=cmd,response=resp)
        return event

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip()
        return bfr
    
    def send_line(self, line):
        self.sock.sendall(bytearray(line))

    def enable_cryocon(self):
        self.plugin_clone.commands.put('!cmd ctemp_enable')
        self.plugin_clone.commands.put('!cmd ctemp_ctrl_on')
        self.plugin_clone.commands.put('!cmd csettemp 20')

    def set_cryocon(self,temperature,ramp=None):
        if ramp is not None:
            self.plugin_clone.commands.put('!cmd ctemp_ramp_on')
            self.plugin_clone.commands.put('!cmd csetramp {}'.format(ramp))
        self.plugin_clone.commands.put('!cmd csettemp {}'.format(temperature))

    def stop_cryocon(self):
        self.plugin_clone.commands.put('!cmd ctemp_ctrl_off')
        self.plugin_clone.commands.put('!cmd ctemp_disable')

    def read_cryocon(self):
        # !cmd cmeasuretemp     -> reads temperature, saves as CYRO_DEGC
        # !cmd CRYO_DEGC        -> query the CRYO_DEGC variable
        # ?res                  -> gets result of CRYO_DEGC query
        self.plugin_clone.commands.put('!cmd cmeasuretemp')

    def mar_enable(self):
        self.plugin_clone.commands.put('!cmd mar_enable')
 
    def mar_disable(self):
        self.plugin_clone.commands.put('!cmd mar_disable')
 
    def run_loopscan(self,mroot,n_points,exp_time):
        # !cmd loopscan n_points exposure_time sleep_time
        self.plugin_clone.commands.put('!cmd mar netroot {}'.format(mroot))
        self.plugin_clone.commands.put('!cmd loopscan {} {}'.format(n_points,exp_time))

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


