import pyqtgraph as pg

def array_plot_2d(data_in):
    return pqg_array_plot_2d(data_in)

def array_plot_1d(data_in):
    return pqg_array_plot_1d(data_in)

def pqg_array_plot_2d(data_in):
    widg = pg.ImageView()
    widg.setImage(data_in)
    return widg 

def pqg_array_plot_1d(data_in):
    widg = pg.PlotWidget()
    widg.getPlotItem().plot(data_in)
    return widg 

def plot_mpl_fig(fig_in):
    return FigCanvas(fig_in)

