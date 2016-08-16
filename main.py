import os
import sys

from PySide import QtGui, QtCore

from ui import slacxui

"""
slacx main module.
"""


def main():
    """
    slacx main execution method.
    """

    # Instantiate QApplication, pass in cmd line args sys.argv.
    # TODO: If file list provided in sys.argv, load these files.
    # TODO: Add functionality to do batch mode without a gui.
    app = QtGui.QApplication(sys.argv)

    # Start a UiManager to create and manage a QMainWindow 
    ui_file = QtCore.QFile(os.getcwd()+"/ui/basic.ui")
    uiman = slacxui.UiManager(ui_file)

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
#For windows execution:
#if sys.platform == 'win32':
#    sys.stdout = open(os.path.join(os.path.expanduser('~'),'out.log'),'w')
#    sys.stderr = open(os.path.join(os.path.expanduser('~'),'err.log'),'w')
#
#For making printouts of obj structure:
#import pprint
#pprint.PrettyPrinter().pprint(uiman.ui.__dict__)


