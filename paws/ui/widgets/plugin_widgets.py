from PySide import QtGui

from ...core.plugins.plugin import PawsPlugin
from ...core.workflow.wf_plugin import WorkflowPlugin 

def plugin_widget(pgin):
    """
    Produce a widget that interacts with the contents of a plugin.
    """
    w = None
    if isinstance(pgin,WorkflowPlugin):
        w = QtGui.QTextEdit()
        msg = 'selected plugin is a WorkflowPlugin. Producing this text widget.'
        w.setText(msg)
    else:
        w = QtGui.QTextEdit()
        msg = str('selected plugin is a {}. '.format(type(pgin).__name__)
                + 'No display widgets exist for this plugin. '
                + 'Add a display method to {} to view this plugin.'.format(__name__))
        w.setText(msg)
         
    return w

