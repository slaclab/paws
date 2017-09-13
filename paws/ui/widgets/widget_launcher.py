"""
This runs various widgets built on the paws.api.
"""

import sys

from paws.qt import qtapi
import paws.ui
from paws.ui.UiManager import UiManager

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
    
# TODO: entry points for alternative/simplified interfaces, e.g.:
# def specialwidget():
#
#    Load an app and start a paw
#
#    Set up a UI for this special case
#
#    Launch 




