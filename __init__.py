import os
import sys

from xicam.plugins import base
from PySide import QtGui, QtCore, QtUiTools

from paws.ui import ui_manager
from paws.core.operations import op_manager
from paws.core.workflow import wf_manager

class PawsXicamPlugin(base.plugin):
    # The display name in the xi-cam plugin bar
    name = 'Workflow'

    def __init__(self, *args, **kwargs):

        # Get a reference to an Application
        try:
            app = QtGui.QApplication(sys.argv)
        except RuntimeError:
            app = QtCore.QCoreApplication.instance()

        # start core objects    
        opman = op_manager.OpManager()
        wfman = wf_manager.WfManager(app=app)
        # start ui objects
        uiman = ui_manager.UiManager(opman,wfman)
        wfman.logmethod = uiman.msg_board_log
        # Make the title box
        uiman.make_title()    
        # Connect the menu actions to UiManager functions
        uiman.connect_actions()
        # Take care of remaining details
        uiman.final_setup()

        # Set the widgets in base.plugin containers
        self.centerwidget = uiman.ui.center_frame
        self.leftwidget = uiman.ui.left_frame
        self.rightwidget = uiman.ui.right_frame
        self.bottomwidget = uiman.ui.message_board

        # There seems to be a problem with this plugin loading approach,
        # where the frames, *in some circumstances, not always*, 
        # mysteriously fail to bring their children with them.
        # Adding these calls to findChildren() 
        # seems to force the frames to find their children.
        # Curious. -LAP
        #import pdb
        #pdb.set_trace()
        uiman.ui.left_frame.findChildren(object)
        uiman.ui.right_frame.findChildren(object)
        uiman.ui.center_frame.findChildren(object)

        super(PawsXicamPlugin, self).__init__(*args, **kwargs)


