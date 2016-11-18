import numpy as np

from slacxop import Operation
import optools


class Any(Operation):
    """Check whether an array has any non-zero / True elements."""

    def __init__(self):
        input_names = ['ndarray']
        output_names = ['any']
        super(Any, self).__init__(input_names, output_names)
        self.input_doc['ndarray'] = 'ndarray of any type or shape'
        self.output_doc['any'] = 'existence of any non-zero / True elements'
        # source & type
        self.input_src['ndarray'] = optools.wf_input
        self.categories = ['TESTS.NDARRAY TESTS']

    def run(self):
        self.outputs['any'] = self.inputs['ndarray'].any()


class AnyNaN(Operation):
    """Check whether an array has any NaN elements."""

    def __init__(self):
        input_names = ['ndarray']
        output_names = ['any_nan']
        super(AnyNaN, self).__init__(input_names, output_names)
        self.input_doc['ndarray'] = 'ndarray of any type or shape'
        self.output_doc['any_nan'] = 'existence of any NaN elements'
        # source & type
        self.input_src['ndarray'] = optools.wf_input
        self.categories = ['TESTS.NDARRAY TESTS']

    def run(self):
        self.outputs['any_nan'] = np.isnan(self.inputs['ndarray']).any()

class IsNaN(Operation):
    """Return boolean array marking NaN elements."""

    def __init__(self):
        input_names = ['ndarray']
        output_names = ['nan']
        super(IsNaN, self).__init__(input_names, output_names)
        self.input_doc['ndarray'] = 'ndarray of any type or shape'
        self.output_doc['nan'] = 'existence of any non-zero / True elements'
        # source & type
        self.input_src['ndarray'] = optools.wf_input
        self.categories = ['TESTS.NDARRAY TESTS']

    def run(self):
        self.outputs['nan'] = np.isnan(self.inputs['ndarray'])



class AnyZero(Operation):
    """Return boolean array marking NaN elements."""

    def __init__(self):
        input_names = ['ndarray']
        output_names = ['any_zeros']
        super(AnyZero, self).__init__(input_names, output_names)
        self.input_doc['ndarray'] = 'ndarray of any type or shape'
        self.output_doc['any_zeros'] = 'existence of any zero / False elements'
        # source & type
        self.input_src['ndarray'] = optools.wf_input
        self.categories = ['TESTS.NDARRAY TESTS']

    def run(self):
        self.outputs['any_zeros'] = np.any(np.logical_not(self.inputs['ndarray']))


class Zip(Operation):
    """Return boolean array marking NaN elements."""

    def __init__(self):
        input_names = ['ndarray_x', 'ndarray_y']
        output_names = ['ndarray_xy']
        super(Zip, self).__init__(input_names, output_names)
        self.input_doc['ndarray_x'] = '1d ndarray, x axis'
        self.input_doc['ndarray_y'] = '1d ndarray, y axis; same size as ndarray_x'
        self.output_doc['ndarray_xy'] = '2 x n ndarray for slacx autodisplay fun'
        # source & type
        self.input_src['ndarray_x'] = optools.wf_input
        self.input_src['ndarray_y'] = optools.wf_input
        self.categories = ['MISC.NDARRAY MANIPULATION']

    def run(self):
        x = self.inputs['ndarray_x']
        y = self.inputs['ndarray_y']
        n = x.size
        if len(x.shape) > 1:
            raise ValueError("ndarray_x must be a 1d array")
        if (x.shape != y.shape):
            raise ValueError("ndarray_x and ndarray_y must have the same shape")
        xy = np.zeros((2,n))
        xy[0,:] = x
        xy[1,:] = y
        self.outputs['ndarray_xy'] = xy

