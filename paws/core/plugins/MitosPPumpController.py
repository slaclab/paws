from __future__ import print_function
from collections import OrderedDict
import datetime
import serial
import time
import copy
import os
import sys
if int(sys.version[0]) == 2:
    import Queue as queue
else:
    import queue 

import tzlocal

from .PawsPlugin import PawsPlugin
from .. import pawstools

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
        self.history = []
        self.n_events = 0
        self.content = OrderedDict(
            history=self.history,
            state=self.state)
        self.commands = queue.Queue() 

    def start(self):
        self.tz = tzlocal.get_localzone()
        self.t_0 = datetime.datetime.now(self.tz)
        t_utc = time.mktime(self.t_0.timetuple())
        cmd='clock started'
        resp='t_0 = {}'.format(t_utc)
        self.add_to_history(cmd,resp)
        self.ser = serial.Serial(
            self.inputs['serial_device'], 
            57600, timeout=1, 
            parity = serial.PARITY_NONE, 
            bytesize = serial.EIGHTBITS, 
            xonxoff = 0, rtscts = 0)
        self.add_to_history('connected {}'.format(self.inputs['serial_device']),'')
        # clear the pump...
        cmd = "C"
        self.send_line(cmd)
        resp = self.receive_line()
        self.add_to_history(cmd,resp)
        self.read_status()
        if not self.state['state_code'] == 1:
            # attempt to enter remote control mode 
            cmd = "A1"
            self.send_line(cmd)  
            resp = self.receive_line()
            self.add_to_history(cmd,resp)
            if not resp == "#A0":
                msg = "Pump failed to enter REMOTE control mode"
                self.add_to_history('ERROR',msg)
                self.dump_history()
                raise RuntimeError(msg)
        self.read_status()
        self.running = True
        while self.running:
            while self.commands.qsize() > 0: 
                cmd = copy.deepcopy(self.commands.get())
                self.commands.task_done()
                self.send_line(cmd)
                resp = self.receive_line()
                self.add_to_history(cmd,resp)
            self.read_status()
            time.sleep(self.inputs['dt'])
        cmd = "C"
        self.send_line(cmd) 
        resp = self.receive_line()
        self.add_to_history(cmd,resp)
        self.read_status()
        t_now = datetime.datetime.now(self.tz)
        while not self.state['state_code'] == 0:
            # wait for IDLE mode 
            time.sleep(self.inputs['dt'])
            t_passed = (datetime.datetime.now(self.tz)-t_now).total_seconds()    
            if t_passed > 30:
                msg = 'Waited more than 30 seconds for pump to go IDLE'
                raise RuntimeError(msg)
        cmd = "A0"
        self.send_line(cmd)
        resp = self.receive_line()
        self.add_to_history(cmd,resp)
        self.ser.close()
        self.add_to_history('closed {}'.format(self.inputs['serial_device']),'')
        self.dump_history()

    def send_line(self,line):
        self.ser.write("{}\r\n".format(line))  

    def receive_line(self):
        r = self.ser.readline()
        return r.strip()

    def add_to_history(self,cmd,resp):
        self.history.append(self.event(cmd,resp))
        if self.data_callback:
            self.data_callback('content.history.{}'.format(self.n_events),
                copy.deepcopy(self.history[self.n_events]))
        self.n_events += 1

    def event(self,cmd,resp):
        t = (datetime.datetime.now(self.tz) - self.t_0).total_seconds()
        event = OrderedDict(t=t,command=cmd,response=resp)
        return event


    def dump_history(self):
        dump_path = os.path.join(pawstools.paws_scratch_dir,'ppump_controller_{}.log'.format(self))
        dump_file = open(dump_path,'w')
        dump_file.write('t \tcommand \tresponse\n')
        for ev in self.history:
            dump_file.write('{} \t{} \t{}\n'.format(ev['t'],ev['command'],ev['response']))
        dump_file.close()

    #def pump_status(self):
    #    s = OrderedDict()
    #    t_i = datetime.datetime.now()
    #    t_rel = float((t_i - self.t_0).total_seconds())
    #    s['t'] = t_rel
    #    self.read_status()
    #    s.update(copy.deepcopy(self.state)) 
    #    return s

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
        s = resp.split(',')
        while '' in s or len(s) < 8:
            self.send_line(cmd)
            resp = self.receive_line()
            s = resp.split(',')
        self.add_to_history(cmd,resp)
        self.state['error_code'] = int(s[0][2:])
        self.state['state_code'] = int(s[1])
        self.state['chamber_pressure'] = float(s[3])
        self.state['supply_pressure'] = float(s[4])
        self.state['target_pressure'] = float(s[5])
        self.state['flow_rate'] = float(s[6])
        self.state['target_flow_rate'] = float(s[7])
        if self.data_callback:
            self.data_callback('content.state',copy.deepcopy(self.state))

    #def print_status(self):
    #    msg = '----------- PUMP STATUS -----------'+os.linesep
    #    msg += 'Error code: {} ({})'.format(self.state['error_code'],
    #        self.ErrorsDict[self.state['error_code']])+os.linesep
    #    msg += 'State code: {} ({})'.format(self.state['state_code'],
    #        self.StateDict[self.state['state_code']])+os.linesep
    #    msg += 'Chamber pressure: \t{}'.format(self.state['chamber_pressure'])+os.linesep 
    #    msg += 'Supply pressure: \t{}'.format(self.state['supply_pressure'])+os.linesep 
    #    msg += 'Target pressure: \t{}'.format(self.state['target_pressure'])+os.linesep 
    #    msg += 'Current flow rate: \t{}'.format(self.state['flow_rate'])+os.linesep 
    #    msg += 'Target flow rate: \t{}'.format(self.state['target_flow_rate'])+os.linesep 
    #    msg += '-----------------------------------'
    #    return msg

    def set_flowrate(self,rate):
        """Set the pump flow rate to the provided value.

        Parameters
        ----------
        rate : integer
            The flow rate set point, in pL/s.
            For example, rate=2000 sends 'F2000',
            which sets the flow rate to 2000 pl/s. 
        """
        self.plugin_clone.commands.put("F{}".format(rate)) 

    def set_pressure(self,pressure):
        """Set the pump pressure to the provided value.

        Parameters
        ----------
        pressure : integer
            The pressure set point, in mbar.
            A value of 1000 sends the 'P1000' command,
            which sets target pressure to 1000 mbar. 
        """
        self.plugin_clone.commands.put("P{}".format(pressure)) 

    def dispense_volume(self, vol):
        """Control the pump to dispense a specified volume.

        Parameters
        ----------
        vol : float
            The volume to dispense 
        """
        pass

