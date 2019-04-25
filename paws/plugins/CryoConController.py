import socket 
import copy
import time
from threading import Thread, Condition

from .PawsPlugin import PawsPlugin

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
        super(CryoConController,self).__init__(verbose=verbose,log_file=log_file)
        self.timer = timer
        self.host = host
        self.port = port
        self.channels = channels
        self.socket_lock = Condition()
        self.sock = None
        self.state_lock = Condition()
        self.state = {} 
        self.controller_thread = None

    def start(self):
        with self.socket_lock:
            self.sock = socket.create_connection((self.host,self.port)) 
        super(CryoConController,self).start()

    def _run(self):
        self.controller_thread = Thread(target=self.run_cryocon)
        # start control, block until control is established
        with self.running_lock:
            self.controller_thread.start()
            self.running_lock.wait()

    def run_cryocon(self):
        self.run_cmd('*idn?')
        self.read_status()
        self.run_notify()
        keep_going = True
        while keep_going: 
            with self.timer.dt_lock:
                self.timer.dt_lock.wait()
            self.read_status()
            with self.timer.running_lock:
                if not self.timer.running:
                    self.stop()
            with self.running_lock:
                keep_going = bool(self.running)
        if self.verbose: self.message_callback('FINISHED')
        self.run_cmd('stop')
        with self.socket_lock:
            self.sock.close()

    def read_status(self):
        for chan in self.channels.keys():
            resp = self.run_cmd('input {}:temp?'.format(chan))
            with self.state_lock:
                self.state['T_read_{}'.format(chan)] = float(resp)
                if self.verbose: self.message_callback('T_read_{}: {}'.format(chan,float(resp)))

    def run_cmd(self,cmd):
        with self.socket_lock:
            self.send_line(cmd)
            resp = self.receive_line()
        if self.verbose: self.message_callback('{}: {}'.format(cmd,resp))
        self.add_to_history(cmd+' '+resp)
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
        self.run_cmd(cmd)

    def loop_setup(self,channel,control_type='PID'):
        cmd = 'loop {}:source {};type {}'.format(self.channels[channel],channel,control_type)
        self.run_cmd(cmd)

    def set_temperature(self,channel,T_set):
        cmd = 'loop {}:setpt {}'.format(self.channels[channel],T_set)
        self.run_cmd(cmd)
        with self.state_lock:
            self.state['T_set_{}'.format(channel)] = T_set 

    def hack_set_temp(self,chan,T_set):
        # NOTE: this does a little dance, 
        # to circumvent a problem with the CryoCon,
        # where it sometimes ignores the ramp rate 
        with self.state_lock:
            T_current = float(self.state['T_read_{}'.format(chan)])
        self.set_temperature(chan,T_current)
        T_inter = T_current + (T_set-T_current)*0.1
        self.set_temperature(chan,T_inter)
        time.sleep(1)
        self.set_temperature(chan,T_set)

    def set_ramp_rate(self,channel,T_ramp):
        cmd = 'loop {}:rate {}'.format(self.channels[channel],T_ramp)
        self.run_cmd(cmd)
        with self.state_lock:
            self.state['T_ramp_{}'.format(channel)] = T_ramp 

    def start_control(self):
        self.run_cmd('control')
 
    def stop_control(self):
        self.run_cmd('stop')
 
