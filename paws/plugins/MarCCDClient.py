import socket 
#from socket import AF_INET, SOCK_STREAM
from threading import Condition

from .PawsPlugin import PawsPlugin

STATE_MASK_BUSY = int(0x8)
STATE_MASK_ACQUIRING = int(0x30)
STATE_MASK_READING = int(0x300)
STATE_MASK_CORRECTING = int(0x3000)
STATE_MASK_WRITING = int(0x30000)
STATE_MASK_DEZINGERING = int(0x300000)
STATE_MASK_SAVING = int(0x33300)
STATE_MASK_ERROR = int(0x44444)
#TIMEOUT = 60
#URGENT_TIMEOUT = 0.5
#BASE_IMAGE_SIZE = 4096

class MarCCDClient(PawsPlugin):

    def __init__(self,timer=None,host=None,port=None,mar_root_dir='/',verbose=False,log_file=None):
        super(MarCCDClient,self).__init__(content)
        self.timer = timer
        self.host = host
        self.port = port
        self.mar_root = mar_root_dir
        self.exposure_lock = Condition()
        self.socket_lock = Condition()
        self.sock = None
        self.state_lock = Condition()
        self.state = {'state_code':None}

    def start(self):
        self.sock = socket.create_connection((self.host,self.port)) 
        super(MarCCDClient,self).start() 

    def _run(self):
        self.set_darkfield()       
        self.read_status()
        keep_going = True
        while keep_going: 
            with self.timer.dt_lock:
                self.timer.dt_lock.wait()
            self.read_status()
            with tmr.running_lock:
                if not tmr.running:
                    self.stop()
            with self.running_lock:
                keep_going = bool(self.running)
        self.add_to_history('MarCCDClient stopping')
        self.dump_history()
        with self.socket_lock:
            self.sock.close()

    def expose(self,integration_time,filename):
        self.wait_for_state([STATE_MASK_ACQUIRING,STATE_MASK_BUSY,STATE_MASK_READING],False)
        if self.verbose: self.message_callback('starting {}-second exposure'.format(integration_time))
        self.run_cmd('start') 
        self.wait_for_state(STATE_MASK_ACQUIRING)
        self.run_cmd('shutter,0')
        time.sleep(integration_time)
        self.run_cmd('shutter,1')
        if self.verbose: self.message_callback('saving exposure to register 0')
        self.run_cmd('readout,0')
        # NOTE/TODO: have to expose twice
        # into two different registers (2 and 0)
        # for dezinger filter to work
        #self.run_cmd('dezinger,0')
        if self.verbose: self.message_callback('correcting exposure')
        self.run_cmd('correct')
        if self.verbose: self.message_callback('writing exposure to {}'.format(self.mar_root+filename))
        self.run_cmd('writefile,{},1'.format(self.mar_root+filename))

    def set_darkfield(self,integration_time=0.):
        if self.verbose: self.message_callback('starting darkfield scan to register 2')
        self.run_cmd('start')
        self.wait_for_state(STATE_MASK_ACQUIRING)
        time.sleep(integration_time)
        self.run_cmd('readout,2')
        self.wait_for_idle()
        if self.verbose: self.message_callback('starting darkfield scan to register 1')
        self.run_cmd('start')
        self.wait_for_state(STATE_MASK_ACQUIRING)
        time.sleep(integration_time)
        self.run_cmd('readout,1')
        self.wait_for_state([STATE_MASK_ACQUIRING,STATE_MASK_BUSY,STATE_MASK_READING],False)
        if self.vb: self.message_callback('starting two-image dezinger')
        self.run_cmd('dezinger,1')
        self.wait_for_state([STATE_MASK_BUSY,STATE_MASK_DEZINGERING],False)

    def wait_for_idle(self,additional_delay=1.3):
        if self.content['verbose']: self.message_callback('waiting for Mar server to be idle')
        while self.state['state_code'] in [\
            STATE_MASK_ACQUIRING, STATE_MASK_READING,\
            STATE_MASK_CORRECTING, STATE_MASK_WRITING,\
            STATE_MASK_DEZINGERING, STATE_MASK_BUSY]:
            self.read_status()
        # an additional delay is implemented to allow the server to truly become idle.
        # in py4syn, this delay was empirically tuned to 1.3 seconds 
        # for reliable two-image acquisition.
        time.sleep(additional_delay) 

    def wait_for_state(self,state,value=True):
        if not isinstance(state,list): state = [state]
        if value:
            while not self.state['state_code'] in state:
                self.read_status()
        else:
            while self.state['state_code'] in state:
                self.read_status()

    def read_status(self):
        resp = self.run_cmd('get_state')
        with self.state_lock:
            self.state['state_code'] = int(resp)
        if self.verbose: self.message_callback(self.print_status())

    def run_cmd(self,cmd):
        with self.socket_lock: 
            self.send_line(cmd)
            resp = self.receive_line()
        self.add_to_history(cmd+' '+resp)
        return resp

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        return bfr.strip().strip(b'\x00\n').decode()
    
    def send_line(self, line):
        self.sock.sendall(bytearray(line.encode('utf-8')))

