"""
This is the main module for gui-driven execution of paws.
"""

import sys

import paws.api
import paws.ui
import paws.ui.UiManager

def main():
    """
    Main entry point for paws with a gui.
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
if __name__ == '__main__':
    main()

