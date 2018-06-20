from collections import OrderedDict

import numpy as np

from ...Operation import Operation

inputs = OrderedDict(
    batch_outputs=None,
    x_key=None,
    y_key=None,
    x_sort_flag=False,
    x_shift_flag=False, 
    lower_index=None,
    upper_index=None) 
outputs = OrderedDict(
    x=None,
    y=None,
    x_y=None) 

class XYDataFromBatch(Operation):
    """
    Harvest two arrays from a batch output (a list of dicts). 
    Takes a batch output, a key for x values, and a key for y values.
    """

    def __init__(self):
        super(XYDataFromBatch,self).__init__(inputs,outputs)        
        self.input_doc['batch_outputs'] = 'list of dicts produced by a batch execution'
        self.input_doc['x_key'] = 'key for x data from batch_outputs'
        self.input_doc['y_key'] = 'key for y data from batch_outputs'
        self.input_doc['x_sort_flag'] = 'if True, sort data for increasing x' 
        self.input_doc['x_shift_flag'] = 'if True, shift x data so that its minimum value is zero' 
        self.input_doc['lower_index'] = 'optional list slice lower limit, inclusive'
        self.input_doc['upper_index'] = 'optional list slice upper limit, exclusive'
        self.output_doc['x'] = 'array of the x values'
        self.output_doc['y'] = 'array of the y values'
        self.output_doc['x_y'] = 'n-by-2 array of x and y values'

    def run(self):
        b_out = self.inputs['batch_outputs']
        kx = self.inputs['x_key']
        ky = self.inputs['y_key']
        sortflag = self.inputs['x_shift_flag']
        shiftflag = self.inputs['x_shift_flag']
        lidx = self.inputs['lower_index']
        uidx = self.inputs['upper_index']

        x_list = []
        y_list = []
        for d in b_out:
            if kx in d and ky in d:
                x_list.append(d[kx])
                y_list.append(d[ky])
        if shiftflag or sortflag:
            xa = np.array(x_list)
            ya = np.array(y_list)
        if shiftflag:
            xmin = min(x_list)
            xa = xa - xmin
        ix = np.arange(len(xa))
        if sortflag:
            ix = np.argsort(xa)
        if lidx is not None:
            ix = ix[lidx:]
            if uidx is not None:
                uidx = uidx-lidx
        if uidx is not None:
            ix = ix[:uidx]

        if shiftflag or sortflag or uidx is not None or lidx is not None:
            x_list = [x_list[int(ii)] for ii in ix]
            y_list = [y_list[int(ii)] for ii in ix]

        self.outputs['x'] = x_list
        self.outputs['y'] = y_list
        self.outputs['x_y'] = zip(x_list,y_list)

