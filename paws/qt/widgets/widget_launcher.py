"""
This runs various widgets built on the paws.api.
"""

import sys

from .. import qtapi

from .. import ui_app
from ..UiManager import UiManager

def main():   
    """
    An entry point for paws full-featured interface.
    """
    # start QtGui.QApplication
    app = ui_app(sys.argv)
    # start paws objects 
    corepaw = qtapi.start(app)

    # start a ui manager
    ui_manager = UiManager(corepaw)

    ### LAUNCH ###
    ui_manager.ui.show()
    ret = app.exec_()
    sys.exit(ret)
    
