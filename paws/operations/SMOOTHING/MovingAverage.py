from collections import OrderedDict

import numpy as np

from ..Operation import Operation

inputs = OrderedDict(
    data=None,
    window=3,
    shape='square',
    error=None)
outputs = OrderedDict(smoothed_data=None)

class MovingAverage(Operation):
    """Applies moving average filter to 1d array."""

    def __init__(self):
        super(MovingAverage, self).__init__(inputs, outputs)
        self.input_doc['data'] = '1d array'
        self.input_doc['window'] = 'integer number of data points to average on either side'
        self.input_doc['shape'] = 'window shape for weighting- triangular or square (default)'
        self.input_doc['error'] = '1d array, same shape as data, optional (default None)'
        self.output_doc['smoothed_data'] = 'smoothed 1d array'

    def run(self):
        x = self.inputs['data']
        w = self.inputs['window']
        err = self.inputs['error']
        nx = len(x)
        if self.inputs['shape'] == 'triangle': 
            shape_weights = (w+1-np.arange(w+1, dtype=float))/float(w+1)
        else:
            shape_weights = np.ones(w+1, dtype=float)
        shape_weights = np.concatenate( (shape_weights[::-1],shape_weights[1:]))
        if err is not None:
            err_weights = err**-2
        else:
            err_weights = np.ones(x.shape, dtype=float)
        x_out = np.array([np.sum( 
                            np.array(x[max(0,i-w):min(i+w,nx)],dtype=float) 
                             * np.array(err_weights[max(0,i-w):min(i+w,nx)]) 
                             * np.array(shape_weights[max(0,w-i):min(2*(nx-i)+1,2*w+1)]) )/
                            float(min(i+w,nx-1)-max(0,i-w)) 
                            for i in range(nx) ])
        self.outputs['smoothed_data'] = x_out

