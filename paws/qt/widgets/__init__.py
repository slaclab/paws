from __future__ import print_function
import pkgutil
import os

import numpy as np
from PySide import QtCore, QtGui, QtUiTools
from matplotlib.figure import Figure

from ...core.operations.Operation import Operation
from ...core.workflows.Workflow import Workflow 
from ...core import plugins
from ...core.plugins.PawsPlugin import PawsPlugin
from .. import qttools
from .OpWidget import OpWidget
from .WorkflowGraphView import WorkflowGraphView
from .text_widgets import display_text, display_text_fast
from . import plugin_widgets

if qttools.have_qt47:
    from . import plotmaker_pqg as plotmaker
else:
    from . import plotmaker_mpl as plotmaker

def make_widget(itm):
    if isinstance(itm,Workflow):
        w = WorkflowGraphView(itm)
    elif isinstance(itm,PawsPlugin):
        plugin_type = type(itm).__name__
        # seek a Q widget definition for this plugin... 
        plugin_widget_name = 'Q'+plugin_type
        if plugin_widget_name in plugin_widgets.plugin_widget_list:
            pgw = plugin_widgets.get_widget(plugin_widget_name)
            pgw.connect_plugin(itm)
            w = pgw.widget
        else:
            pgw = plugin_widgets.default_plugin_widget(plugin_type)
    elif isinstance(itm,Operation):
        w = OpWidget(itm)
    elif isinstance(itm,np.ndarray):
        #if itm.dtype == np.int_ or itm.dtype == np.float_:
        dims = np.shape(itm)
        try:
            if len(dims) == 2 and dims[0] > 2 and dims[1] > 2:
                w = plotmaker.array_plot_2d(itm)
            elif len(dims) == 1 or (len(dims) == 2 and (dims[0]==2 or dims[1]==2)):
                w = plotmaker.array_plot_1d(itm)
        except:
            t = display_text_fast(itm)
            w = QtGui.QTextEdit(t)
        #else:
        #    t = display_text_fast(itm)
        #    w = QtGui.QTextEdit(t)
    elif isinstance(itm,Figure):
        w = plotmaker.plot_mpl_fig(itm)
    elif (isinstance(itm,float) 
    or isinstance(itm,int) 
    or isinstance(itm,dict) 
    or isinstance(itm,list) 
    or isinstance(itm,str)
    or isinstance(itm,unicode)):    
        t = display_text_fast(itm)
        w = QtGui.QTextEdit(t)
    elif type(itm).__name__ in ['System','ChemicalSystem']:
        # keeping this import out of the module dependencies for now
        from .PifWidget import PifWidget
        w = PifWidget(itm)
    else:
        msg = str('[{}]: selected item ({}) is not supported in {}'
            .format(__name__,type(itm).__name__,__name__)
            + '<br><br>Printout of item: <br>{}'.format(itm))
        w = QtGui.QTextEdit(msg)
    return w

