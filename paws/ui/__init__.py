from PySide import QtGui
import qdarkstyle

import paws.api

def ui_app(app_args=[]):
    """
    Return a reference to a new QApplication or a currently running QApplication.
    
    Input arguments are passed to the QApplication constructor.
    If any exception is thrown,
    the paws.api is called upon 
    to try to find a running QCoreApplication.
    """
    try:
        app = QtGui.QApplication(app_args)
        app.setStyleSheet(qdarkstyle.load_stylesheet() + app.styleSheet())
    except:
        app = paws.api.core_app(app_args)
    return app



