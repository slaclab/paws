from xicam.plugins import base
from .paws import api as pawsapi
from .paws import ui as pawsui
from .paws.ui import ui_manager as pawsuiman

class PawsXicamPlugin(base.plugin):
    # The display name in the xi-cam plugin bar
    name = 'Workflow'

    def __init__(self, *args, **kwargs):
        app = pawsui.ui_app()
        # start core objects
        xipaw = pawsapi.start()
        # start ui objects
        ui_manager = pawsui.ui_manager.UiManager(
        xipaw.op_manager(),xipaw.wf_manager(),xipaw.plugin_manager())

        # Set the widgets in base.plugin containers
        self.centerwidget = pawsuiman.ui.center_frame
        self.leftwidget = pawsuiman.ui.left_frame
        self.rightwidget = pawsuiman.ui.right_frame
        self.bottomwidget = pawsuiman.ui.message_board

        # There seems to be a problem with this plugin loading approach,
        # where the frames sometimes fail 
        # to bring their children with them.
        # Adding calls to findChildren() 
        # seems to force the frames
        # to include their children.
        # -LAP
        pawsuiman.ui.left_frame.findChildren(object)
        pawsuiman.ui.right_frame.findChildren(object)
        pawsuiman.ui.center_frame.findChildren(object)

        super(PawsXicamPlugin, self).__init__(*args, **kwargs)

