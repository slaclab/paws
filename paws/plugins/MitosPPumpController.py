from collections import OrderedDict
from threading import Thread, Condition
import serial

import numpy as np
from scipy.optimize import minimize as scipimin

from .PawsPlugin import PawsPlugin

states = { 0:'IDLE', \
        1:'CONTROLLING', \
        2:'TARE', \
        3:'ERROR', \
        4:'LEAK TEST'}

errors = { 0:'None', \
        1:'Supply greater than maximum', \
        2:'Tare time out', \
        3:'Tare supply still connected ', \
        4:'Control start time out', \
        5:'Pressure target too low', \
        6:'Pressure target too high', \
        7:'Leak test supply pressure too low', \
        8:'Leak test time out', \
        100:'Broken'}

class MitosPPumpController(PawsPlugin):
    """PAWS Plugin for controlling a Mitos P-pump.

    Uses a serial port (or virtual serial port)
    to communicate to a USB-attached Mitos P-pump.
    RS232 protocol settings: 
    57600 baud, 8 data bits, 1 stop bit, no parity, no handshaking.
    The pump controller acts as a proxy for controlling a clone of itself.
    The clone operates in its own thread, exchanging information 
    with the original pump controller in a threadsafe way,
    at each tick of the timer.

    When the pump is in CONTROL mode,
    a command must be sent every 30 seconds,
    or the pump will automatically exit CONTROL mode.
    """
    def __init__(self,timer,serial_device,flowrate_table=None,verbose=False,log_file=None):
        """Create a MitosPPumpController.

        Parameters
        ----------
        timer : paws.plugins.Timer.Timer
            Timer plugin for triggering pump controller activities
            and initiating thread-safe data exchanges 
        serial_device : str
            String serial device indicator (e.g. "COM2") 
            or filesystem path (e.g. "/dev/ttyUSB0")
        flowrate_table : array 
            Table mapping Mitos flow control setpoints to actual flowrates 
            (with instrument calibrated for water).
            Should be a two-column array,
            where the first column contains instrument setpoints,
            and the second column contains the corresponding measured flowrates,
            both in units of microlitres/minute
        verbose : bool
        log_file : str
        """
        super(MitosPPumpController,self).__init__(verbose=verbose,log_file=log_file)
        self.serial_lock = Condition()
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
        self.controller_thread = None
        self.timer = timer
        self.serial_device = serial_device
        self.flowrate_table = flowrate_table
        self.flow_conversion_power = 1.
        self.calibrate()

    def start(self):
        with self.serial_lock:
            self.ser = serial.Serial(
                self.serial_device, 
                57600, timeout=1, 
                parity = serial.PARITY_NONE, 
                bytesize = serial.EIGHTBITS, 
                xonxoff = 0, rtscts = 0)
        super(MitosPPumpController,self).start()

    def _run(self):
        self.controller_thread = Thread(target=self.run_pump)
        self.controller_thread.start()
        # block until device control is established: 
        with self.running_lock:
            self.running_lock.wait()

    def run_pump(self):
        keep_going = True
        # check for control...
        self.update_status()
        if not self.state['state_code'] == 1:
            # attempt to enter remote control mode 
            resp = self.run_cmd('A1')
            if not resp == "#A0":
                msg = "Pump failed to enter REMOTE control mode"
                self.message_callback(msg)
                self.add_to_history(msg)
                keep_going = False
                self.stop()

        # clear the pump...
        self.run_cmd('C')

        # self._run() will be waiting for run_notify()...
        self.run_notify()
        while keep_going:
            with self.timer.dt_lock:
                self.timer.dt_lock.wait()
            self.update_status()
            with self.timer.running_lock:
                if not self.timer.running:
                    self.stop()
            with self.running_lock:
                keep_going = bool(self.running)

        # relinquish control, close the port, stop the plugin
        self.run_cmd('A0') 
        if self.verbose: self.message_callback('FINISHED')
        self.ser.close()
        self.stop()
       
    def calibrate(self):
        if self.flowrate_table is not None:
            flow_setpts = self.flowrate_table[:,0]
            flow_meas = self.flowrate_table[:,1]
            fit_obj = lambda a: np.sum([(fset**a-fmeas)**2 for fset,fmeas in zip(flow_setpts,flow_meas)])
            res = scipimin( fit_obj,1. )
            self.flow_conversion_power = res.x[0]
            if self.verbose: 
                msg = 'finished calibrating- power law flowrate conversion: {}'.format(
                self.flow_conversion_power)
                self.message_callback(msg)

    def get_setpt(self,rate):
        if rate == 0.: return 0.
        abs_rate = abs(rate)**(1./self.flow_conversion_power)
        if rate < 0:
            return -1*abs_rate
        else:
            return abs_rate

    def get_true_flowrate(self,setpt):
        if setpt == 0.: return 0.
        abs_setpt = abs(setpt)**self.flow_conversion_power 
        if setpt < 0:
            return -1*abs_setpt
        else:
            return abs_setpt

    def update_status(self):
        with self.state_lock:
            self.read_status()
        if self.verbose: self.message_callback(self.print_status())

    def run_cmd(self,cmd):
        with self.serial_lock:
            self._send_line(cmd)
            resp = self._receive_line()
        self.add_to_history(cmd+' '+resp)
        return resp

    def _send_line(self,line):
        self.ser.write("{}\r\n".format(line).encode('utf-8'))  

    def _receive_line(self):
        return self.ser.readline().strip().decode()

    def read_status(self):
        """Read pump status, save as self.state.

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
            st = self.state
            msg = '\n----------- PUMP STATUS -----------\n'
            msg += 'Error code: {} ({})\n'.format(st['error_code'],errors[st['error_code']])
            msg += 'State code: {} ({})\n'.format(st['state_code'],states[st['state_code']])
            msg += 'Chamber pressure: \t{}\n'.format(st['chamber_pressure'])
            msg += 'Supply pressure: \t{}\n'.format(st['supply_pressure'])
            msg += 'Target pressure: \t{}\n'.format(st['target_pressure'])
            msg += 'Current flow rate: \t{}\n'.format(st['flow_rate'])
            msg += 'Target flow rate: \t{}\n'.format(st['target_flow_rate'])
            msg += '-----------------------------------\n'
        return msg

    def set_flowrate(self,rate):
        """Set the pump flow rate to `rate` (microlitres per minute).

        Parameters
        ----------
        rate : float 
            The flow rate set point, in microlitres per minute.
        """
        # TODO: think of an elegant way to handle setpts below the resolution of the pump controls
        #if rate < 0.1:
        #    rate = 0.
        if self.verbose: self.message_callback('setting flowrate: {} uL/min'.format(rate))
        setpt = self.get_setpt(rate) 
        pl_s_rate = int(round(float(setpt)*1.E6/60.))
        self.run_cmd('F{}'.format(pl_s_rate))

    def set_pressure(self,pressure):
        """Set the pump pressure to the provided value.
    
        Parameters
        ----------
        pressure : integer
            The pressure set point, in mbar.
            A value of 1000 sends the 'P1000' command,
            which sets target pressure to 1000 mbar. 
        """
        self.run_cmd('P{}'.format(pressure))

    def tare(self):
        """Tare the P-pump."""
        if self.verbose: self.message_callback('taring pump')
        self.run_cmd('R0')

    def set_idle(self):
        """Set the P-pump to idle."""
        if self.verbose: self.message_callback('setting pump to idle')
        self.run_cmd('P0')

    def dispense_volume(self, vol):
        """Control the pump to dispense a specified volume.

        Parameters
        ----------
        vol : float
            The volume to dispense 
        """
        pass
