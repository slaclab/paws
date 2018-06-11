from __future__ import print_function
from collections import OrderedDict
import socket 
from threading import Condition

from .PawsPlugin import PawsPlugin

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
        self.loopscan_lock = Condition()
        self.sock = None

    def description(self):
        desc = 'SpecInfoClient Plugin: '\
            'This is a TCP Client used to communicate with SpecInfoServer. '\
            'Startup requires a host name and a port number, '\
            'where SpecInfoServer should be listening.'
        return desc

    def start(self):
        self.run_clone()

    def run(self):
        hst = self.inputs['host'] 
        prt = self.inputs['port'] 
        self.sock = socket.create_connection((hst,prt)) 
        vb = self.inputs['verbose']
        tmr = self.inputs['timer'] 
        # executed by self.thread_clone in its own thread
        cmd = '!rqc'
        with tmr.dt_lock:
            t_now = float(tmr.dt_utc())
        self.send_line(cmd)
        resp = self.receive_line()
        if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd,resp.decode())
        while not resp.decode() == 'client in control.':
            with tmr.dt_lock:
                tmr.dt_lock.wait()
                t_now = float(tmr.dt_utc())
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
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                with tmr.dt_lock:
                    t_now = float(tmr.dt_utc())
                self.send_line(cmd)
                resp = self.receive_line()
                if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
                # if the command did not go through, use the timer to try again until it does.
                while resp.decode() in ['','spec is busy!']:
                    with tmr.dt_lock:
                        tmr.dt_lock.wait()
                        t_now = float(tmr.dt_utc())
                    self.send_line(cmd)
                    resp = self.receive_line()
                if vb: self.message_callback('{} :: {} :: {}'.format(t_now,cmd,resp.decode()))
                # if the cmd that just went through was a loopscan,
                # wait for control and then notify
                if cmd.strip().split()[1] == 'loopscan':
                    cmd = '!cmd ct'
                    self.send_line(cmd)
                    resp = self.receive_line()
                    while resp.decode() in ['','spec is busy!']:
                        with tmr.dt_lock:
                            tmr.dt_lock.wait()
                        self.send_line(cmd)
                        resp = self.receive_line()
                    self.notify_locks(self.loopscan_lock)
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
        with tmr.dt_lock:
            t_now = float(tmr.dt_utc())
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd,resp.decode())
            self.proxy.dump_history()
        self.sock.close()

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip()
        return bfr
    
    def send_line(self, line):
        self.sock.sendall(bytearray(line.encode('utf-8')))

    def enable_cryocon(self):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('!cmd ctemp_enable')
            self.thread_clone.commands.put('!cmd ctemp_ctrl_on')

    def set_cryocon(self,temperature,ramp=None):
        with self.thread_clone.command_lock:
            if ramp is not None:
                self.thread_clone.commands.put('!cmd ctemp_ramp_on')
                self.thread_clone.commands.put('!cmd csetramp {}'.format(ramp))
            self.thread_clone.commands.put('!cmd csettemp {}'.format(temperature))

    def stop_cryocon(self):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('!cmd ctemp_ctrl_off')
            self.thread_clone.commands.put('!cmd ctemp_disable')

    def read_cryocon(self):
        # !cmd cmeasuretemp     -> reads temperature, saves as CYRO_DEGC
        # !cmd CRYO_DEGC        -> query the CRYO_DEGC variable
        # ?res                  -> gets result of CRYO_DEGC query
        # TODO: this should block until it has a result,
        # and then it should return that result
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('!cmd cmeasuretemp')

    def mar_enable(self):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('!cmd mar_enable')
 
    def mar_disable(self):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('!cmd mar_disable')
 
    def run_loopscan(self,mroot,n_points,exp_time,block=False):
        # !cmd loopscan n_points exposure_time sleep_time
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('!cmd mar netroot {}'.format(mroot))
            self.thread_clone.commands.put('!cmd loopscan {} {}'.format(n_points,exp_time))
        if block:
            # wait for self.thread_clone.loopscan_lock
            if self.inputs['verbose']: self.message_callback('blocking until loopscan finishes')
            with self.thread_clone.loopscan_lock:
                self.thread_clone.loopscan_lock.wait()
            if self.inputs['verbose']: self.message_callback('loopscan finished')

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


