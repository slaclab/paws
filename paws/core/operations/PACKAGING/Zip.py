import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

class Zip(Operation):
    """
    Zip two 1d arrays together.
    """

    def __init__(self):
        input_names = ['x', 'y']
        output_names = ['x_y']
        super(Zip, self).__init__(input_names, output_names)
        self.input_doc['x'] = '1d array'
        self.input_doc['y'] = '1d array, same size as x'
        self.output_doc['x_y'] = 'n x 2 array containing x and y'
        # source & type
        self.input_type['x'] = opmod.workflow_item
        self.input_type['y'] = opmod.workflow_item

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        if x is None or y is None:
            return
        xy = np.array(zip(x, y))
        self.outputs['x_y'] = xy

