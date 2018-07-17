from collections import OrderedDict

from matplotlib import pyplot as plt
from ..Operation import Operation

inputs = OrderedDict(
    x_y_data=None,
    logx=False,
    logy=False,
    fignum=1)
outputs = OrderedDict()

class MakePlot(Operation):
    """Make a matplotlib figure, plot some (x,y) data on it, show the figure"""

    def __init__(self):
        super(MakePlot,self).__init__(inputs,outputs) 
        self.input_doc['x_y_data'] = 'n-by-2 array of x and y values'
        self.input_doc['logx'] = 'logarithmic x-axis if True'
        self.input_doc['logy'] = 'logarithmic y-axis if True'
        self.input_doc['fignum'] = 'integer figure number'
        
    def run(self):
        xy = self.inputs['x_y_data']
        lx = self.inputs['logx']
        ly = self.inputs['logy']
        fn = self.inputs['fignum']
        fig = plt.figure(fn)
        ax = fig.add_subplot(111)
        if xy is not None: 
            if lx and ly:
                ax.loglog(xy[:,0],xy[:,1])
            elif ly:
                ax.semilogy(xy[:,0],xy[:,1])
            elif lx:
                ax.semilogx(xy[:,0],xy[:,1])
            else:
                ax.plot(xy[:,0],xy[:,1])
            plt.show() 
