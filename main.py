"""
This is the main module for gui-driven execution of paws.
"""

import sys

import paws.api
import paws.ui
import paws.ui.ui_manager

def main():
    """
    Main entry point for paws with a gui.
    """
    # start QtGui.QApplication
    app = paws.ui.ui_app(sys.argv)
    # start core objects
    op_manager, wf_manager, plugin_manager = paws.api.start()

    # start ui manager
    ui_manager = paws.ui.ui_manager.UiManager(op_manager,wf_manager,plugin_manager)

    ### LAUNCH ###
    # show ui_manager.ui (a QMainWindow)
    ui_manager.ui.show()
    # app.exec_() begins the event loop,
    # returns an exit code when it is done
    ret = app.exec_()
    # save config files as needed
    op_manager.save_config()
    sys.exit(ret)
    
# Run the main() function if this module is invoked 
if __name__ == '__main__':
    main()

