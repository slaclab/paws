"""
This runs various widgets built on the paws.api.
"""

import sys

import paws.api
import paws.ui
from paws.ui.widgets.PipelineWidget import PipelineWidget

def pipeline():
    """
    Entry point for paws pipeline interface.
    """
    # start QtGui.QApplication
    app = paws.ui.ui_app(sys.argv)
    # start paws objects 
    corepaw = paws.api.start()

    # start pipeline widget manager
    widg = PipelineWidget(corepaw)
    widg.ui.show()

    ### LAUNCH ###
    ret = app.exec_()
    corepaw.save_config()
    sys.exit(ret)

def main():   
    """
    An entry point for paws full-featured interface.
    """
    # start QtGui.QApplication
    app = paws.ui.ui_app(sys.argv)
    # start paws objects 
    corepaw = paws.api.start()

    # start a ui manager
    ui_manager = paws.ui.UiManager.UiManager(corepaw,app)

    ### LAUNCH ###
    ui_manager.ui.show()
    ret = app.exec_()
    # TODO: connect corepaw.save_config to app.aboutToQuit() signal,
    # in case app.exec_() does not have time to return,
    # which may happen in some situations on some platforms.
    corepaw.save_config()
    sys.exit(ret)
    
# Run the main() function if this module is invoked 
#if __name__ == '__main__':
#    # TODO: collect sys.argv to determine which widget to launch
#    main()

