from collections import OrderedDict
import copy

import numpy as np

from ..Operation import Operation

inputs = OrderedDict(
    batch_outputs={},
    x_values=[],
    x_sort_flag=True,
    x_shift_flag=False, 
    lower_index=None,
    upper_index=None,
    index_step=1) 
outputs = OrderedDict(
    x_sorted = None,
    x_sorted_array = None,
    sorted_outputs = {}) 

class SortBatch(Operation):
    """
    Harvest sorted lists from a batch output (a dict of unsorted lists). 
    Takes a batch output, and a key for the values on which to sort.
    """

    def __init__(self):
        super(SortBatch,self).__init__(inputs,outputs)        
        self.input_doc['batch_outputs'] = 'dict of lists, where all lists are in corresponding order'
        self.input_doc['x_values'] = 'x data on which to sort the batch_outputs'
        self.input_doc['x_sort_flag'] = 'if True, sort data for increasing x' 
        self.input_doc['x_shift_flag'] = 'if True, shift x data so that its minimum value is zero' 
        self.input_doc['lower_index'] = 'optional list slice lower limit, inclusive'
        self.input_doc['upper_index'] = 'optional list slice upper limit, exclusive'
        self.input_doc['index_step'] = 'optional number of indices to skip between sorted outputs'
        self.output_doc['x_sorted'] = 'list of sorted x_values'
        self.output_doc['x_array_sorted'] = 'array of sorted x_values'
        self.output_doc['batch_outputs_sorted'] = 'list of sorted batch_outputs'

    def run(self):
        b_out = self.inputs['batch_outputs']
        xvals = self.inputs['x_values']
        sortflag = self.inputs['x_shift_flag']
        shiftflag = self.inputs['x_shift_flag']
        skipidx = self.inputs['index_step']
        lidx = self.inputs['lower_index']
        uidx = self.inputs['upper_index']

        n_batch_outputs = len(xvals) 
        if shiftflag or sortflag or uidx is not None or lidx is not None:
            xa = np.array(xvals)
            if shiftflag:
                xmin = min(xvals)
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
            if skipidx > 1:
                ix = ix[::skipidx]
                xa = xa[::skipidx]
            self.outputs['x_array_sorted'] = xa
            self.outputs['x_sorted'] = [xvals[int(ii)] for ii in ix]

        s_out = self.outputs['sorted_outputs']
        for y_key in b_out.keys():
            y_list = copy.deepcopy(b_out[y_key])
            if shiftflag or sortflag or uidx is not None or lidx is not None:
                # only sort y_list if it contains a full batch of outputs
                #if len(y_list) == n_batch_outputs:
                y_list = [y_list[int(ii)] for ii in ix]
            s_out[y_key] = y_list

        return self.outputs
