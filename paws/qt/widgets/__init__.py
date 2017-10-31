"""This package defines widgets that are used to communicate with paws."""

import numpy as np
from PySide import QtGui
from matplotlib.figure import Figure

from ...core.operations.Operation import Operation
from ...core.workflows.Workflow import Workflow 
from ...core.plugins.PawsPlugin import PawsPlugin
from .. import qttools
from .OpWidget import OpWidget
from .WorkflowGraphView import WorkflowGraphView
from .text_widgets import display_text, display_text_fast

if qttools.have_qt47:
    from . import plotmaker_pqg as plotmaker
else:
    from . import plotmaker_mpl as plotmaker

def make_widget(itm):
    if isinstance(itm,Workflow):
        w = WorkflowGraphView(itm)
    elif isinstance(itm,PawsPlugin):
        w = QtGui.QTextEdit()
        msg = str('selected plugin is a {}. '.format(type(itm).__name__)
                + 'There are no display methods associated with this plugin. '
                + 'Add a display method to {} to view this plugin.'.format(__name__))
        w.setText(msg)
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
        # TODO: consider what is the right level of support for
        # (and therefore dependency on) pypif
        from .PifWidget import PifWidget
        w = PifWidget(itm)
    else:
        msg = str('[{}]: selected item ({}) is not supported in {}'
            .format(__name__,type(itm).__name__,__name__)
            + '<br><br>Printout of item: <br>{}'.format(itm))
        w = QtGui.QTextEdit(msg)
    return w




