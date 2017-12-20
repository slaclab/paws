from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools
       
inputs = OrderedDict(
    batch_outputs=None,
    x_key=None,
    y_key=None,
    x_sort_flag=False,
    x_shift_flag=False) 
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
        self.output_doc['x'] = 'array of the x values'
        self.output_doc['y'] = 'array of the y values'
        self.output_doc['x_y'] = 'n-by-2 array of x and y values'

    def run(self):
        b_out = self.inputs['batch_outputs']
        kx = self.inputs['x_key']
        ky = self.inputs['y_key']
        sortflag = self.inputs['x_shift_flag']
        shiftflag = self.inputs['x_shift_flag']
        x_list = []
        y_list = []
        for d in b_out:
            if kx in d and ky in d:
                x_list.append(d[kx])
                y_list.append(d[ky])
        if shiftflag or sortflag:
            x_all = np.array(x_list)
            y_all = np.array(y_list)
        if shiftflag and len(x_list)>0:
            xmin = min(x_list)
            x_all = x_all - xmin
            x_list = list(x_all)
        if sortflag:
            i_xsort = np.argsort(x_all)
            x_list = list(x_all[i_xsort])
            y_list = list(y_all[i_xsort])
        self.outputs['x'] = x_list
        self.outputs['y'] = y_list
        self.outputs['x_y'] = zip(x_list,y_list)


