import numpy as np

from ... import Operation as op
from ...Operation import Operation
from ... import optools

class XYDataFromBatch(Operation):
    """
    Given a batch output and appropriate keys, 
    use the uris to harvest x and y data from the batch.
    """

    def __init__(self):
        input_names = ['batch_output','x_uri','y_uri','x_shift_flag']
        output_names = ['x','y','x_y','x_y_sorted']
        super(XYDataFromBatch,self).__init__(input_names,output_names)        
        self.input_doc['batch_output'] = 'list of dicts produced by a batch execution.'
        self.input_doc['x_uri'] = 'uri of data for x. Must be in batch.saved_items().'
        self.input_doc['y_uri'] = 'uri of data for y. Must be in batch.saved_items().'
        self.input_doc['x_shift_flag'] = 'if True, shift x data so that its minimum value is zero.' 
        self.input_src['batch_output'] = op.wf_input
        self.input_src['x_uri'] = op.wf_input
        self.input_src['y_uri'] = op.wf_input
        self.input_src['x_shift_flag'] = op.text_input
        self.input_type['batch_output'] = op.ref_type
        self.input_type['x_uri'] = op.path_type
        self.input_type['y_uri'] = op.path_type
        self.input_type['x_shift_flag'] = op.bool_type
        self.inputs['x_shift_flag'] = False
        self.output_doc['x'] = 'array of the x values in batch output order.'
        self.output_doc['y'] = 'array of the y values in batch output order.'
        self.output_doc['x_y'] = 'n-by-2 array of x and y values in batch output order.'
        self.output_doc['x_y_sorted'] = 'n-by-2 array of x and y values, sorted for increasing x.'

    def run(self):
        b_out = self.inputs['batch_output']
        x_uri = self.inputs['x_uri']
        y_uri = self.inputs['y_uri']
        x_all = np.array([optools.get_uri_from_dict(x_uri,d) for d in b_out],dtype=float)
        y_all = np.array([optools.get_uri_from_dict(y_uri,d) for d in b_out],dtype=float)
        if any(x_all):
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
        x_sort = np.sort(x_all)
        y_xsort = y_all[np.argsort(x_all)]
        self.outputs['x_y_sorted'] = np.array(zip(x_sort,y_xsort))


