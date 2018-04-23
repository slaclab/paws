from __future__ import print_function
from collections import OrderedDict
import serial
import copy
import os
import sys
from threading import Thread, Condition
if int(sys.version[0]) == 2:
    import Queue as queue
else:
    import queue 

from .PawsPlugin import PawsPlugin
from .. import pawstools

inputs = OrderedDict(
    serial_device=None,
    timer=None,
    verbose=False)

class MitosPPumpController(PawsPlugin):
    """PAWS Plugin for controlling a Mitos P-pump.

    Uses a serial port (or virtual serial port)
    to communicate to a USB-attached Mitos P-pump.
    RS232 protocol settings: 
    57600 baud, 8 data bits, 1 stop bit, no parity, no handshaking.
    The pump controller acts as a proxy for controlling a clone of itself.
    The clone operates in its own thread, exchanging information 
    with the original pump controller in a threadsafe way,
    at each tick of the input timer.

    When the pump is in CONTROL mode,
    a command must be sent every 30 seconds,
    or the pump will automatically exit CONTROL mode.
    """
    def __init__(self):
        super(MitosPPumpController,self).__init__(inputs)
        self.input_doc['serial_device'] = 'string serial device indicator '\
            '(e.g. "COM2") or filesystem path (e.g. "/dev/ttyUSB0")'
        self.input_doc['timer'] = 'Timer PawsPlugin, used to initiate '\
            'thread-safe data exchanges between the pump controller '\
            'and its operational clone.'
        self.ErrorsDict = { 0:'None', \
                            1:'Supply than maximum', \
                            2:'Tare time out', \
                            3:'Tare supply still connected ', \
                            4:'Control start time out', \
                            5:'Pressure target too low', \
                            6:'Pressure target too high', \
                            7:'Leak test supply pressure too low', \
                            8:'Leak test time out', \
                            100:'Broken'}
        self.StateDict  = { 0:'IDLE', \
                            1:'CONTROLLING', \
                            2:'TARE', \
                            3:'ERROR', \
                            4:'LEAK TEST'}
        self.ser = None
        self.state = OrderedDict(
            error_code = None,
            state_code = None, 
            chamber_pressure = None, 
            supply_pressure = None, 
            target_pressure = None, 
            flow_rate = None, 
            target_flow_rate = None)
        # a lock for pump history 
        self.history_lock = Condition()
        self.history = []
        # a lock for pump controls
        #self.control_lock = Condition()
        # a lock for signalling run/stop
        self.running_lock = Condition()
        #self.n_events = 0
        self.commands = queue.Queue() 
        self.thread_clone = None
        self.proxy = None

    def start(self):
        with self.running_lock:
            self.running = True
        self.thread_clone = self.build_clone()
        self.thread_clone.proxy = self
        self.thread_clone.ser = serial.Serial(
            self.inputs['serial_device'], 
            57600, timeout=1, 
            parity = serial.PARITY_NONE, 
            bytesize = serial.EIGHTBITS, 
            xonxoff = 0, rtscts = 0)
        th = Thread(target=self.thread_clone.run)
        th.start()
       
    def run(self):
        vb = self.inputs['verbose']
        # this method is run by self.thread_clone 
        keep_going = True
        # check for control...
        self.read_status()
        if not self.state['state_code'] == 1:
            # attempt to enter remote control mode 
            cmd = "A1"
            self.send_line(cmd)  
            resp = self.receive_line()
            with self.proxy.history_lock:
                with self.proxy.inputs['timer'].dt_lock:
                    t_now = float(self.proxy.inputs['timer'].time_points[-1])
                self.proxy.add_to_history(t_now,str(cmd),str(resp))
            if not resp.decode() == "#A0":
                msg = "Pump failed to enter REMOTE control mode"
                with self.proxy.history_lock:
                    with self.proxy.inputs['timer'].dt_lock:
                        t_now = float(self.proxy.inputs['timer'].time_points[-1])
                    self.proxy.add_to_history(t_now,'ERROR',str(msg))
                keep_going = False
                with self.proxy.running_lock:
                    self.proxy.stop()
                #raise RuntimeError(msg)

        # clear the pump...
        cmd = "C"
        self.send_line(cmd)
        resp = self.receive_line()
        with self.proxy.history_lock:
            with self.proxy.inputs['timer'].dt_lock:
                t_now = float(self.proxy.inputs['timer'].time_points[-1])
            self.proxy.add_to_history(t_now,str(cmd),str(resp))

        while keep_going:
            with self.proxy.inputs['timer'].dt_lock:
                self.proxy.inputs['timer'].dt_lock.wait()
            self.read_status()
            if vb: self.message_callback(self.print_status())
            while self.commands.qsize() > 0: 
                cmd = str(self.commands.get())
                self.commands.task_done()
                self.send_line(cmd)
                resp = self.receive_line()
                with self.proxy.history_lock:
                    with self.proxy.inputs['timer'].dt_lock:
                        t_now = float(self.proxy.inputs['timer'].time_points[-1])
                    self.proxy.add_to_history(t_now,str(cmd),str(resp))
            with self.proxy.inputs['timer'].running_lock:
                if not self.proxy.inputs['timer'].running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
        cmd = "A0"
        with self.proxy.inputs['timer'].dt_lock:
            t_now = float(self.proxy.inputs['timer'].time_points[-1])
        self.send_line(cmd)
        resp = self.receive_line()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,str(cmd),str(resp))
            self.proxy.dump_history()
        self.ser.close()

    def send_line(self,line):
        self.ser.write("{}\r\n".format(line).encode('utf-8'))  

    def receive_line(self):
        r = self.ser.readline()
        return r.strip()

    def add_to_history(self,t,cmd,resp):
        self.history.append(self.event(t,cmd,resp))
        #print('\nMitosPPumpController command: {}'.format(cmd))
        #print('response: {}'.format(resp))

    def event(self,t,cmd,resp):
        event = OrderedDict(t=t,command=cmd,response=resp)
        return event

    def dump_history(self):
        dump_path = os.path.join(pawstools.paws_scratch_dir,'ppump_controller_{}.log'.format(self))
        dump_file = open(dump_path,'w')
        dump_file.write('t :: command :: response\n')
        for ev in self.history:
            dump_file.write('{} :: {} :: {}\n'.format(ev['t'],ev['command'],ev['response']))
        dump_file.close()


    def read_status(self):
        """ Read pump status.

        The reply from the pump is formatted as 
        #sErr,Sp,Src,Pc,Ps,Pt,Qc,Qt,Ft
        These are numeric codes defining the response state.  

        Err - Error code. A value of 0 means CMD_ACCEPTED - OK.

        Sp  - State of the pump
            0.   IDLE
            1.   CONTROLLING
            2.   TARE
            3.   ERROR
            4.   LEAK TEST
        The status returned by the pump should reflect
        the latest command sent from the PC to the pump.

        Src - Mode of control: 0 is manual, 1 is remote controlled.

        Pc  - Chamber pressure in mbar.

        Ps  - Supply pressure in mbar.

        Pt  - Target pressure in mbar. 

        Qc  - Current flow rate in pl/s. 
            Requires a connected Mitos Sensor Display flow meter.

        Qt  - Target flow rate in pl/s. 
            Requires a connected Mitos Sensor Display flow meter.

        Ft  - Flow sensor type plus flow control mode. 
            Requires a connected Mitos Sensor Display,
            or sensor interface flow meter.
            This consists of an upper nibble, 
            middle nibble and lower nibble.
        """
        cmd = "s"
        self.send_line(cmd)
        resp = self.receive_line()
        s = resp.split(b',')
        while '' in s or len(s) < 8:
            self.send_line(cmd)
            resp = self.receive_line()
            s = resp.split(b',')
        with self.proxy.history_lock:
            with self.proxy.inputs['timer'].dt_lock:
                t_now = float(self.proxy.inputs['timer'].time_points[-1])
            self.proxy.add_to_history(t_now,str(cmd),str(resp))
        self.state['error_code'] = int(s[0][2:])
        self.state['state_code'] = int(s[1])
        self.state['chamber_pressure'] = float(s[3])
        self.state['supply_pressure'] = float(s[4])
        self.state['target_pressure'] = float(s[5])
        self.state['flow_rate'] = float(s[6])
        self.state['target_flow_rate'] = float(s[7])
        # TODO: perform this update using the queue
        #if self.data_callback:
        #    self.data_callback('content.state',copy.deepcopy(self.state))

    def print_status(self):
        msg = '----------- PUMP STATUS -----------'+os.linesep
        msg += 'Error code: {} ({})'.format(self.state['error_code'],
            self.ErrorsDict[self.state['error_code']])+os.linesep
        msg += 'State code: {} ({})'.format(self.state['state_code'],
            self.StateDict[self.state['state_code']])+os.linesep
        msg += 'Chamber pressure: \t{}'.format(self.state['chamber_pressure'])+os.linesep 
        msg += 'Supply pressure: \t{}'.format(self.state['supply_pressure'])+os.linesep 
        msg += 'Target pressure: \t{}'.format(self.state['target_pressure'])+os.linesep 
        msg += 'Current flow rate: \t{}'.format(self.state['flow_rate'])+os.linesep 
        msg += 'Target flow rate: \t{}'.format(self.state['target_flow_rate'])+os.linesep 
        msg += '-----------------------------------'
        return msg

    def set_flowrate(self,rate):
        """Set the pump flow rate to `rate` (microlitres per minute).

        Parameters
        ----------
        rate : integer
            The flow rate set point, in microlitres per minute.
            The pump controller expects and integer value in
            picolitres per second.
            The rate is rounded to the nearest integer value
            after converting it to picolitres per second.
        """
        pl_s_rate = int(round(float(rate)*1.E6/60.))
        self.thread_clone.commands.put("F{}".format(pl_s_rate)) 

    def set_pressure(self,pressure):
        """Set the pump pressure to the provided value.

        Parameters
        ----------
        pressure : integer
            The pressure set point, in mbar.
            A value of 1000 sends the 'P1000' command,
            which sets target pressure to 1000 mbar. 
        """
        self.thread_clone.commands.put("P{}".format(pressure)) 

    def tare(self):
        """Tare the P-pump."""
        if self.inputs['verbose']: self.message_callback('taring pump')
        self.thread_clone.commands.put("R0")

    def set_idle(self):
        """Set the P-pump to idle."""
        if self.inputs['verbose']: self.message_callback('setting pump to idle')
        self.thread_clone.commands.put("P0")

    def dispense_volume(self, vol):
        """Control the pump to dispense a specified volume.

        Parameters
        ----------
        vol : float
            The volume to dispense 
        """
        pass

    def get_plugin_content(self):
        with self.history_lock:
            h = copy.deepcopy(self.history)
        return {'history':h}


