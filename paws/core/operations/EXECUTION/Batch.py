from collections import OrderedDict
import glob
import copy

import numpy as np

from ..Operation import Operation
from ...workflows.Workflow import Workflow
from .. import optools

inputs=OrderedDict(
    work_item=None,
    input_arrays=[],
    input_keys=[],
    static_inputs=[],
    static_input_keys=[],
    pass_thru_params={},
    order_array=None,
    order_function=None)

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

        self.input_doc['input_arrays'] = 'list of arrays, '\
            'one for each of the `input_keys`, '\
            'to be iterated over during batch execution'
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

        self.input_doc['pass_thru_params'] = 'dict of '\
            'input_name:output_name pairs, where the `work_item` input '\
            'for input_name is set using the `work_item` output output_name '\
            'from the previous execution of `work_item`. '\
            'This step is skipped for the first `work_item` in the batch. '

        self.input_doc['order_array'] = '(optional) array, '\
            'similar to input_arrays, used in conjunction '\
            'with `order_function` to determine '\
            'the order of execution of the batch- '\
            'if `order_function` is not provided, '\
            '`order_array` should be an array of real numbers'
        self.input_doc['order_function'] = '(optional) function '\
            'called on elements of `order_array` to determine '\
            'execution order, which will be '\
            'in increasing order of the return value'

        self.output_doc['batch_inputs'] = 'list of dicts, '\
            'where each dict gives the input_key:input_value pairs '\
            'used in each execution of `work_item`, '\
            'in batch execution order'
        self.output_doc['batch_outputs'] = 'list of dicts, '\
            'where each dict presents the `work_item` outputs, '\
            'in batch execution order'

        self.input_datatype['input_arrays'] = 'list'
        self.input_datatype['input_keys'] = 'list'
        self.input_datatype['static_inputs'] = 'list'
        self.input_datatype['static_input_keys'] = 'list'
        self.input_datatype['pass_thru_params'] = 'dict'

    def run(self):
        wrk = self.inputs['work_item']

        inps = self.inputs['input_arrays']
        inpks = self.inputs['input_keys']
        stat_inps = self.inputs['static_inputs']
        stat_inpks = self.inputs['static_input_keys']
        pass_thru_params = self.inputs['pass_thru_params']

        # index the execution order
        odrvals = self.inputs['order_array']
        odrfnc = self.inputs['order_function']
        if odrfnc is not None and odrvals is not None:
            odrvals = np.array([odrfnc(v) for v in odrvals])
            odr_idx = np.argsort(odrvals)
        else:
            odr_idx = np.arange(len(inps[0]))
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
        out_dict = None
        for i,idx in enumerate(odr_idx): 

            if self.stop_flag:
                self.message_callback('Batch stopped.')
                return
                
            self.message_callback('BATCH RUN {} / {}'.format(i,n_batch-1))
            wrki = wrkitms[idx]

            if any(stat_inpks): 
                for inpnm,inpval in zip(stat_inpks,stat_inps):
                    if isinstance(wrki,Workflow):
                        wrki.set_wf_input(inpnm,inpval)
                    else:
                        wrki.inputs[inpnm] = inpval

            if any(pass_thru_params) and out_dict is not None:
                for inp_name,out_name in pass_thru_params.items():
                    if isinstance(wrki,Workflow):
                        wrki.set_wf_input(inp_name,out_dict[out_name])
                    else:
                        wrki.inputs[inp_name] = out_dict[out_name]

            if isinstance(wrki,Workflow):
                wrki.execute()
                out_dict = wrki.workflow_outputs()
            else:
                # assume Operation
                wrki.run()
                out_dict = wrki.outputs
            self.outputs['batch_outputs'][i] = out_dict
            if self.data_callback: 
                self.data_callback('outputs.batch_outputs.'+str(i),copy.deepcopy(out_dict))
        self.message_callback('BATCH FINISHED')

