import os
import time
from functools import partial

from PySide import QtGui, QtCore, QtUiTools

from . import uitools
from .wfuiman import WfUiManager
from .opuiman import OpUiManager
from .pluguiman import PluginUiManager
from ..core.operations.operation import Operation
from ..core import pawstools
from . import data_viewer

# TODO: Make a metaclass that generates Operation subclasses.
# TODO: Use the above to make an Op development interface. 
# TODO: Consider whether this should inherit from QtCore.QObject instaed of object?

class UiManager(object):
    """
    Stores a reference to a QMainWindow,
    performs operations on it
    """

    # TODO: when the QImageView widget gets resized,
    # it will call QWidget.resizeEvent().
    # Try to use this to resize the images in the QImageView.

    def __init__(self,opman,wfman,plugman):
        """Make a UI from ui_file, save a reference to it"""
        super(UiManager,self).__init__()
        # Pick a UI definition, load it up
        ui_file = QtCore.QFile(pawstools.rootdir+"/ui/qtui/basic.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        # load() produces a QMainWindow(QWidget).
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        # Set up the self.ui widget to delete itself when closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.opman = opman 
        self.wfman = wfman 
        self.plugman = plugman

    def edit_wf(self,trmod,itm_idx=QtCore.QModelIndex()):
        """
        Interact with user to edit the workflow.
        Pass in a TreeModel and index to open the editor 
        with the item at that index loaded.
        """
        if itm_idx.isValid():
            if trmod == self.wfman:
                while itm_idx.parent().isValid():
                    itm_idx = itm_idx.parent()
            x = trmod.get_item(itm_idx).data
        else:
            x = None
            itm_idx = self.ui.wf_tree.currentIndex()
            if itm_idx.isValid():
                while itm_idx.parent().isValid():
                    itm_idx = itm_idx.parent()
                x = self.wfman.get_item(itm_idx).data
            else:
                itm_idx = self.ui.op_tree.currentIndex()
                if itm_idx.isValid():# and self.opman.get_item(idx).data is not None:
                    x = self.opman.get_item(itm_idx).data
        existing_op_flag = isinstance(x,Operation)
        try:
            new_op_flag = issubclass(x,Operation)
        except:
            new_op_flag = False
        if new_op_flag: 
            uiman = self.start_wf_editor(self.opman,itm_idx)
            uiman.ui.op_selector.setCurrentIndex(itm_idx)
            uiman.ui.show()
            return
        elif existing_op_flag: 
            uiman = self.start_wf_editor(self.wfman,itm_idx)
            uiman.ui.wf_selector.setCurrentIndex(itm_idx)
            uiman.ui.show()
            return
        else:
            # if we are here, there was either an invalid index selected,
            # or the selection did not point to a valid Operation
            uiman = self.start_wf_editor()
            uiman.ui.show()

    def edit_ops(self,item_indx=None):
        """
        interact with user to enable existing Operations
        and edit or develop new Operations 
        """
        uiman = OpUiManager(self.opman)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        uiman.ui.show()

    def start_wf_editor(self,trmod=None,indx=QtCore.QModelIndex()):
        """
        Create a WfUiManager (QMainWindow), return it 
        """
        uiman = WfUiManager(self.wfman,self.opman,self.plugman)
        if trmod and indx.isValid():
            uiman.get_op(trmod,indx)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        return uiman

    def display_item(self,idx):
        """
        Display selected item from the workflow tree in image_viewer 
        """
        if idx.isValid(): 
            itm_data = self.wfman.get_item(idx).data
            uri = self.wfman.build_uri(idx)
            data_viewer.display_item(itm_data,uri,self.ui.image_viewer,None)

    def final_setup(self):
        self.ui.message_board.setReadOnly(True)
        self.ui.message_board.insertPlainText('--- MESSAGE BOARD ---\n') 
        self.msg_board_log('paws is ready',timestamp=pawstools.dtstr) 
        self.ui.wf_tree.hideColumn(1)
        self.ui.op_tree.hideColumn(1)
        self.ui.plugin_tree.hideColumn(1)
        self.ui.hsplitter.setStretchFactor(1,2)    
        self.ui.vsplitter.setStretchFactor(0,1)    

    def toggle_run_wf(self):
        if self.wfman.is_running():
            self.wfman.stop_wf()
            self.ui.run_wf_button.setText("&Run")
        else:
            self.ui.run_wf_button.setText("S&top")
            self.wfman.run_wf()

    def start_load_ui(self):
        uitools.start_load_ui(self)

    def start_save_ui(self):
        uitools.start_save_ui(self)

    def start_plugins_ui(self):
        uiman = PluginUiManager(self.plugman)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        uiman.ui.show()

    def connect_actions(self):
        """Set up the works for buttons and menu items"""
        #self.ui.add_op_button.setText("Add to Workflow")
        #self.ui.add_op_button.clicked.connect( partial(self.edit_wf,self.opman) )
        self.ui.edit_ops_button.setText("Edit &operations")
        self.ui.edit_ops_button.clicked.connect(self.edit_ops)
        self.ui.load_wf_button.setText("&Load")
        self.ui.load_wf_button.clicked.connect(self.start_load_ui)
        self.ui.edit_wf_button.setText("Edit &workflow")
        self.ui.edit_wf_button.clicked.connect( partial(self.edit_wf,self.wfman) )
        self.ui.run_wf_button.setText("&Run")
        self.ui.run_wf_button.clicked.connect(self.toggle_run_wf)
        self.ui.save_wf_button.setText("&Save")
        self.ui.save_wf_button.clicked.connect(self.start_save_ui)
        self.ui.edit_plugins_button.setText("Edit &plugins")
        self.ui.edit_plugins_button.clicked.connect(self.start_plugins_ui)
        self.ui.plugin_tree.setModel(self.plugman)
        self.ui.wf_tree.setModel(self.wfman)
        self.ui.op_tree.setModel(self.opman)
        self.ui.op_tree.hideColumn(1)
        self.wfman.wfdone.connect(self.toggle_run_wf)
        self.ui.op_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.op_tree) ) 
        self.ui.wf_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.wf_tree) )
        self.ui.wf_tree.clicked.connect( self.display_item )
        self.ui.op_tree.doubleClicked.connect( partial(self.edit_wf,self.opman) )
        self.ui.wf_tree.doubleClicked.connect( partial(self.edit_wf,self.wfman) )
        # TODO: Figure out how to get the display to follow
        # when I scroll through the tree with my arrow keys.
        #self.ui.wf_tree.activated.connect(self.display_item)
        #self.ui.wf_tree.selectionModel().selectionChanged.connect( self.ui.wf_tree.selectionChanged )

    def make_title(self):
        """Display the paws logo in the image viewer"""
        # Load the graphic  
        img_file = os.path.join(pawstools.rootdir, "ui/graphics/paws_icon_white.png")
        # Make a QtGui.QPixmap from this file
        pixmap = QtGui.QPixmap(img_file)
        # Make a QtGui.QGraphicsPixmapItem from this QPixmap
        pixmap_item = QtGui.QGraphicsPixmapItem(pixmap)
        # Add this QtGui.QGraphicsPixmapItem to a QtGui.QGraphicsScene 
        scene = QtGui.QGraphicsScene()
        scene.addItem(pixmap_item)
        qwhite = QtGui.QColor(255,255,255,255)
        textitem = scene.addText("v{}".format(pawstools.version))
        textitem.setPos(100,35)
        textitem.setDefaultTextColor(qwhite)
        # Add the QGraphicsScene to self.ui.image_viewer layout 
        logo_view = QtGui.QGraphicsView()
        logo_view.setScene(scene)
        self.ui.image_viewer.addWidget(logo_view,0,0,1,1)
        self.ui.setWindowTitle("paws v{}".format(pawstools.version))
        self.ui.setWindowIcon(pixmap)

    def msg_board_log(self,msg,timestamp=pawstools.timestr):
        """Print timestamped message to msg board"""
        self.ui.message_board.insertPlainText(
        '- ' + timestamp() + ': ' + msg + '\n') 
        # TODO: Figure out how to get the message board to stay put if the scrollbar is under user control
        #if not self.ui.message_board.isActive():
        self.ui.message_board.verticalScrollBar().setValue(self.ui.message_board.verticalScrollBar().maximum())
      

