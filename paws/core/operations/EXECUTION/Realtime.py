from collections import OrderedDict
import copy
import time

from ..Operation import Operation
from .. import optools

inputs=OrderedDict(
    work_item=None,
    input_generators=[],
    input_keys=[],
    static_inputs=[],
    static_input_keys=[],
    delay=1.,
    max_delay=float('inf'),
    max_exec=float('inf'))

outputs=OrderedDict(
    realtime_inputs=None,
    realtime_outputs=None)

class Realtime(Operation):
    """Realtime-execute a Workflow or Operation"""

    def __init__(self):
        super(Realtime,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'the Operation '\
            'or Workflow object to be executed in real time'

        self.input_doc['input_generators'] = 'one generator for each of '\
            'the `input_keys`, to generate inputs during execution- '\
            '`work_item` will be executed when all of the generators '\
            'return a value that is not None'
        self.input_doc['input_keys'] = 'list of keys for setting '\
            'inputs of the `work_item`- these should correspond to '\
            'either Operation.inputs or Workflow.inputs, '\
            'depending on whether `work_item` is an Operation or a Workflow'

        self.input_doc['static_inputs'] = 'one object for each of '\
            'the `work_item` inputs indicated by `static_input_keys`, '\
            'to be set to the same value for every execution'
        self.input_doc['static_input_keys'] = 'list of keys for setting '\
            'static inputs of the `work_item`- these should correspond to '\
            'either Operation.inputs or Workflow.inputs, '\
            'depending on whether `work_item` is an Operation or a Workflow'
            
        self.input_doc['delay'] = 'delay in seconds '\
            'between attempts to generate new inputs'
        self.input_doc['max_delay'] = '(optional) maximum delay'\
            'in seconds, before giving up and stopping execution'
        self.input_doc['max_exec'] = '(optional) maximum number '\
            'of executions of `work_item`'
            
        self.output_doc['realtime_inputs'] = 'list of dicts '\
            'containing [input_name:input_value] '\
            'for each execution of `work_item`'
        self.output_doc['realtime_outputs'] = 'list of dicts '\
            'containing [output_name:output_value] '\
            'for each execution of `work_item`'
        
    def run(self):
        wrk = self.inputs['work_item']
        inp_gens = self.inputs['input_generators']
        inpks = self.inputs['input_keys']
        stat_inps = self.inputs['static_inputs']
        stat_inpks = self.inputs['static_input_keys']
        maxdly = self.inputs['max_delay']
        maxexec = self.inputs['max_exec']
        dly = self.inputs['delay']

        self.outputs['realtime_inputs'] = [] 
        self.outputs['realtime_outputs'] = [] 
        if self.data_callback: 
            self.data_callback('outputs.realtime_inputs',[])
            self.data_callback('outputs.realtime_outputs',[])

        nx = 0 # total number of executions
        keep_going = True
        self.message_callback('STARTING REALTIME EXECUTION')
        while keep_going:
            # collect inputs from inp_gens
            inp_dict = OrderedDict.fromkeys(inpks)
            inps_ready = False
            nd = 0 # number of consecutive delays
            if nx >= maxexec:
                msg = 'Reached maximum executions ({}): Realtime stopping.'.format(maxexec) 
                self.message_callback(msg)
                keep_going = False
            while keep_going and not inps_ready:

                if self.stop_flag:
                    self.message_callback('Realtime execution stopped.')
                    return
                
                for k,gen in zip(inpks,inp_gens):
                    if inp_dict[k] is None:
                        inp_dict[k] = gen.next()
                if all([inp_dict[k] is not None for k in inpks]):
                    inps_ready = True
                    if self.data_callback: 
                        self.data_callback('outputs.realtime_inputs.'+str(nx),copy.deepcopy(inp_dict))
                else:
                    # delay
                    time.sleep(float(dly)) 
                    nd+=1
                    currentdly = nd*dly
                    #self.message_callback('... WAITING FOR INPUTS ({}/{} ms)'
                    #    .format(currentdly,maxdly))
                    if currentdly >= maxdly:
                        keep_going = False 
            if keep_going:
                for inpnm,inpval in inp_dict.items():
                    wrk.set_input(inpnm,inpval)
                if any(stat_inpks): 
                    for inpnm,inpval in zip(stat_inpks,stat_inps):
                        wrk.set_input(inpnm,inpval)
                self.message_callback('REALTIME RUN {}'.format(nx))
                wrk.run()
                out_dict = wrk.get_outputs()
                self.outputs['realtime_outputs'].append(out_dict)
                if self.data_callback: 
                    self.data_callback('outputs.realtime_outputs.'+str(nx),copy.deepcopy(out_dict))
                nx+=1
        self.message_callback('REALTIME EXECUTION STOPPED')

