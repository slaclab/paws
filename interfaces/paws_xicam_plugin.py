from xicam.plugins import base
import paws.api 
import paws.ui
import paws.ui.ui_manager

class PawsXicamPlugin(base.plugin):
    # The display name in the xi-cam plugin bar
    name = 'Workflow'

    def __init__(self, *args, **kwargs):
        app = paws.ui.ui_app()
        # start core objects
        paws.api.start()
        op_manager = paws.api.op_manager
        wf_manager = paws.api.wf_manager
        plugin_manager = paws.api.wf_manager
        # start ui objects
        ui_manager = paws.ui.ui_manager.UiManager(op_manager,wf_manager,plugin_manager)

        # Set the widgets in base.plugin containers
        self.centerwidget = ui_manager.ui.center_frame
        self.leftwidget = ui_manager.ui.left_frame
        self.rightwidget = ui_manager.ui.right_frame
        self.bottomwidget = ui_manager.ui.message_board

        # There seems to be a problem with this plugin loading approach,
        # where the frames, *in some circumstances, not always*, 
        # mysteriously fail to bring their children with them.
        # Adding these calls to findChildren() 
        # seems to force the frames to find their children.
        # Curious. -LAP
        #import pdb
        #pdb.set_trace()
        ui_manager.ui.left_frame.findChildren(object)
        ui_manager.ui.right_frame.findChildren(object)
        ui_manager.ui.center_frame.findChildren(object)

        super(PawsXicamPlugin, self).__init__(*args, **kwargs)


