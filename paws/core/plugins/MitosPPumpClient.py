from __future__ import print_function
from collections import OrderedDict

from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod

inputs = OrderedDict(serial_io_file = None)

class MitosPPumpClient(PawsPlugin):
    """PAWS Plugin for controlling a Mitos P-pump.

    Uses a virtual serial port 
    to communicate to a USB_attached Mitos P-pump.
    RS232 protocol settings: 
    57600 baud, 8 data bits, 1 stop bit, no parity, no handshaking
    """
    def __init__(self):
        super(MitosPPumpClient,self).__init__(inputs)
        self.input_doc['serial_io_file'] = 'filesystem path '\
            'pointing to serial device io pseudo-file'
        self.history = [] 

    def start(self):
        pass

    def description(self):
        desc = 'MitosPPumpClient Plugin: '\
            'This is a TCP Client used to operate a Mitos P-Pump. '\
            'Startup requires a serial device, '\
            'where a Mitos P-pump should be listening.'
        return desc

    def content(self):
        return {'inputs':self.inputs,'history':self.history}

    def stop(self):
        self.history.append("MitosPPumpClient stop")

