from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(
    flow_reactor=None,
    recipe=None,
    delay=0)
outputs=OrderedDict()
 
class SetFlowReactor(Operation):
    """Set the temperature and flow rates for a FlowReactor Plugin."""

    def __init__(self):
        super(SetFlowReactor,self).__init__(inputs,outputs)
        self.input_doc['flow_reactor'] = 'FlowReactor plugin'
        self.input_doc['recipe'] = 'dict describing temperatures and flow rates'

    def run(self):
        fr = self.inputs['flow_reactor'] 
        rcp = self.inputs['recipe']
        self.message_callback(fr.prettyprint_recipe(rcp))
        fr.set_recipe(rcp)
        d = self.inputs['delay']
        if d > 0:
            self.message_callback('blocking {} seconds'.format(d))
            time.sleep(d)
            self.message_callback('finished blocking'.format(d))
        stat = fr.print_status()
        self.message_callback(stat)

