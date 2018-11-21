from __future__ import print_function
from collections import OrderedDict
import socket 
from socket import AF_INET, SOCK_STREAM
from threading import Condition

from .PawsPlugin import PawsPlugin

content = OrderedDict(
    host=None,
    port=None,
    timer=None,
    mar_root_dir='/',
    verbose=False)

class MarCCDClient(PawsPlugin):

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

    def __init__(self):
        super(MarCCDClient,self).__init__(content)
        self.content_doc['host'] = 'string representing host name or IP address'
        self.content_doc['port'] = 'integer port number where Mar server listens' 
        self.content_doc['timer'] = 'Timer plugin for triggering client activities' 
        self.content_doc['verbose'] = 'If True, plugin uses its message_callback' 
        # this lock allows Operations to wait for exposure loops to finish
        self.exposure_lock = Condition()
        self.sock = None
        self.thread_blocking = True
        self.state_lock = Condition()
        self.state = OrderedDict(
            state_code = None
            )

    def description(self):
        return 'MarCCDClient Plugin: '\
            'TCP/IP Client used to communicate with MarCCD server'

    def start(self):
        super(MarCCDClient,self).start() 

    def run(self):
        hst = self.content['host'] 
        prt = self.content['port'] 
        self.sock = socket.create_connection((hst,prt)) 
        self.vb = self.content['verbose']
        tmr = self.content['timer'] 
        self.mar_root = self.content['mar_root_dir']

        self.set_darkfield()       

        self.update_status()
        keep_going = True
        while keep_going: 
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            while self.commands.qsize() > 0:
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                cmd_parts = cmd.split(',')
                if cmd_parts[0] == 'expose':
                    self.expose(float(cmd_parts[1]),cmd_parts[2])
                #self.run_cmd(cmd)
            self.update_status()
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd,resp.decode())
            self.proxy.dump_history()
        self.sock.close()

    def expose(self,integration_time,filename):
        self.wait_for_state([self.STATE_MASK_ACQUIRING,self.STATE_MASK_BUSY,self.STATE_MASK_READING],False)
        if self.vb: self.message_callback('starting {}-second exposure'.format(integration_time))
        self.run_cmd('start') 
        self.wait_for_state(self.STATE_MASK_ACQUIRING)
        self.send_cmd('shutter,0')
        time.sleep(integration_time)
        self.send_cmd('shutter,1')
        if self.vb: self.message_callback('saving exposure to register 0')
        self.run_cmd('readout,0')
        # NOTE: have to expose twice
        # into two different registers (2 and 0)
        # for dezinger filter to work
        #self.run_cmd('dezinger,0')
        if self.vb: self.message_callback('correcting exposure')
        self.run_cmd('correct')
        if self.vb: self.message_callback('writing exposure to {}'.format(self.mar_root+filename))
        self.run_cmd('writefile,{},1'.format(self.mar_root+filename))

    def set_darkfield(self,integration_time=0.):
        if self.vb: self.message_callback('starting darkfield scan to register 2')
        self.run_cmd('start')
        self.wait_for_state(self.STATE_MASK_ACQUIRING)
        time.sleep(integration_time)
        self.run_cmd('readout,2')
        self.wait_for_idle()
        if self.vb: self.message_callback('starting darkfield scan to register 1')
        self.run_cmd('start')
        self.wait_for_state(self.STATE_MASK_ACQUIRING)
        time.sleep(integration_time)
        self.run_cmd('readout,1')
        self.wait_for_state([self.STATE_MASK_ACQUIRING,self.STATE_MASK_BUSY,self.STATE_MASK_READING],False)
        if self.vb: self.message_callback('starting two-image dezinger')
        self.run_cmd('dezinger,1')
        self.wait_for_state([self.STATE_MASK_BUSY,self.STATE_MASK_DEZINGERING],False)

    def wait_for_idle(self,additional_delay=1.3):
        if self.content['verbose']: self.message_callback('waiting for Mar server to be idle')
        while self.state['state_code'] in [\
            self.STATE_MASK_ACQUIRING, self.STATE_MASK_READING,\
            self.STATE_MASK_CORRECTING, self.STATE_MASK_WRITING,\
            self.STATE_MASK_DEZINGERING, self.STATE_MASK_BUSY]:
            self.update_status()
        # an additional delay is implemented to allow the server to truly become idle.
        # in py4syn, this delay was empirically tuned to 1.3 seconds 
        # for reliable two-image acquisition.
        time.sleep(additional_delay) 

    def wait_for_state(self,state,value=True):
        if not isinstance(state,list): state = [state]
        if value:
            while not self.state['state_code'] in state:
                self.update_status()
        else:
            while self.state['state_code'] in state:
                self.update_status()

    def update_status(self):
        with self.state_lock:
            self.read_status()
        with self.proxy.state_lock:
            self.proxy.state = copy.deepcopy(self.state)
        if vb: self.message_callback(self.print_status())

    def read_status(self):
        resp = self.run_cmd('get_state')
        self.state['state_code'] = int(resp)

    def run_cmd(self,cmd):
        with self.content['timer'].dt_lock:
            t_now = float(self.content['timer'].dt_utc())
        self.send_line(cmd)
        resp = self.receive_line()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd+' '+resp)
        return resp

    def receive_line(self):
        bfr = bytearray(b' ' * 1024) 
        ln = self.sock.recv_into(bfr) 
        return bfr.strip().strip(b'\x00\n').decode()
    
    def send_line(self, line):
        self.sock.sendall(bytearray(line.encode('utf-8')))

    def request_exposure(self,integration_time,filename):
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put('expose,{},{}'.format(integration_time,filename))


