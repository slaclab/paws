from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools
       
inputs = OrderedDict(batch_outputs=None,x_key=None,y_key=None,x_shift_flag=False) 
outputs = OrderedDict(x=None,y=None,x_y=None,x_y_sorted=None) 

class XYDataFromBatch(Operation):
    """
    Harvest two arrays from a batch output (a list of dicts). 
    Takes a batch output, a key for x values, and a key for y values.
    """

    def __init__(self):
        super(XYDataFromBatch,self).__init__(inputs,outputs)        
        self.input_doc['batch_outputs'] = 'list of dicts produced by a batch execution.'
        self.input_doc['x_uri'] = 'uri of data for x. Must be in batch.saved_items().'
        self.input_doc['y_uri'] = 'uri of data for y. Must be in batch.saved_items().'
        self.input_doc['x_shift_flag'] = 'if True, shift x data so that its minimum value is zero.' 
        self.input_type['batch_outputs'] = opmod.workflow_item
        self.output_doc['x'] = 'array of the x values in batch output order.'
        self.output_doc['y'] = 'array of the y values in batch output order.'
        self.output_doc['x_y'] = 'n-by-2 array of x and y values in batch output order.'
        self.output_doc['x_y_sorted'] = 'n-by-2 array of x and y values, sorted for increasing x.'

    def run(self):
        b_out = self.inputs['batch_outputs']
        kx = self.inputs['x_key']
        ky = self.inputs['y_key']
        #x_all = np.array([optools.get_uri_from_dict(kx,d) for d in b_out],dtype=float)
        #y_all = np.array([optools.get_uri_from_dict(ky,d) for d in b_out],dtype=float)
        x_list = []
        y_list = []
        for d in b_out:
            if kx in d and ky in d:
                x_list.append(d[kx])
                y_list.append(d[ky])
        #x_list = [d[kx] if kx in d and ky in d for d in b_out]
        #y_list = [d[ky] if kx in d and ky in d for d in b_out]
        #y_0 = b_out[0][kx]
        #x_0 = b_out[0][ky]
        x_all = np.array(x_list)
        y_all = np.array(y_list)
        x_len = len(x_list)
        if x_len > 0:
            xmin = np.min(x_all)
        else:
            xmin = 0
        if self.inputs['x_shift_flag']:
            x_all = x_all - xmin
            #xmin = 0 
        self.outputs['x'] = x_all 
        self.outputs['y'] = y_all
        self.outputs['x_y'] = np.array(zip(x_all,y_all))
        #self.outputs['x_y_sorted'] = np.sort(np.array(zip(x_all,y_all)),0)
        i_xsort = np.argsort(x_all)
        y_xsort = y_all[i_xsort]
        x_sort = x_all[i_xsort] 
        self.outputs['x_y_sorted'] = np.array(zip(x_sort,y_xsort))


