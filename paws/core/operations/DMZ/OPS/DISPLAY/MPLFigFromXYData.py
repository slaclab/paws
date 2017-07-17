from matplotlib import pyplot as plt

from ..Operation import Operation
from .. import optools

class MPLFigFromXYData(Operation):

    def __init__(self):
        input_names = ['x', 'y']
        output_names = ['figure']
        super(MPLFigFromXYData, self).__init__(input_names, output_names)
        self.input_doc['x'] = '1d array; independent variable'
        self.input_doc['y'] = '1d array; dependent variable'
        self.output_doc['figure'] = 'matplotlib.pyplot.Figure with a plot of y vs x'
        self.input_src['x'] = optools.wf_input
        self.input_src['y'] = optools.wf_input
        self.categories = ['DISPLAY']

    def run(self):
        fig = plt.figure()
        plt.plot(self.inputs['x'],self.inputs['y'])
        self.outputs['figure'] = fig



