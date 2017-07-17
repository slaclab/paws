import numpy as np

from .. import Operation as op
from ..Operation import Operation

class WindowZip(Operation):
    """
    From input sequences for x and y, 
    produce an n-by-2 array 
    where x is bounded by the specified limits 
    """

    def __init__(self):
        input_names = ['x','y','x_min','x_max']
        output_names = ['x_window','y_window','x_y_window']
        super(WindowZip,self).__init__(input_names,output_names)        
        self.input_src['x'] = op.wf_input
        self.input_src['y'] = op.wf_input
        self.input_src['x_min'] = op.text_input
        self.input_src['x_max'] = op.text_input
        self.input_type['x'] = op.ref_type
        self.input_type['y'] = op.ref_type
        self.input_type['x_min'] = op.float_type
        self.input_type['x_max'] = op.float_type
        self.inputs['x_min'] = 0.02 
        self.inputs['x_max'] = 0.6 
        self.input_doc['x'] = 'list (or iterable) of x values'
        self.input_doc['y'] = 'list (or iterable) of y values'
        self.input_doc['x_min'] = 'inclusive minimum x value of output'
        self.input_doc['x_max'] = 'inclusive maximum x value of output'
        self.output_doc['x_window'] = 'n-by-1 array of x_min <= x <= x_max'
        self.output_doc['y_window'] = 'n-by-1 array of y for x_min <= x <= x_max'
        self.output_doc['x_y_window'] = 'n-by-2 array with x, y pairs for x_min <= x <= x_max'

    def run(self):
        xvals = self.inputs['x']
        yvals = self.inputs['y']
        x_min = self.inputs['x_min']
        x_max = self.inputs['x_max']
        x_y_window = window_zip(xvals, yvals, x_min, x_max)
        self.outputs['x_window'] = x_y_window[:,0]
        self.outputs['y_window'] = x_y_window[:,1]
        self.outputs['x_y_window'] = x_y_window

def window_zip(x, y, x_min, x_max):
    good = ((x >= x_min) & (x <= x_max))
    return zip(x[good],y[good])

def zip(x, y):
    x_y = np.zeros((x.size, 2))
    x_y[:, 0] = x
    x_y[:, 1] = y
    return x_y

def logsafe_zip(x, y):
    bad = (x <= 0) | (y <= 0) | np.isnan(y)
    return zip(x[~bad], y[~bad])
