import socket 
from threading import Condition
import time

from .PawsPlugin import PawsPlugin

class SpecInfoClient(PawsPlugin):

    def __init__(self,host,port,verbose=False,log_file=None):
        """Create a SpecInfoClient plugin.
            
        This is a TCP Client used to communicate with SpecInfoServer.
        Startup requires a host name and a port number,
        where SpecInfoServer should be listening.

        Parameters
        ----------
        host : str
            string representing host name or IP address
        port : int
            integer port number where SpecInfoServer listens
        verbose : bool
        log_file : str
        """
        super(SpecInfoClient,self).__init__(verbose=verbose,log_file=log_file)
        self.host = host
        self.port = port
        self.socket_lock = Condition()
        self.sock = None

    def start(self):
        with self.socket_lock:
            self.sock = socket.create_connection((self.host,self.port)) 
        self.take_control()
        super(SpecInfoClient,self).start()

    def close_socket(self):
        with self.socket_lock:
            self.sock.close()

    def run_cmd(self,cmd):
        resp = ''
        while resp in ['','spec is busy!']:
            with self.socket_lock:
                self.send_line(cmd)
                resp = self.receive_line()
        self.add_to_history(cmd+' '+resp)
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
        resp = self.run_cmd('!rqc')
        while not resp == 'client in control.':
            time.sleep(0.1)
            resp = self.run_cmd('!rqc')

    def mar_expose(self,filename,exposure_time):
        self.run_cmd('!cmd mar netroot {}'.format(filename))
        self.run_cmd('!cmd mar collect {}'.format(exposure_time))
        sleep_time = exposure_time+5
        self.message_callback('waiting {} seconds for {}-second exposure'.format(sleep_time,exposure_time))
        time.sleep(sleep_time)

    def enable_cryocon(self):
        self.run_cmd('!cmd ctemp_enable')
        self.run_cmd('!cmd ctemp_ctrl_on')

    def set_cryocon(self,temperature,ramp=None):
        if ramp is not None:
            self.run_cmd('!cmd ctemp_ramp_on')
            self.run_cmd('!cmd csetramp {}'.format(ramp))
        self.run_cmd('!cmd csettemp {}'.format(temperature))

    def stop_cryocon(self):
        self.run_cmd('!cmd ctemp_ctrl_off')
        self.run_cmd('!cmd ctemp_disable')

    def read_cryocon(self):
        # !cmd cmeasuretemp     -> reads temperature, saves as CYRO_DEGC
        self.run_cmd('!cmd cmeasuretemp')
        # TODO: this should block until it has a result,
        # and then it should return that result, via:
        # !cmd CRYO_DEGC    -> queries the CRYO_DEGC variable
        # ?res              -> gets result of CRYO_DEGC query

    def mar_enable(self):
        self.run_cmd('!cmd mar_enable')

    def mar_disable(self):
        self.run_cmd('!cmd mar_disable')

    def run_loopscan(self,mroot,n_points,exp_time):
        # !cmd loopscan n_points exposure_time sleep_time
        self.run_cmd('!cmd mar netroot {}'.format(mroot))
        self.run_cmd('!cmd loopscan {} {}'.format(n_points,exp_time))

