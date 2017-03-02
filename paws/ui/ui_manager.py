import os
from functools import partial

from PySide import QtGui, QtCore, QtUiTools

from . import uitools
from .wfuiman import WfUiManager
from .opuiman import OpUiManager
from .pluguiman import PluginUiManager
from ..core.operations.operation import Operation
from ..core import pawstools
from . import data_viewer
from ..core.listmodel import ListModel

# TODO: Make a metaclass that generates Operation subclasses.
# TODO: Use the above to make an Op development interface. 

class UiManager(QtCore.QObject):
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
        ui_file = QtCore.QFile(pawstools.rootdir+"/ui/qtui/basic.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        # Set up the self.ui widget to delete itself when closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        opman.logmethod = self.msg_board_log
        wfman.logmethod = self.msg_board_log
        plugman.logmethod = self.msg_board_log
        # put up one default empty Workflow to start with
        #wfname = plugman.auto_tag('workflow')
        #wfman.add_wf(wfname)
        self.opman = opman 
        self.wfman = wfman 
        self.plugman = plugman
        self.make_title()
        self.connect_actions()
        self.final_setup()

    def new_wf(self): 
        wfname = self.plugman.auto_tag('workflow')
        self.ui.wf_selector.model().append_item(wfname)
        self.wfman.add_wf(wfname)
        self.ui.wf_selector.setCurrentIndex(self.wfman.n_wf()-1)

    def set_wf(self,wf_selector_idx):
        wfname = self.ui.wf_selector.model().list_data()[wf_selector_idx]
        self.ui.wf_tree.setModel(self.wfman.workflows[wfname])
        self.update_run_wf_button()

    def current_wf(self):
        idx = self.ui.wf_selector.currentIndex()
        wfname = self.ui.wf_selector.model().list_data()[idx]
        return self.wfman.workflows[wfname]

    def edit_wf(self,itm_idx=QtCore.QModelIndex()):
        """
        Interact with user to edit the workflow.
        Pass in QModelIndex to open the editor 
        with the item at that index loaded.
        """
        trmod = self.current_wf()
        if itm_idx.isValid():
            # valid index in workflow tree: percolate up to root ancestor
            while itm_idx.parent().isValid():
                itm_idx = itm_idx.parent()
        else:
            # invalid index: try to find something valid that is selected
            itm_idx = self.ui.wf_tree.currentIndex()
            if itm_idx.isValid():
                while itm_idx.parent().isValid():
                    itm_idx = itm_idx.parent()
            else:
                itm_idx = self.ui.op_tree.currentIndex()
                trmod = self.opman
        if itm_idx.isValid():
            uiman = self.start_wf_editor(trmod,itm_idx)
            if trmod in self.wfman.workflows.values():
                uiman.ui.wf_selector.setCurrentIndex(itm_idx)
            else:
                uiman.ui.op_selector.setCurrentIndex(itm_idx)
        else:
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
        uiman = WfUiManager(self.current_wf(),self.opman,self.plugman)
        if trmod and indx.isValid():
            uiman.get_op(trmod,indx)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        return uiman

    def display_plugin_item(self,idx):
        """
        Display selected item from the plugin tree in image_viewer 
        """
        if idx.isValid(): 
            itm_data = self.plugman.get_item(idx).data
            data_viewer.display_item(itm_data,self.ui.image_viewer,None)

    def display_wf_item(self,idx):
        """
        Display selected item from the workflow tree in image_viewer 
        """
        if idx.isValid(): 
            itm_data = self.current_wf().get_item(idx).data
            data_viewer.display_item(itm_data,self.ui.image_viewer,None)

    def final_setup(self):
        self.ui.message_board.setReadOnly(True)
        self.ui.message_board.insertPlainText('--- MESSAGE BOARD ---\n') 
        self.msg_board_log('paws is ready',timestamp=pawstools.dtstr) 
        self.ui.wf_tree.hideColumn(1)
        self.ui.wf_tree.hideColumn(2)
        self.ui.op_tree.hideColumn(1)
        self.ui.op_tree.hideColumn(2)
        self.ui.plugin_tree.hideColumn(1)
        self.ui.plugin_tree.hideColumn(2)
        self.ui.hsplitter.setStretchFactor(1,2)    
        self.ui.vsplitter.setStretchFactor(0,1)    

    def toggle_run_wf(self,wfname=None):
        if wfname:
            wf = self.wfman.workflows[wfname]
        else:
            current_wf_idx = self.ui.wf_selector.currentIndex()
            wfname = self.ui.wf_selector.model().list_data()[current_wf_idx]
            wf = self.current_wf()
        if wf.is_running():
            self.wfman.stop_wf(wfname)
        else:
            self.wfman.run_wf(wfname)
        self.update_run_wf_button()

    def update_run_wf_button(self):
        if self.current_wf().is_running():
            self.ui.run_wf_button.setText("S&top")
        else:
            self.ui.run_wf_button.setText("&Run")

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
        lm = ListModel(self.wfman.workflows.keys())
        self.ui.wf_selector.setModel(lm)
        self.ui.wf_selector.currentIndexChanged.connect( partial(self.set_wf) )
        self.ui.edit_ops_button.setText("Edit &operations")
        self.ui.edit_ops_button.clicked.connect(self.edit_ops)
        self.ui.add_wf_button.setText("&New...")
        self.ui.add_wf_button.clicked.connect(self.new_wf)
        self.ui.load_wf_button.setText("&Load")
        self.ui.load_wf_button.clicked.connect(self.start_load_ui)
        self.ui.edit_wf_button.setText("Edit &workflow")
        self.ui.edit_wf_button.clicked.connect( partial(self.edit_wf) )
        self.ui.run_wf_button.setText("&Run")
        self.ui.run_wf_button.clicked.connect(self.toggle_run_wf)
        self.wfman.wfdone.connect(self.toggle_run_wf)
        self.ui.save_wf_button.setText("&Save")
        self.ui.save_wf_button.clicked.connect(self.start_save_ui)
        self.ui.edit_plugins_button.setText("Edit &plugins")
        self.ui.edit_plugins_button.clicked.connect(self.start_plugins_ui)
        self.ui.plugin_tree.setModel(self.plugman)
        self.ui.wf_tree.setModel(self.current_wf())
        self.ui.op_tree.setModel(self.opman)
        self.ui.op_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.op_tree) ) 
        self.ui.wf_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.wf_tree) )
        self.ui.wf_tree.clicked.connect( self.display_wf_item )
        self.ui.plugin_tree.clicked.connect( self.display_plugin_item )
        self.ui.wf_tree.doubleClicked.connect( partial(self.edit_wf) )

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
        self.ui.message_board.verticalScrollBar().setValue(self.ui.message_board.verticalScrollBar().maximum())
      

