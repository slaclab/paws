from __future__ import print_function
from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from .. import optools

inputs=OrderedDict(
    work_item=None,
    batch_inputs={},
    static_inputs={},
    serial_params={})

outputs=OrderedDict(
    batch_outputs={})
        
class Batch(Operation):
    """Batch-execute a Workflow or Operation in specific order"""

    def __init__(self):
        super(Batch,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'the Operation '\
            'or Workflow object to be batch-executed'
        self.input_doc['batch_inputs'] = 'dict of iterables, '\
            'where the dict keys refer to `work_item` inputs, '\
            'and the iterablevalues are used '\
            'as inputs for each execution in the batch.'
        self.input_doc['static_inputs'] = 'similar to `batch_inputs`, '\
            'but with single values instead of iterables- '\
            'the same value is used as input on each iteration.'
        self.input_doc['serial_inputs'] = 'dict of '\
            'input_name:output_name pairs, where the `work_item` input '\
            'for input_name is set using the `work_item` output output_name '\
            'from the previous execution of `work_item`. '\
            'This is not applied for the first `work_item` in the batch. '

        self.output_doc['batch_outputs'] = 'dict of lists, '\
            'where each list contains the batch of outputs '\
            'for the corresponding output key.'
            
        self.input_datatype['batch_inputs'] = dict
        self.input_datatype['static_inputs'] = dict
        self.input_datatype['serial_params'] = dict

    def run(self):
        #wrkitm = self.inputs['work_item'].build_clone()
        wrkitm = self.inputs['work_item']
        inps = self.inputs['batch_inputs']

        stat_inps = self.inputs['static_inputs']
        ser_params = self.inputs['serial_params']

        batch_size = len(list(inps.values())[0])

        outs_dict = dict.fromkeys(wrkitm.outputs.keys())
        for k in outs_dict:
            outs_dict[k] = []
        self.outputs['batch_outputs'] = outs_dict
        if self.data_callback:
            self.data_callback('outputs.batch_outputs',outs_dict)

        self.message_callback('STARTING BATCH')

        out_dict = None
        for batch_idx in range(batch_size):
            inp_dict = OrderedDict()
            if any(ser_params) and out_dict is not None:
                for inp_name,out_name in ser_params.items():
                    inp_dict[inp_name] = out_dict[out_name]
            for k in inps.keys():
                inp_dict[k] = inps[k][batch_idx]
            for k in stat_inps.keys():
                inp_dict[k] = stat_inps[k]
            for inp_name,inp_value in inp_dict.items():
                wrkitm.set_input(inp_name,inp_value)
 
            self.message_callback('BATCH RUN {} / {}'.format(batch_idx,batch_size-1))
            wrkitm.run()
            out_dict = copy.deepcopy(wrkitm.get_outputs())

            for k,v in out_dict.items():
                outs_dict[k].append(v)
                if self.data_callback: 
                    self.data_callback('outputs.batch_outputs.'+k+'.'+str(batch_idx),v)
            if self.stop_flag:
                self.message_callback('Batch stopped.')
                return
        
        self.message_callback('BATCH FINISHED')

