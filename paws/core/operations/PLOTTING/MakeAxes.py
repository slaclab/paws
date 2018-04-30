from collections import OrderedDict

from matplotlib import pyplot as plt
from ..Operation import Operation

inputs = OrderedDict(
    fignum=1,
    window_title='figure',
    axes_title='plot')
outputs = OrderedDict(axes=None)

class MakeAxes(Operation):
    """Creates matploblib pyplot axes for subsequent plotting operations"""

    def __init__(self):
        super(MakeAxes,self).__init__(inputs,outputs) 
        self.input_doc['fignum'] = 'figure number'
        self.input_doc['window_title'] = 'title for the window'
        self.input_doc['axes_title'] = 'title for the plot axes'
        self.output_doc['axes'] = 'matplotlib axes'
        
    def run(self):
        fignum = self.inputs['fignum']
        wt = self.inputs['window_title']
        axt = self.inputs['axes_title']
        fig = plt.figure(fignum)
        fig.canvas.set_window_title(wt)
        ax = fig.add_subplot(111)
        ax.set_title(axt)
        self.outputs['axes'] = ax 

