from collections import OrderedDict
import copy

import numpy as np

from ..Operation import Operation

inputs = OrderedDict(
    batch_outputs={},
    x_key=None,
    x_sort_flag=True,
    x_shift_flag=False, 
    lower_index=None,
    upper_index=None) 
outputs = OrderedDict(
    x_list = None,
    x_array = None,
    sorted_outputs = {}) 

class SortBatch(Operation):
    """
    Harvest sorted lists from a batch output (a dict of unsorted lists). 
    Takes a batch output, and a key for the values on which to sort.
    """

    def __init__(self):
        super(SortBatch,self).__init__(inputs,outputs)        
        self.input_doc['batch_outputs'] = 'dict of lists, where all lists are in corresponding order'
        self.input_doc['x_key'] = 'key for x data from batch_outputs'
        self.input_doc['x_sort_flag'] = 'if True, sort data for increasing x' 
        self.input_doc['x_shift_flag'] = 'if True, shift x data so that its minimum value is zero' 
        self.input_doc['lower_index'] = 'optional list slice lower limit, inclusive'
        self.input_doc['upper_index'] = 'optional list slice upper limit, exclusive'
        self.output_doc['x_list'] = 'list of values of x (sorted)'
        self.output_doc['x_array'] = 'array of values of x (sorted)'
        self.output_doc['sorted_outputs'] = 'dict similar to inputs, but sorted on `x_key`'

    def run(self):
        b_out = self.inputs['batch_outputs']

        kx = self.inputs['x_key']
        sortflag = self.inputs['x_shift_flag']
        shiftflag = self.inputs['x_shift_flag']
        lidx = self.inputs['lower_index']
        uidx = self.inputs['upper_index']

        x_list = b_out[kx]
        n_batch_outputs = len(x_list) 
        if shiftflag or sortflag or uidx is not None or lidx is not None:
            xa = np.array(x_list)
            if shiftflag:
                xmin = min(x_list)
                xa = xa - xmin
            ix = np.arange(len(xa))
            if sortflag:
                ix = np.argsort(xa)
            xa = xa[ix]
            if lidx is not None:
                ix = ix[lidx:]
                xa = xa[lidx:]
                if uidx is not None:
                    uidx = uidx-lidx
            if uidx is not None:
                ix = ix[:uidx]
                xa = xa[:uidx]
            self.outputs['x_array'] = xa
            self.outputs['x_list'] = [x_list[int(ii)] for ii in ix]

        self.message_callback('sorting {} on key: "{}"'.format(list(b_out.keys()),kx))
        s_out = self.outputs['sorted_outputs']
        for y_key in b_out.keys():
            y_list = copy.deepcopy(b_out[y_key])

            if shiftflag or sortflag or uidx is not None or lidx is not None:
                # only sort y_list if it contains a full batch of outputs
                if len(y_list) == n_batch_outputs:
                    y_list = [y_list[int(ii)] for ii in ix]
        
            s_out[y_key] = y_list

        return self.outputs

