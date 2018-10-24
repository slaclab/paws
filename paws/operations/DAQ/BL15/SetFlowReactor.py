from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(
    flow_reactor=None,
    recipe=None,
    delay_time=0,
    delay_volume=0)
outputs=OrderedDict()
 
class SetFlowReactor(Operation):
    """Set the temperature and flow rates for a FlowReactor Plugin."""

    def __init__(self):
        super(SetFlowReactor,self).__init__(inputs,outputs)
        self.input_doc['flow_reactor'] = 'FlowReactor plugin'
        self.input_doc['recipe'] = 'dict describing temperatures and flow rates'
        self.input_doc['delay_time'] = 'minimum time (seconds) to wait after recipe is set'
        self.input_doc['delay_volume'] = 'minimum volume (microlitres) to pump after recipe is set'

    def run(self):
        fr = self.inputs['flow_reactor'] 
        rcp = self.inputs['recipe']
        #self.message_callback(fr.prettyprint_recipe(rcp))
        fr.set_recipe(rcp)
        delvol = self.inputs['delay_volume']
        del_time = self.inputs['delay_time']
        vol_time = 60*delvol/rcp['flowrate']
        if del_time > vol_time:
            self.message_callback('blocking {} seconds'.format(del_time))
            time.sleep(del_time)
            self.message_callback('finished blocking')
        else:
            msg = 'blocking {} seconds to pump {} microlitres'.format(vol_time,delvol)
            self.message_callback(msg)
            time.sleep(vol_time)
            self.message_callback('finished blocking')
        flag,statstr,statdict = fr.check_status()
        self.message_callback(statstr)

