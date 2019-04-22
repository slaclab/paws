import os
import time
import copy
import pprint

import numpy as np
import pandas as pd
import yaml

from paws.plugins.Timer import Timer
from paws.plugins.FlowReactor import FlowReactor

inputs = OrderedDict(
    ppumps_setup={},
    cryocon_setup={},
    timer_dt=1.,
    recipe={},
    delay_time=60.,
    verbose=False,
    log_file=None
    )

outputs = OrderedDict()

class RunRecipe(Workflow):

    def __init__(self):
        super(RunRecipe,self).__init__(inputs,outputs)

    def run(self):
        timer = Timer(dt=self.inputs['timer_dt'])
        timer.start()
        flow_reactor = FlowReactor(
            timer=timer,
            ppumps_setup=ppumps_setup,
            cryocon_setup=cryocon_setup,
            verbose=self.inputs['verbose'],
            log_file=self.inputs['log_file']
            )
        flow_reactor.start()
        flow_reactor.set_recipe(rcp)
        self.message_callback('blocking {} seconds'.format(self.inputs['delay_time']))
        time.sleep(self.inputs['delay_time'])
        flow_reactor.set_temperature(25.)
        flow_reactor.stop()
        timer.stop()

