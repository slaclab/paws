from __future__ import print_function
from collections import OrderedDict

from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod

inputs = OrderedDict(serial_io_file = None)

class MitosPPumpClient(PawsPlugin):

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
            'where it is expected that a Mitos P-pump will be listening.')
        return desc

    def content(self):
        return {'inputs':self.inputs,'history':self.history}

    def stop(self):
        self.history.append("MitosPPumpClient stop")

