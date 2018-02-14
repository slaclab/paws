from __future__ import print_function
from collections import OrderedDict
import serial
import datetime

class PumpController(object):
    """ This class presents an API for controlling Mitos P-pumps """
    
    def __init__(self,com_port,print_diagnostics=True):
        """Initialize a pump controller.

        Parameters
        ----------
        com_port : str
            String representing COM i/o file, 
            e.g. 'COM2' or '/dev/ttyUSB1'
        print_diagnostics : bool
            Flag for whether or not to test and print some diagnostics
            after the connection is set up
        """

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

        self.com = com_port
        self.print_diag = print_diagnostics

        self.ser = serial.Serial(self.com, 57600, timeout=1, 
            parity = serial.PARITY_NONE, 
            bytesize = serial.EIGHTBITS, 
            xonxoff = 0, rtscts = 0)

        # diagnostics 
        if self.print_diag:
            self.ser.write("l\r\n")   # Returns current label on the pump
            tmpStr = self.ser.readline()
            self.ser.write("n\r\n")   # Returns the serial number for the pump
            tmpStr = tmpStr[2:-2] + ", #" + self.ser.readline()[2:-1]
            print(tmpStr)
            self.ser.write("m\r\n")   # Get the current maximum and minimum target ranges from pump
            tmpStr = self.ser.readline()
            print("Max,Min " + tmpStr[2:-2])

        # enter remote control mode 
        self.ser.write("A1\r\n")  
        tmpStr = self.ser.readline()
        if tmpStr == "#A0\r\n":
            if self.print_diag:
                print("Pump is now in remote control mode")
        else:
            msg = "Remote control mode error"
            raise RuntimeError(msg)

        self.Error = 0
        #self.State = 0

        self.ChamberPressure = 0
        self.SupplyPressure  = 0
        self.TargetPressure  = 0
        self.CurrentFlowRate = 0
        self.TargetFlowRate  = 0

    def __del__(self):
        # Leave remote control mode
        self.ser.write("A0\r\n")  
        self.ser.close()
        if self.print_diag:
            print(self.ser.readline())
            print(self.com + ' is closed')

    def set_pressure(self, pressure, timeout=10):
        """ Set the pump pressure to the provided value.

        Parameters
        ----------
        pressure : integer
            The pressure set point, in mbar.
            A value of 1000 sends the 'P1000' command,
            which sets target pressure to 1000 mbar and starts control. 
            The pump will reply '#P0' and start pressure control if in remote control mode.
            Setting target pressure to 0 (sending the "P0" command) 
            moves the pump to the IDLE state,  
            where the pump stops controlling pressure, and opens the vent valve.
        timeout : float
            Time before giving up, in seconds

        Returns
        -------
        integer
            Return code indicating 
            whether or not the pressure was set successfully
        """
        stat = self.read_status(True)
        if stat['state_code'] != 0:
            self.ser.write("C\r\n") # Clear error
            # TODO: print something informative
            print(self.ser.readline())
        self.ser.write("P%i\r\n" % pressure) 
        # TODO: print something informative
        print(self.ser.readline())

        stat = self.read_status()
        if not stat['state_code'] == 1:
            msg = 'pump is not in control mode: current state is {} ({})'\
            .format(stat['state_code'],self.StateDict[stat['state_code']])
            raise RuntimeError(msg)

        time_start = datetime.datetime.now()
        while stat['state_code'] == 1:
            stat = self.read_status()
            cp = stat['chamber_pressure']
            tp = stat['target_pressure']
            print('--- Pressure Control ---')
            print('target: {}, actual: {}'.format(tp,cp))
            print('------------------------')
            if abs(cp-tp) < tp*0.05:
                return 1
            time_elapsed = datetime.datetime.now() - time_start
            if time_elapsed.total_seconds() > timeout:
                msg = 'Timeout: Setpoint not achieved within {} seconds'\
                .format(timeout)
                print(msg)
                return 0

    def set_flowrate(self, rate, prec=0.05, timeout=10):
        """Set the pump flow rate to the provided value.

        Parameters
        ----------
        rate : integer
            The flow rate set point, in pL/s.
            For example, rate=2000 sends 'F2000',
            which sets the flow rate to 2000 pl/s. 
            The pump should reply "#F0" and start flow control, 
            if in remote control mode.
        prec : float
            Fractional precision of the flow rate.
        timeout : float
            Time before giving up, in seconds 

        Returns
        -------
        integer
            Return code indicating whether or not the flow rate was set successfully
        """

        stat = self.read_status(True)
        if stat['state_code'] != 0:
            self.ser.write("C\r\n") # Clear error
            # TODO: print something informative
            print(self.ser.readline())

        self.ser.write("F%i\r\n" % rate) 
        # TODO: print something informative
        print(self.ser.readline())

        stat = self.read_status()
        if not stat['state_code'] == 1:
            msg = 'pump is not in control mode: current state is {} ({})'\
            .format(stat['state_code'],self.StateDict[stat['state_code']])
            raise RuntimeError(msg)

        time_start = datetime.datetime.now()
        while stat['state_code'] == 1:
            stat = self.read_status()

            fr = stat['flow_rate']
            tfr = stat['target_flow_rate']
            print('----- Flow Control -----')
            print('target: {}, actual: {}'.format(tfr,fr))
            print('------------------------')
            if abs(tfr-fr) < tfr*prec:
                return 1
            time_elapsed = datetime.datetime.now() - time_start
            if time_elapsed.total_seconds() > timeout:
                msg = 'Timeout: Setpoint not achieved within {} seconds'\
                .format(timeout)
                print(msg)
                return 0
        return 1

    def dispense_volume(self, vol):
        """Control the pump to dispense a specified volume.

        Parameters
        ----------
        vol : float
            The volume to dispense 

        Returns
        -------
        integer
            Return code indicating whether or not the volume was successfully dispensed 
        """
        pass

    def read_status(self,print_diagnostic=False):
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
        if print_diagnostic:
            print('----------- PUMP STATUS -----------')
            print('Error code: {} ({})'.format(ec,self.ErrorsDict[ec]))
            print('State code: {} ({})'.format(st,self.StateDict[st]))
            print('Chamber pressure: \t{}'.format(chamber_p))
            print('Supply pressure: \t{}'.format(supply_p))
            print('Target pressure: \t{}'.format(target_p))
            print('Current flow rate: \t{}'.format(flow_rate))
            print('Target flow rate: \t{}'.format(target_flow))
            print('-----------------------------------')
        return stat

        #if self.State == 3:
        #    self.ser.write("e\r\n") 
        #    print self.ser.readline()

#--- Testing ---#

def main(argv = None):
    #print("Running...")
    #pump = PumpController('COM2')
    #pump.set_pressure(50)
    #pump.set_flowrate(500)
    pump.read_status(True)
    #print("Test finished")
	#sys.exit(1)

if __name__ == '__main__':
	main()

