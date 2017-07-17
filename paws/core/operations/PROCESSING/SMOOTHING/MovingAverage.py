import numpy as np

from ... import Operation as op
from ...Operation import Operation

class MovingAverage(Operation):
    """
    Applies moving average smoothing filter to 1d array,
    optionally weighted by window shape and error values.
    """

    def __init__(self):
        input_names = ['data','window','shape','error']
        output_names = ['smoothdata']
        super(MovingAverage, self).__init__(input_names, output_names)
        self.input_doc['data'] = '1d array'
        self.input_doc['window'] = 'integer number of data points to average on either side'
        self.input_doc['shape'] = 'window shape for weighting- triangular or square (default)'
        self.input_doc['error'] = '1d array, same shape as data, optional (default None)'
        self.output_doc['smoothdata'] = 'smoothed 1d array'
        self.input_src['data'] = op.wf_input
        self.input_src['window'] = op.text_input
        self.input_src['shape'] = op.text_input
        self.input_src['error'] = op.wf_input
        self.input_type['data'] = op.ref_type
        self.input_type['window'] = op.int_type
        self.input_type['shape'] = op.str_type
        self.input_type['error'] = op.none_type
        self.inputs['window'] = 3
        self.inputs['shape'] = 'square' 

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
        self.outputs['smoothdata'] = x_out

