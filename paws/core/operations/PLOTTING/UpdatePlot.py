from collections import OrderedDict

from matplotlib import pyplot as plt
from ..Operation import Operation

inputs = OrderedDict(
    axes=None,
    x_y_data=None,
    logx=False,
    logy=False,
    clear=True)
outputs = OrderedDict()

class UpdatePlot(Operation):
    """Update existing axes with new data"""

    def __init__(self):
        super(UpdatePlot,self).__init__(inputs,outputs) 
        self.input_doc['axes'] = 'Existing matplotlib axes'
        self.input_doc['x_y_data'] = 'n-by-2 array of x and y values'
        self.input_doc['clear'] = 'boolean flag, clear plot if True'
        
    def run(self):
        clr = self.inputs['clear']
        ax = self.inputs['axes']
        xy = self.inputs['x_y_data']
        lx = self.inputs['logx']
        ly = self.inputs['logy']
        if clr: 
            for artist in ax.lines + ax.collections:
                artist.remove()
            #ax.clear()
        if lx and ly:
            ax.loglog(xy[:,0],xy[:,1])
        elif ly:
            ax.semilogy(xy[:,0],xy[:,1])
        elif lx:
            ax.semilogx(xy[:,0],xy[:,1])
        plt.ion()
        plt.show()
        plt.pause(0.001)



