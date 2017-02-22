"""Module defining the API for paws"""

from PySide import QtCore

from paws.core.operations.op_manager import OpManager 
from paws.core.workflow.wf_manager import WfManager 
from paws.core.plugins.plugin_manager import PluginManager 

wf_manager = None
op_manager = None
plugin_manager = None

def core_app(app_args=[]):
    """
    Return a reference to a new QCoreApplication or a currently running QApplication.
    
    Input arguments are passed to the QApplication constructor.
    If a RuntimeError is thrown,
    it is assumed that a QApplication is already running,
    and an attempt is made to return a reference to that QApplication.
    If that fails, this returns None.

    :param app_args: arguments to pass to the QApplication constructor
    :type args: sequence
    :returns: reference to a new or existing QCoreApplication
    :return type: PySide.QtCore.QCoreApplication or None
    """
    try:
        app = QtCore.QCoreApplication(args)
    except RuntimeError:
        try:
            app = QtCore.QCoreApplication.instance()
        except:
            app = None
    return app

def start(app_args=[]):
    """
    Instantiate an Operation Manager, a Workflow Manager, and a Plugin Manager. Return references to them.

    paws.api.start() calls paws.api.core_app(),
    then sets up and returns references to 
    a paws Workflow Manager (paws.core.workflow.wf_manager.WfManager),
    Operation Manager (paws.core.operations.op_manager.OpManager),
    and Plugin Manager (paws.core.plugins.plugin_manager.PluginManager).

    :param app_args: arguments to pass to the QApplication constructor
    :type args: sequence
    :returns: references to paws operation manager, workflow manager, and plugin manager 
    :return type: tuple of paws.core.operations.op_manager.OpManager, paws.core.workflow.wf_manager.WfManager, paws.core.plugins.plugin_manager.PluginManager
    """
    app = core_app(app_args)
    op_manager = OpManager()
    plugin_manager = PluginManager()
    wf_manager = WfManager(app,plugin_manager)
    return op_manager, wf_manager, plugin_manager 

