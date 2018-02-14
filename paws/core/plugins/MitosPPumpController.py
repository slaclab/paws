from __future__ import print_function
from collections import OrderedDict

from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod

from paws import PumpController

inputs = OrderedDict(serial_device=None)

class MitosPPumpController(PawsPlugin):
    """PAWS Plugin for controlling a Mitos P-pump.

    Uses a serial port (or virtual serial port)
    to communicate to a USB-attached Mitos P-pump.
    RS232 protocol settings: 
    57600 baud, 8 data bits, 1 stop bit, no parity, no handshaking
    """
    def __init__(self):
        super(MitosPPumpController,self).__init__(inputs)
        self.input_doc['serial_device'] = 'filesystem path '\
            'pointing to serial device io pseudo-file'
        self.history = [] 
        self.controller = None

    def start(self):
        self.controller = PumpController.PumpController(self.inputs['serial_device'])
        pass

    def description(self):
        desc = 'MitosPPumpController Plugin: '\
            'This is a TCP Client used to operate a Mitos P-Pump. '\
            'Startup requires a serial io device, '\
            'where a Mitos P-pump should be listening.'
        return desc

    def content(self):
        return {'inputs':self.inputs,'history':self.history,'controller':self.controller}

    def stop(self):
        self.history.append("MitosPPumpController stop")

