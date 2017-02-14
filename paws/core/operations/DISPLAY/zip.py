import numpy as np

from ..operation import Operation
from .. import optools

class Zip(Operation):
    """Zips two 1d ndarrays together."""

    def __init__(self):
        input_names = ['ndarray_x', 'ndarray_y']
        output_names = ['ndarray_xy']
        super(Zip, self).__init__(input_names, output_names)
        self.input_doc['ndarray_x'] = '1d ndarray, x axis'
        self.input_doc['ndarray_y'] = '1d ndarray, y axis; same size as ndarray_x'
        self.output_doc['ndarray_xy'] = 'n x 2 ndarray for automatic display plotting'
        # source & type
        self.input_src['ndarray_x'] = optools.wf_input
        self.input_src['ndarray_y'] = optools.wf_input

    def run(self):
        x = self.inputs['ndarray_x']
        y = self.inputs['ndarray_y']
        zip_check(x, y)
        xy = zip(x, y)
        self.outputs['ndarray_xy'] = xy

class LogLogZip(Operation):
    """Takes the logarithm of two 1d ndarrays, then zips them together.

    Logarithm is taken in base ten.

    Any elements with non-positive values are removed, so this operation
    may not be appropriate for computational purposes."""


    def __init__(self):
        input_names = ['ndarray_x', 'ndarray_y']
        output_names = ['ndarray_logxlogy']
        super(LogLogZip, self).__init__(input_names, output_names)
        self.input_doc['ndarray_x'] = '1d ndarray, x axis'
        self.input_doc['ndarray_y'] = '1d ndarray, y axis; same size as ndarray_x'
        self.output_doc['ndarray_logxlogy'] = 'n x 2 ndarray for automatic display plotting'
        # source & type
        self.input_src['ndarray_x'] = optools.wf_input
        self.input_src['ndarray_y'] = optools.wf_input
        self.categories = ['MISC.NDARRAY MANIPULATION','DISPLAY']

    def run(self):
        x = self.inputs['ndarray_x']
        y = self.inputs['ndarray_y']
        zip_check(x, y)
        # good_vals = elements for which both x and y have defined logarithm
        good_vals = ((x > 0) & (y > 0) & (~np.isnan(x)) & (~np.isnan(y)))
        xy = zip(np.log10(x[good_vals]), np.log10(y[good_vals]))
        self.outputs['ndarray_logxlogy'] = xy

def zip_check(x, y):
    '''
    Checks that inputs are 1d vectors of the same size and shape.
    '''
    if len(x.shape) > 1:
        raise ValueError("ndarray_x and ndarray_y must be 1d arrays")
    if (x.shape != y.shape):
        raise ValueError("ndarray_x and ndarray_y must have the same shape")

def zip(x, y):
    '''
    Zips input 1d vectors together for display.

    Should be pre-checked.
    '''
    n = x.size
    xy = np.zeros((n, 2))
    xy[:, 0] = x
    xy[:, 1] = y
    return xy
