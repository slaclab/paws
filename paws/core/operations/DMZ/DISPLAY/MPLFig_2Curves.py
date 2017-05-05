from matplotlib import pyplot as plt

from ..Operation import Operation
from .. import optools

class MPLFig_2Curves(Operation):

    def __init__(self):
        input_names = ['x_y_1', 'x_y_2']
        output_names = ['figure']
        super(MPLFig_2Curves, self).__init__(input_names, output_names)
        self.input_doc['x_y_1'] = 'n-by-2 array of y versus x for curve 1'
        self.input_doc['x_y_2'] = 'n-by-2 array of y versus x for curve 2'
        self.output_doc['figure'] = 'matplotlib.pyplot.Figure with the two curves plotted together'
        self.input_src['x_y_1'] = optools.wf_input
        self.input_src['x_y_2'] = optools.wf_input
        self.input_type['x_y_1'] = optools.ref_type
        self.input_type['x_y_2'] = optools.ref_type

    def run(self):
        fig = plt.figure()
        x_y_1 = self.inputs['x_y_1']
        x_y_2 = self.inputs['x_y_2']
        plt.plot(x_y_1[:,0],x_y_1[:,1],'g')
        plt.plot(x_y_2[:,0],x_y_2[:,1],'r')
        self.outputs['figure'] = fig



