import PySide   # importing this locally configures pyqtgraph to use PySide
from matplotlib.backends import qt_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas 
from matplotlib.figure import Figure
import pyqtgraph as pg

def mpl_arraycontour(data_in):
    fig = Figure(figsize=(100,100))
    axes = fig.add_subplot(111)
    axes.contour(data_in)
    # FigCanvas is a subclass of QWidget
    return FigCanvas(fig)

def pqg_arraycontour(data_in):
    # ImageView is subclass of QWidget
    # ImageView __init__(parent, name, view, imageItem, *args)
    imv = pg.ImageView()
    imv.setImage(data_in)
    return imv

