import time

from paws.plugins.Timer import Timer
from paws.plugins.MitosPPumpController import MitosPPumpController

inputs = OrderedDict(
    ppumps_setup = {},
    delay_time = 0. 
    )

outputs = OrderedDict()

class TarePumps(Workflow):

    def __init__(self):
        super(TarePumps,self).__init__(inputs,outputs)

    def run(self):
        # pump controller plugins run on timer ticks
        timer = Timer(dt=1.)
        timer.start()
        pumps = {}
        for pump_nm,setup in self.inputs['ppumps_setup'].items():
            pumps[pump_nm] = MitosPPumpController(**setup)
            pumps[pump_nm].start()
            self.message_callback('taring {}'.format(pump_nm))
            pumps[pump_nm].tare()
            # delay between tares to make it easier for a human to monitor
            time.sleep(self.inputs['delay_time'])
        # make sure all pumps are done taring
        self.message_callback('waiting 10 seconds to allow tares to finish...')
        time.sleep(10)
        # stopping the timer should signal all pump controllers to stop
        timer.stop()

