from __future__ import print_function
from collections import OrderedDict
import socket 
from threading import Condition
import time

from .PawsPlugin import PawsPlugin

content = OrderedDict(
    host=None,
    port=None,
    timer=None)

class SpecInfoClient(PawsPlugin):

    def __init__(self):
        super(SpecInfoClient,self).__init__(content)
        self.content_doc['host'] = 'string representing host name or IP address'
        self.content_doc['port'] = 'integer port number where SpecInfoServer listens' 
        self.content_doc['timer'] = 'Timer plugin for triggering client activities' 
        self.socket_lock = Condition()
        self.sock = None
        self.thread_blocking = True

    def description(self):
        desc = 'SpecInfoClient Plugin: '\
            'This is a TCP Client used to communicate with SpecInfoServer. '\
            'Startup requires a host name and a port number, '\
            'where SpecInfoServer should be listening.'
        return desc

    def start(self,threaded=True):
        super(SpecInfoClient,self).start(threaded)

    def run(self):
        hst = self.content['host'] 
        prt = self.content['port'] 
        with self.socket_lock:
            self.sock = socket.create_connection((hst,prt)) 
        tmr = self.content['timer'] 

        self.take_control()

        keep_going = True
        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        if self.verbose: self.message_callback('FINISHED')
        with tmr.dt_lock:
            t_now = float(tmr.dt_utc())
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,'STOP')
            self.proxy.dump_history()
        self.sock.close()

    def run_cmd(self,cmd):
        with self.content['timer'].dt_lock:
            t_now = float(self.content['timer'].dt_utc())
        resp = ''
        while resp in ['','spec is busy!']:
            with self.socket_lock:
                self.send_line(cmd)
                resp = self.receive_line()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd+' '+resp)
        if self.verbose: self.message_callback(cmd+' '+resp)
        return resp

    def send_line(self, line):
        self.sock.sendall(bytearray(line.encode('utf-8')))

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        bfr = bfr.strip().decode()
        return bfr
    
    def take_control(self):
        tmr = self.content['timer'] 
        resp = self.run_cmd('!rqc')
        while not resp == 'client in control.':
            with tmr.dt_lock:
                tmr.dt_lock.wait()
                t_now = float(tmr.dt_utc())
            resp = self.run_cmd('!rqc')

    def mar_expose(self,filename,exposure_time):
        self.thread_clone.run_cmd('!cmd mar netroot {}'.format(filename))
        self.thread_clone.run_cmd('!cmd mar collect {}'.format(exposure_time))
        sleep_time = exposure_time+5
        self.message_callback('waiting {} seconds for {}-second exposure'.format(sleep_time,exposure_time))
        time.sleep(sleep_time)

#    def enable_cryocon(self):
#        with self.thread_clone.command_lock:
#            self.thread_clone.commands.put('!cmd ctemp_enable')
#            self.thread_clone.commands.put('!cmd ctemp_ctrl_on')
#
#    def set_cryocon(self,temperature,ramp=None):
#        with self.thread_clone.command_lock:
#            if ramp is not None:
#                self.thread_clone.commands.put('!cmd ctemp_ramp_on')
#                self.thread_clone.commands.put('!cmd csetramp {}'.format(ramp))
#            self.thread_clone.commands.put('!cmd csettemp {}'.format(temperature))
#
#    def stop_cryocon(self):
#        with self.thread_clone.command_lock:
#            self.thread_clone.commands.put('!cmd ctemp_ctrl_off')
#            self.thread_clone.commands.put('!cmd ctemp_disable')
#
#    def read_cryocon(self):
#        # !cmd cmeasuretemp     -> reads temperature, saves as CYRO_DEGC
#        # !cmd CRYO_DEGC        -> query the CRYO_DEGC variable
#        # ?res                  -> gets result of CRYO_DEGC query
#        # TODO: this should block until it has a result,
#        # and then it should return that result
#        with self.thread_clone.command_lock:
#            self.thread_clone.commands.put('!cmd cmeasuretemp')
#
#    def mar_enable(self):
#        with self.thread_clone.command_lock:
#            self.thread_clone.commands.put('!cmd mar_enable')
# 
#    def mar_disable(self):
#        with self.thread_clone.command_lock:
#            self.thread_clone.commands.put('!cmd mar_disable')
# 
#    def run_loopscan(self,mroot,n_points,exp_time,block=False):
#        # !cmd loopscan n_points exposure_time sleep_time
#        with self.thread_clone.command_lock:
#            self.thread_clone.commands.put('!cmd mar netroot {}'.format(mroot))
#            self.thread_clone.commands.put('!cmd loopscan {} {}'.format(n_points,exp_time))
#        if block:
#            # wait for self.thread_clone.loopscan_lock
#            if self.verbose: self.message_callback('blocking until loopscan finishes')
#            with self.thread_clone.loopscan_lock:
#                self.thread_clone.loopscan_lock.wait()
#            if self.verbose: self.message_callback('loopscan finished')
#
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


