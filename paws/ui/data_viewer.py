import numpy as np
from PySide import QtCore, QtGui
from matplotlib.figure import Figure
from pypif.obj import System

from ..core.operations.Operation import Operation 
from ..core.plugins.PawsPlugin import PawsPlugin
from ..core.plugins.WorkflowPlugin import WorkflowPlugin
from . import uitools
from .widgets.OpWidget import OpWidget
from .widgets.PifWidget import PifWidget
from .widgets.WorkflowGraphView import WorkflowGraphView
from .widgets.text_widgets import display_text, display_text_fast

if uitools.have_qt47:
    from . import plotmaker_pqg as plotmaker
else:
    from . import plotmaker_mpl as plotmaker

def display_item(itm,qlayout,logmethod=None):
    if logmethod: 
        logmethod('Log messages for data viewer not yet implemented')

    # Loop through the layout, last to first, clear the frame
    n_widgets = qlayout.count()
    for i in range(n_widgets-1,-1,-1):
        # QLayout.takeAt returns a LayoutItem
        widg = qlayout.takeAt(i)
        # get the QWidget of that LayoutItem and set it to deleteLater()
        widg.widget().deleteLater()

    pif_widget = None
    if isinstance(itm,System):
        pif_widget = PifWidget(itm)

    pgin_widget = None
    if isinstance(itm,PawsPlugin):
        if isinstance(itm,WorkflowPlugin):
            w = WorkflowGraphView(itm.wf)
            #textbox = QtGui.QTextEdit(scroll_area)
            #textbox.setText('selected plugin is a WorkflowPlugin.')
            pgin_widget = w 
        else:
            w = QtGui.QTextEdit()
            msg = str('selected plugin is a {}. '.format(type(itm).__name__)
                    + 'No display widgets exist for this plugin. '
                    + 'Add a display method to {} to view this plugin.'.format(__name__))
            w.setText(msg)
            pgin_widget = w 

    op_widget = None
    if isinstance(itm,Operation):
        op_widget = OpWidget(itm)

    plot_widget = None
    if isinstance(itm,np.ndarray):
        dims = np.shape(itm)
        if len(dims) == 2 and dims[0] > 2 and dims[1] > 2:
            plot_widget = plotmaker.array_plot_2d(itm)
        elif len(dims) == 1 or (len(dims) == 2 and (dims[0]==2 or dims[1]==2)):
            plot_widget = plotmaker.array_plot_1d(itm)
    elif isinstance(itm,Figure):
        plot_widget = plotmaker.plot_mpl_fig(itm)
    
    t = display_text_fast(itm)
    text_widget = QtGui.QTextEdit(t)

    # Assemble whatever widgets were produced, add them to the layout    
    if op_widget:
        qlayout.addWidget(op_widget,0,0,1,1) 
    elif pif_widget:
        qlayout.addWidget(pif_widget,0,0,1,1) 
    elif pgin_widget:
        qlayout.addWidget(pgin_widget,0,0,1,1) 
    elif plot_widget:
        qlayout.addWidget(plot_widget,0,0,1,1) 
    elif text_widget:
        # TODO: Anything else for displaying text, other than plopping it down in the center?
        qlayout.addWidget(text_widget,0,0,1,1) 
    else:
        msg = str('[{}]: selected item ({}) has no display method'.format(__name__,type(itm).__name__)
            + '<br><br>Printout of item: <br>{}'.format(itm))
        msg_widget = QtGui.QTextEdit(msg)
        qlayout.addWidget(msg_widget,0,0,1,1) 
        pass

