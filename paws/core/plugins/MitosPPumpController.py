from __future__ import print_function
from collections import OrderedDict
import datetime
import serial

from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod

inputs = OrderedDict(
    serial_device=None,
    dt=1.)

class MitosPPumpController(PawsPlugin):
    """PAWS Plugin for controlling a Mitos P-pump.

    Uses a serial port (or virtual serial port)
    to communicate to a USB-attached Mitos P-pump.
    RS232 protocol settings: 
    57600 baud, 8 data bits, 1 stop bit, no parity, no handshaking.

    When the pump is in CONTROL mode,
    a command must be sent every 30 seconds,
    or the pump will automatically exit CONTROL mode.
    """
    def __init__(self):
        super(MitosPPumpController,self).__init__(inputs)
        self.input_doc['serial_device'] = 'string serial device indicator '\
            '(e.g. "COM2") or filesystem path (e.g. "/dev/ttyUSB0")'
        self.history = []
        self.ErrorsDict = { 0:'None', \
                            1:'Supply than maximum', \
                            2:'Tare time out', \
                            3:'Tare supply still connected ', \
                            4:' Control start time out', \
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
        self.connected = False
        
        self.commands = []
        self.flow_setpt = 0
        self.pressure_setpt = 0

    def add_command(self,cmd):
        self.commands.append(cmd)

    def start(self):
        if not self.connected:
            self.ser = serial.Serial(
                self.inputs['serial_device'], 
                57600, timeout=1, 
                parity = serial.PARITY_NONE, 
                bytesize = serial.EIGHTBITS, 
                xonxoff = 0, rtscts = 0)
            self.connected = True
        stat = self.read_status()
        if not stat['state_code'] == 1:
            # attempt to enter remote control mode 
            self.ser.write("A1\r\n")  
            res = self.ser.readline()
            if not res == "#A0\r\n":
                msg = "Pump failed to enter REMOTE control mode"
                raise RuntimeError(msg)
        if not self.running:
            self.running = True
            self.history = []
            if self.data_callback:
                self.data_callback('content.history',self.history)
            #self.controller = PumpController(self.inputs['serial_device'])
            dt = self.inputs['dt']
            self.history = [self.pump_status()]
            if self.data_callback:
                self.data_callback('content.history.0',self.history[0])
            self.n_points = 1
            self.t_0 = datetime.datetime.now()
            while self.running:
                time.sleep(dt)
                if len(self.commands) > 0:
                    for i in range(len(self.commands)):
                        cmd = self.commands.pop[0]
                        self.ser.write(cmd+"\r\n")
                        self.ser.readline()
                self.history.append(self.pump_status())
                if self.data_callback:
                    self.data_callback('content.history.{:i}'.format(self.n_points),self.history[self.n_points])
                    self.n_points += 1
            #self.controller.ser.write("A0\r\n")  
            #self.controller.ser.close()
            #self.controller = None
            #self.history.append("MitosPPumpController stop")

    def pump_status(self):
        s = OrderedDict()
        stat_i = self.read_status()
        t_i = datetime.datetime.now()
        t_rel = t_i - self.t_0
        s['t'] = t_rel
        s.update(stat_i)
        return s

    def content(self):
        return {'inputs':self.inputs,'history':self.history}

    def stop(self):
        if self.running:
            self.running = False

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
        self.ser.write("s\r\n") 
        tmpStrArray = self.ser.readline().split(',')
        stat = OrderedDict()
        ec = int(tmpStrArray[0][2:])
        st = int(tmpStrArray[1])
        chamber_p = int(tmpStrArray[3])
        supply_p = int(tmpStrArray[4])
        target_p = int(tmpStrArray[5])
        flow_rate = int(tmpStrArray[6])
        target_flow = int(tmpStrArray[7])
        stat['error_code'] = ec
        stat['state_code'] = st 
        stat['chamber_pressure'] = chamber_p 
        stat['supply_pressure'] = supply_p 
        stat['target_pressure'] = target_p
        stat['flow_rate'] = flow_rate 
        stat['target_flow_rate'] = target_flow 
        return stat

    def print_status(self):
        stat = self.read_status()
        msg = '----------- PUMP STATUS -----------'+os.linesep
        msg += 'Error code: {} ({})'.format(stat['error_code'],self.ErrorsDict[stat['error_code']])+os.linesep
        msg += 'State code: {} ({})'.format(stat['state_code'],self.StateDict[stat['state_code']])+os.linesep
        msg += 'Chamber pressure: \t{}'.format(stat['chamber_pressure'])+os.linesep 
        msg += 'Supply pressure: \t{}'.format(stat['supply_pressure'])+os.linesep 
        msg += 'Target pressure: \t{}'.format(stat['target_pressure'])+os.linesep 
        msg += 'Current flow rate: \t{}'.format(stat['flow_rate'])+os.linesep 
        msg += 'Target flow rate: \t{}'.format(stat['target_flow_rate'])+os.linesep 
        msg += '-----------------------------------'
        return msg

    def set_flowrate(self,rate):
        """Set the pump flow rate to the provided value.

        Parameters
        ----------
        rate : integer
            The flow rate set point, in pL/s.
            For example, rate=2000 sends 'F2000',
            which sets the flow rate to 2000 pl/s. 
        """
        self.pressure_setpt = 0
        self.flow_setpt = rate 
        self.commands.append("F{:i}\r\n".format(rate)) 

    def set_pressure(self,pressure):
        """Set the pump pressure to the provided value.

        Parameters
        ----------
        pressure : integer
            The pressure set point, in mbar.
            A value of 1000 sends the 'P1000' command,
            which sets target pressure to 1000 mbar. 
        """
        self.pressure_setpt = pressure 
        self.flow_setpt = 0 
        self.commands.append("P{:i}\r\n".format(pressure)) 

    def dispense_volume(self, vol):
        """Control the pump to dispense a specified volume.

        Parameters
        ----------
        vol : float
            The volume to dispense 
        """
        pass


