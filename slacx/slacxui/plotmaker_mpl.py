from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
#import matplotlib
#from matplotlib.backends import qt_compat

def array_plot_2d(data_in):
    return mpl_array_plot_2d(data_in)

def array_plot_1d(data_in):
    return mpl_array_plot_1d(data_in)

def mpl_array_plot_1d(data_in):
    fig = Figure(figsize=(100,100))
    axes = fig.add_subplot(111)
    axes.plot(data_in)
    return FigCanvas(fig)

def mpl_array_plot_2d(data_in):
    fig = Figure(figsize=(100,100))
    axes = fig.add_subplot(111)
    axes.contour(data_in)
    # FigCanvas is a subclass of QWidget
    return FigCanvas(fig)

def plot_mpl_fig(fig_in):
    return FigCanvas(fig_in)


