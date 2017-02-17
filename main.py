"""
This is the main module for paws.
"""

import os
import sys

from PySide import QtCore
# TODO: Only import QtGui and qdarkstyle if we are using a gui
from PySide import QtGui
import qdarkstyle

from paws.core.operations.op_manager import OpManager 
from paws.core.workflow.wf_manager import WfManager 
from paws.core.plugins.plugin_manager import PluginManager 
# TODO: Only import UiManager if we are using a gui
from paws.ui.ui_manager import UiManager

def main():
    """
    paws main method.
    """

    # TODO: parse sys.argv?
    
    # Instantiate QApplication, pass in cmd line args sys.argv.
    try:
        app = QtGui.QApplication(sys.argv)
    except RuntimeError:
        # An application already exists, probably. Get a reference to it.
        app = QtCore.QCoreApplication.instance()

    # load dark style on top of application stylesheet:
    app.setStyleSheet(qdarkstyle.load_stylesheet() + app.styleSheet())

    opman = OpManager()
    plugman = PluginManager()
    wfman = WfManager(app,plugman)
    uiman = UiManager(opman,wfman,plugman)
    plugman.logmethod = uiman.msg_board_log
    wfman.logmethod = uiman.msg_board_log
    opman.logmethod = uiman.msg_board_log

    # Make the paws title box
    uiman.make_title()    

    # Connect the menu actions to UiManager functions
    uiman.connect_actions()

    # Take care of remaining details
    uiman.final_setup()

    ### LAUNCH ###
    # show uiman.ui (a QMainWindow)
    uiman.ui.show()
    # app.exec_() returns an exit code when it is done
    ret = app.exec_()
    # save config files as needed
    opman.save_config()
    sys.exit(ret)
    
# Run the main() function if this module is invoked 
if __name__ == '__main__':
    main()

