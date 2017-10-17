import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

class Window(Operation):
    """
    Window an n-by-2 array x_y 
    such that x is bounded by specified limits 
    """

    def __init__(self):
        input_names = ['x_y','x_min','x_max']
        output_names = ['x_y_window']
        super(Window,self).__init__(input_names,output_names)        
        self.input_type['x_y'] = opmod.workflow_item
        self.input_doc['x_y'] = 'n-by-2 array of x and y values'
        self.input_doc['x_min'] = 'inclusive minimum x value of output'
        self.input_doc['x_max'] = 'inclusive maximum x value of output'
        self.output_doc['x_y_window'] = 'n-by-2 array with x, y pairs for x_min <= x <= x_max'

    def run(self):
        x_y = self.inputs['x_y']
        x_min = self.inputs['x_min']
        x_max = self.inputs['x_max']
        idx_keep = ((x_y[:,0] >= x_min) & (x_y[:,0] <= x_max))
        self.outputs['x_y_window'] = x_y[idx_keep,:] 

