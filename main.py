import os
import sys

from PySide import QtGui, QtCore
import qdarkstyle

from ui import slacxuiman
from core import slacximgman
from core.operations import slacxopman

"""
slacx main module.
"""


def main():
    """
    slacx main execution method.
    """

    # Instantiate QApplication, pass in cmd line args sys.argv.
    app = QtGui.QApplication(sys.argv)

    # TODO: parse sys.argv for:
    #   running without a gui 
    #   image files to load  
    #   Operations to load 
    #   loading a workflow
    #   batch mode
    #   real-time mode

    # If running with gui, load dark style:
    style = app.styleSheet()
    app.setStyleSheet(qdarkstyle.load_stylesheet() + style)

    # Start an ImgManager to manage input files.
    # TODO: give kwargs to these init routines to rebuild saved jobs
    imgman = slacximgman.ImgManager()
    # Start an OpManager to manage operations.
    opman = slacxopman.OpManager()

    # Start a UiManager to create and manage a QMainWindow.
    # Takes ui file name as only argument.
    ui_file = QtCore.QFile(os.getcwd()+"/ui/basic.ui")
    uiman = slacxuiman.UiManager(ui_file)
    # UiManager needs to store references to the QAbstractItemModel objects
    # that are used to interact with the features of the gui
    # TODO: make this part of the UiManager constructor.
    uiman.imgman = imgman
    uiman.opman = opman

    # Make the slacx title box
    uiman.make_title()    

    # Connect the menu actions to UiManager functions
    uiman.connect_actions()

    # Take care of remaining details
    uiman.final_setup()

    ### LAUNCH ###
    # Show uiman.ui (a QMainWindow)
    uiman.ui.show()
    # sys.exit gracefully after app.exec_() returns its exit code
    sys.exit(app.exec_())

    
# Run the main() function if this module is the top level.
if __name__ == '__main__':
    main()


### ARCHIVES ###
#For win32 execution:
#if sys.platform == 'win32':
#    sys.stdout = open(os.path.join(os.path.expanduser('~'),'out.log'),'w')
#    sys.stderr = open(os.path.join(os.path.expanduser('~'),'err.log'),'w')
#
#For making printouts of obj structure:
#import pprint
#pprint.PrettyPrinter().pprint(uiman.ui.__dict__)


