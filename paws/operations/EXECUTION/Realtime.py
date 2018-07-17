from collections import OrderedDict
import copy
import time

from ..Operation import Operation
from .. import optools

inputs=OrderedDict(
    work_item=None,
    input_generators={},
    static_inputs={},
    wait_delay=1.,
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

        self.input_doc['input_generators'] = 'dict of generators, '\
            'where the dict keys refer to `work_item` inputs, '\
            'and values are generators whose values are used '\
            'as inputs for each iteration of `work_item`.'
        self.input_doc['static_inputs'] = 'similar to `input_generators`, '\
            'but with single values instead of generators- '\
            'the same value is used as input on each iteration.'

        self.input_doc['wait_delay'] = 'delay in seconds '\
            'between attempts to generate new inputs'
        self.input_doc['max_delay'] = '(optional) maximum delay'\
            'in seconds, before giving up and stopping execution'
        self.input_doc['max_exec'] = '(optional) maximum number '\
            'of executions of `work_item`'
            
        self.output_doc['realtime_inputs'] = 'dict of lists, '\
            'where each list contains the realtime inputs '\
            'for the corresponding input key.'
        self.output_doc['realtime_outputs'] = 'dict of lists, '\
            'where each list contains the realtime outputs '\
            'for the corresponding output key.'
        
    def run(self):
        wrk = self.inputs['work_item']
        inp_gens = self.inputs['input_generators']
        stat_inps = self.inputs['static_inputs']
        maxdly = self.inputs['max_delay']
        maxexec = self.inputs['max_exec']
        dly = self.inputs['wait_delay']

        ins_dict = dict.fromkeys(inp_gens.keys()) 
        outs_dict = dict.fromkeys(wrk.outputs.keys()) 
        for k in inp_gens.keys():
            ins_dict[k] = []
        for k in wrk.outputs.keys():
            outs_dict[k] = [] 
        self.outputs['realtime_inputs'] = ins_dict 
        self.outputs['realtime_outputs'] = outs_dict 
        if self.data_callback: 
            self.data_callback('outputs.realtime_inputs',ins_dict)
            self.data_callback('outputs.realtime_outputs',outs_dict)

        nx = 0 # total number of executions
        keep_going = True
        if maxexec < 1: keep_going = False
        self.message_callback('STARTING REALTIME EXECUTION')
        while keep_going:
            gen_inp_dict = OrderedDict.fromkeys(inp_gens)
            inps_ready = False
            nd = 0 # number of consecutive delays
            while not inps_ready:

                # handle stop requests while waiting for new inputs
                if self.stop_flag:
                    self.message_callback('Realtime execution stopped.')
                    return
                
                inps_ready = True
                for k,gen in inp_gens.items():
                    if gen_inp_dict[k] is None:
                        gen_inp_dict[k] = next(gen)
                    if gen_inp_dict[k] is None:
                        inps_ready = False 
                if not inps_ready: 
                    time.sleep(float(dly)) 
                    nd+=1
                    currentdly = nd*dly
                    if currentdly >= maxdly:
                        msg = 'Reached maximum delay ({}): Realtime stopping.'.format(maxdly) 
                        self.message_callback(msg)
                        keep_going = False 

            if keep_going:
                for inpnm,inpval in gen_inp_dict.items():
                    wrk.set_input(inpnm,inpval)
                    ins_dict[inpnm].append(inpval)
                for inpnm,inpval in stat_inps.items():
                    wrk.set_input(inpnm,inpval)
                if self.data_callback:
                    for k,val in gen_inp_dict.items():
                        self.data_callback('outputs.realtime_inputs.'+k+'.'+str(nx),val)
                self.message_callback('REALTIME RUN {}'.format(nx))
                wrk.run()
                out_dict = wrk.get_outputs()
                for k,v in out_dict.items():
                    outs_dict[k].append(v)
                if self.data_callback: 
                    for k,val in out_dict.items():
                        self.data_callback('outputs.realtime_inputs.'+k+'.'+str(nx),val)
                nx+=1
            if nx >= maxexec:
                msg = 'Reached maximum executions ({}): Realtime stopping.'.format(maxexec) 
                self.message_callback(msg)
                keep_going = False
            if self.stop_flag:
                self.message_callback('Realtime loop stopped.')
                keep_going = False 
        self.message_callback('REALTIME EXECUTION STOPPED')

