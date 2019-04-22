import time
from collections import OrderedDict

from ...plugins.Timer import Timer
from ...plugins.MitosPPumpController import MitosPPumpController

inputs = OrderedDict(
    ppumps_setup = {},
    flowrates = {},
    delay_time = 0. 
    )

outputs = OrderedDict()

class FlushPumps(Workflow):

    def __init__(self):
        super(TarePumps,self).__init__(inputs,outputs)

    def run(self):
        # pump controller plugins run on timer ticks
        timer = Timer(dt=1.)
        timer.start()
        pumps = {}
        for pump_nm,setup in self.inputs['ppumps_setup'].items():
            pumps[pump_nm] = MitosPPumpController(
                timer=timer,verbose=self.inputs['verbose'],**setup)
            pumps[pump_nm].start()
            pumps[pump_nm].set_flowrate(self.inputs['flowrates'][pump_nm])
        time.sleep(self.inputs['delay_time'])
        timer.stop()

