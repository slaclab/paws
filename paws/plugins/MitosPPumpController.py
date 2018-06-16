from __future__ import print_function
from collections import OrderedDict
import copy
import os
from threading import Condition

import serial

from .PawsPlugin import PawsPlugin

inputs = OrderedDict(
    serial_device=None,
    timer=None,
    flowrate_table=None,
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
        self.input_doc['flowrate_table'] = 'table mapping flowrates '\
            'to Mitos instrument setpoints (with flow meter calibrated for water). '\
            'This table should be formatted as a list '\
            'containing a list of flowrates and a list of setpoints: '\
            '[[flowrates],[setpoints]], with each specified in microlitres/minute, '\
            'with linear interplation as needed (and no extrapolation).'
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
        self.state_lock = Condition()
        self.state = OrderedDict(
            error_code = None,
            state_code = None, 
            chamber_pressure = None, 
            supply_pressure = None, 
            target_pressure = None, 
            flow_rate = None, 
            target_flow_rate = None)
        self.thread_blocking = True

    def start(self):
        self.run_clone()
       
    def run(self):
        vb = self.inputs['verbose']
        # this method is run by self.thread_clone 
        self.ser = serial.Serial(
            self.inputs['serial_device'], 
            57600, timeout=1, 
            parity = serial.PARITY_NONE, 
            bytesize = serial.EIGHTBITS, 
            xonxoff = 0, rtscts = 0)
        tmr = self.inputs['timer']
        keep_going = True
        # check for control...
        with self.state_lock:
            self.read_status()
        with self.proxy.state_lock:
            self.proxy.state = copy.deepcopy(self.state)
        if not self.state['state_code'] == 1:
            # attempt to enter remote control mode 
            resp = self.run_cmd('A1')
            if not resp == "#A0":
                msg = "Pump failed to enter REMOTE control mode"
                with self.proxy.history_lock:
                    with tmr.dt_lock:
                        t_now = float(tmr.dt_utc())
                    self.proxy.add_to_history(t_now,'ERROR: '+msg)
                keep_going = False
                with self.proxy.running_lock:
                    self.proxy.stop()
                #raise RuntimeError(msg)

        # clear the pump...
        self.run_cmd('C')

        while keep_going:
            with tmr.dt_lock:
                tmr.dt_lock.wait()
            while self.commands.qsize() > 0: 
                with self.command_lock:
                    cmd = self.commands.get()
                    self.commands.task_done()
                self.run_cmd(cmd)
            with self.state_lock:
                self.read_status()
            with self.proxy.state_lock:
                self.proxy.state = copy.deepcopy(self.state)
            if vb: self.message_callback(self.print_status())
            with tmr.running_lock:
                if not tmr.running:
                    with self.proxy.running_lock:
                        self.proxy.stop()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)

        # relinquish control
        self.run_cmd('A0') 

        with self.proxy.history_lock:
            self.proxy.dump_history()
        self.ser.close()
        if vb: self.message_callback('MitosPPumpController FINISHED')

    def run_cmd(self,cmd):
        with self.inputs['timer'].dt_lock:
            t_now = float(self.inputs['timer'].dt_utc())
        self.send_line(cmd)
        resp = self.receive_line()
        with self.proxy.history_lock:
            self.proxy.add_to_history(t_now,cmd+' '+resp)
        return resp

    def send_line(self,line):
        self.ser.write("{}\r\n".format(line).encode('utf-8'))  

    def receive_line(self):
        return self.ser.readline().strip().decode()

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
        resp = self.run_cmd('s')
        s = resp.split(',')
        while '' in s or len(s) < 8:
            resp = self.run_cmd('s')
            s = resp.split(',')
        with self.state_lock:
            self.state['error_code'] = int(s[0][2:])
            self.state['state_code'] = int(s[1])
            self.state['chamber_pressure'] = float(s[3])
            self.state['supply_pressure'] = float(s[4])
            self.state['target_pressure'] = float(s[5])
            self.state['flow_rate'] = float(s[6])
            self.state['target_flow_rate'] = float(s[7])

    def print_status(self):
        with self.state_lock:
            msg = os.linesep+'----------- PUMP STATUS -----------'+os.linesep
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
        setpt = self.get_setpt(rate) 
        pl_s_rate = int(round(float(setpt)*1.E6/60.))
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put("F{}".format(pl_s_rate)) 

    def get_setpt(self,rate):
        tbl = self.inputs['flowrate_table']
        setpt = np.interp(rate,tbl[0],tbl[1])
        return setpt

    def set_pressure(self,pressure):
        """Set the pump pressure to the provided value.

        Parameters
        ----------
        pressure : integer
            The pressure set point, in mbar.
            A value of 1000 sends the 'P1000' command,
            which sets target pressure to 1000 mbar. 
        """
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put("P{}".format(pressure)) 

    def tare(self):
        """Tare the P-pump."""
        if self.inputs['verbose']: self.message_callback('taring pump')
        with self.thread_clone.command_lock:
            self.thread_clone.commands.put("R0")

    def set_idle(self):
        """Set the P-pump to idle."""
        if self.inputs['verbose']: self.message_callback('setting pump to idle')
        with self.thread_clone.command_lock:
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
        d = super(MitosPPumpController,self).get_plugin_content()
        with self.state_lock:
            d['state'] = copy.deepcopy(self.state)
        return d

