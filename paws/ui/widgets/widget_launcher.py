"""
This runs various widgets built on the paws.api.
"""

import sys

from paws.qt import qtapi
import paws.ui
from paws.ui.UiManager import UiManager
from paws.ui.widgets.PipelineWidget import PipelineWidget

def main():   
    """
    An entry point for paws full-featured interface.
    """
    # start QtGui.QApplication
    app = paws.ui.ui_app(sys.argv)
    # start paws objects 
    corepaw = qtapi.start(app)

    # start a ui manager
    ui_manager = UiManager(corepaw)

    ### LAUNCH ###
    ui_manager.ui.show()
    ret = app.exec_()
    # TODO: connect corepaw.save_config to app.aboutToQuit() signal,
    # in case app.exec_() does not have time to return,
    # which may happen in some situations on some platforms.
    corepaw.save_config()
    sys.exit(ret)
    
def pipeline():
    """
    Entry point for paws pipeline interface.
    """
    # start QtGui.QApplication
    app = paws.ui.ui_app(sys.argv)
    # start paws objects 
    corepaw = qtapi.start(app)

    # start pipeline widget manager
    widg = PipelineWidget(corepaw)
    widg.ui.show()

    ### LAUNCH ###
    ret = app.exec_()
    corepaw.save_config()
    sys.exit(ret)

