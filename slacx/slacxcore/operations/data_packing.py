import numpy as np

from slacxop import Operation
import optools

class WindowZip(Operation):
    """
    From input iterables of x and y, 
    produce an n-by-2 array 
    where x is bounded by the specified limits 
    """

    def __init__(self):
        input_names = ['x','y','x_min','x_max']
        output_names = ['x_y_window']
        super(WindowZip,self).__init__(input_names,output_names)        
        self.input_src['x'] = optools.wf_input
        self.input_src['y'] = optools.wf_input
        self.input_src['x_min'] = optools.user_input
        self.input_src['x_max'] = optools.user_input
        self.input_type['x_min'] = optools.float_type
        self.input_type['x_max'] = optools.float_type
        self.inputs['x_min'] = 0.02 
        self.inputs['x_max'] = 0.6 
        self.input_doc['x'] = 'list (or iterable) of x values'
        self.input_doc['y'] = 'list (or iterable) of y values'
        self.output_doc['x_y_window'] = 'n-by-2 array with x, y pairs for x_min<x<x_max'
        self.categories = ['PACKAGING']

    def run(self):
        xvals = self.inputs['x']
        yvals = self.inputs['y']
        x_min = self.inputs['x_min']
        x_max = self.inputs['x_max']
        idx_good = ((xvals > x_min) & (xvals < x_max))
        x_y_window = np.zeros((idx_good.sum(),2))
        x_y_window[:,0] = xvals[idx_good]
        x_y_window[:,1] = yvals[idx_good]
        self.outputs['x_y_window'] = x_y_window

class Window_q_I_2(Operation):
    """
    From input iterables of *q_list_in* and *I_list_in*,
    produce two 1d vectors
    where q is greater than *q_min* and less than *q_min*
    """

    def __init__(self):
        input_names = ['q_list_in','I_list_in','q_min','q_max']
        output_names = ['q_list_out','I_list_out']
        super(Window_q_I_2,self).__init__(input_names,output_names)
        # docstrings
        self.input_doc['q_list_in'] = '1d iterable listing q values'
        self.input_doc['I_list_in'] = '1d iterable listing I values'
        self.input_doc['q_min'] = 'lowest value of q of interest'
        self.input_doc['q_max'] = 'highest value of q of interest'
        self.output_doc['q_list_out'] = '1d iterable listing q values where q is between *q_min* and *q_max*'
        self.output_doc['I_list_out'] = '1d iterable listing I values where q is between *q_min* and *q_max*'
        # source & type
        self.input_src['q_list_in'] = optools.wf_input
        self.input_src['I_list_in'] = optools.wf_input
        self.input_src['q_min'] = optools.user_input
        self.input_src['q_max'] = optools.user_input
        self.input_type['q_min'] = optools.float_type
        self.input_type['q_max'] = optools.float_type
        self.inputs['q_min'] = 0.02
        self.inputs['q_max'] = 0.6
        self.categories = ['PACKAGING']

    def run(self):
        qvals = self.inputs['q_list_in']
        ivals = self.inputs['I_list_in']
        q_min = self.inputs['q_min']
        q_max = self.inputs['q_max']
        if (q_min >= q_max):
            raise ValueError("*q_max* must be greater than *q_min*.")
        good_qvals = ((qvals > q_min) & (qvals < q_max))
        self.outputs['q_list_out'] = qvals[good_qvals]
        self.outputs['I_list_out'] = ivals[good_qvals]


