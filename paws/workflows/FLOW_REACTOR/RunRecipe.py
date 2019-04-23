import time

from ..Workflow import Workflow

inputs = OrderedDict(
    flow_reactor=None, 
    recipe={},
    delay_time=60.
    )

outputs = OrderedDict()

class RunRecipe(Workflow):

    def __init__(self):
        super(RunRecipe,self).__init__(inputs,outputs)

    def run(self):
        self.inputs['flow_reactor'].set_recipe(self.inputs['recipe'])
        self.message_callback('blocking {} seconds'.format(self.inputs['delay_time']))
        time.sleep(self.inputs['delay_time'])
        self.inputs['flow_reactor'].set_temperature(25.)
        self.inputs['flow_reactor'].stop_pumps()

