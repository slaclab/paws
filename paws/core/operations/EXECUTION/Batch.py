from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from ...workflows.Workflow import Workflow
from .. import Operation as opmod 
from .. import optools

inputs=OrderedDict(
    work_item=None,
    order_array=None,
    order_function=None,
    input_arrays=None,
    input_keys=None,
    static_inputs=None,
    static_input_keys=None)

outputs=OrderedDict(
    batch_inputs=None,
    batch_outputs=None)
        
# TODO: unify Operation and Workflow APIs to eliminate instance checks

class Batch(Operation):
    """Batch-execute a Workflow or Operation in specific order"""

    def __init__(self):
        super(Batch,self).__init__(inputs,outputs)
        self.input_doc['work_item'] = 'the Operation '\
            'or Workflow object to be batch-executed'

        self.input_doc['order_array'] = 'array, similar to input_arrays, '\
            'used in conjunction with `order_function` to determine '\
            'the order of execution of the batch. '\
            'if `order_function` is not provided, '\
            '`order_array` should be an array of real numbers'
        self.input_doc['order_function'] = 'function called on elements '\
            'of `order_array` to determine execution order, which will be '\
            'in increasing order of the return value'

        self.input_doc['input_arrays'] = 'one array for each of '\
            'the `input_keys`, to be iterated over during batch execution.'
        self.input_doc['input_keys'] = 'list of keys for setting '\
            'batch inputs of the `work_item`- these should correspond to '\
            'either Operation.inputs or Workflow.inputs, '\
            'depending on whether `work_item` is an Operation or a Workflow'

        self.input_doc['static_inputs'] = 'one object for each of '\
            'the `work_item` inputs indicated by `static_input_keys`, '\
            'to be set to the same value across the entire batch'
        self.input_doc['static_input_keys'] = 'list of keys for setting '\
            'static inputs of the `work_item`- these should correspond to '\
            'either Operation.inputs or Workflow.inputs, '\
            'depending on whether `work_item` is an Operation or a Workflow'
            
        self.output_doc['batch_inputs'] = 'list of dicts, '\
            'where each dict gives the input_key:input_value pairs '\
            'used in each execution of `work_item`, '\
            'in batch execution order'
        self.output_doc['batch_outputs'] = 'list of dicts, '\
            'where each dict presents the `work_item` outputs, '\
            'in batch execution order'

        self.input_type['workflow'] = opmod.entire_workflow
        
    def run(self):
        # index the execution order
        odrvals = self.inputs['order_array']
        odrfnc = self.inputs['order_function']

        inps = self.inputs['input_arrays']
        inpks = self.inputs['input_keys']

        if odrfnc is not None and odrvals is not None:
            odrvals = np.array([odrfnc(v) for v in odrvals])
            odr_idx = np.argsort(odrvals)
        else:
            odr_idx = np.arange(len(inps[0]))

        #odr = odrvals[odr_idx]
        stat_inps = self.inputs['static_inputs']
        stat_inpks = self.inputs['static_input_keys']

        wrk = self.inputs['work_item']

        n_batch = len(odr_idx)

        # copy the work item and index it
        if isinstance(wrk,Workflow):
            wrkitms = [wrk.clone_wf() for idx in odr_idx]
        else:
            # assume Operation
            wrkitms = [wrk.clone_op() for idx in odr_idx]
            
        batch_inp_dicts = []
        for idx,wrkitm in zip(odr_idx,wrkitms):
            batch_inps = OrderedDict.fromkeys(inpks)
            for inpk,inp in zip(inpks,inps):
                wrkitm.set_wf_input(inpk,inp[idx])
                batch_inps[inpk] = inp[idx]
            batch_inp_dicts.append(batch_inps)

        self.outputs['batch_inputs'] = batch_inp_dicts 
        self.outputs['batch_outputs'] = [None for ib in range(n_batch)] 
        if self.data_callback: 
            self.data_callback('outputs.batch_inputs',copy.deepcopy(batch_inp_dicts))
            self.data_callback('outputs.batch_outputs',[None for ib in range(n_batch)])

        self.message_callback('STARTING BATCH')
        for i,idx in enumerate(odr_idx): 
            self.message_callback('BATCH RUN {} / {}'.format(i,n_batch-1))
            wrki = wrkitms[idx]

            if any(stat_inpks): 
                for inpnm,inpval in zip(stat_inpks,stat_inps):
                    if isinstance(wrki,Workflow):
                        wrki.set_wf_input(inpnm,inpval)
                    else:
                        # assume it's an Operation
                        wrki.inputs[inpnm] = inpval

            if isinstance(wrki,Workflow):
                wrki.execute()
                out_dict = wrki.wf_outputs_dict()
            else:
                # assume Operation
                wrki.run()
                out_dict = wrki.outputs
            self.outputs['batch_outputs'][i] = out_dict
            if self.data_callback: 
                self.data_callback('outputs.batch_outputs.'+str(i),copy.deepcopy(out_dict))
        self.message_callback('BATCH FINISHED')

