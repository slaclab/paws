import os
import time
from functools import partial

from PySide import QtGui, QtCore, QtUiTools
import numpy as np

from . import uitools
from .opuiman import OpUiManager
from ..slacxcore.operations.slacxop import Operation
from ..slacxcore import slacxtools
from . import data_viewer

# TODO: Make add_op_button load an Operation into the opman, rather than instantiate an Operation into wfman.
# TODO: Add a button next to add_op_button for editing an op. 
# TODO: Load the properties of that op into an interface. 
# TODO: Make a metaclass that generates Operation subclasses.

class UiManager(object):
    """
    Stores a reference to a QMainWindow,
    performs operations on it
    """

    # TODO: when the QImageView widget gets resized,
    # it will call QWidget.resizeEvent().
    # Try to use this to resize the images in the QImageView.

    def __init__(self,opman,wfman):
        """Make a UI from ui_file, save a reference to it"""
        # Pick a UI definition, load it up
        ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/basic.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        # load() produces a QMainWindow(QWidget).
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        # Set up the self.ui widget to delete itself when closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.opman = opman 
        self.wfman = wfman 

    def load_from_file(self,wf_file):
        """
        Build things in to wfman from a wfl (YAML) file
        """
        self.wfman.load_from_file(wf_file)
       
    def save_to_file(self):
        """
        Serialize things from wfman into a wfl (YAML) file
        """
        self.wfman.save_to_file()

    def run_wf(self):
        """
        run the workflow
        """
        #self.msg_board_log('Executing current workflow')
        # Check for a batch executor...
        #self.msg_board_log('Determining execution method...')
        if self.wfman.find_batch_items():
            #self.msg_board_log('Start BATCH execution')
            self.wfman.run_wf_batch()
        else:
            #self.msg_board_log('Start SERIAL execution')
            self.wfman.run_wf_serial()

    def edit_wf(self,trmod,item_indx=QtCore.QModelIndex()):
        """
        interact with user to edit operations in the workflow
        """
        if item_indx.isValid():
            idx = item_indx
            if trmod == self.wfman:
                while idx.parent().isValid():
                    idx = idx.parent()
            x = trmod.get_item(idx).data
        else:
            x = None
            idx = self.ui.wf_tree.currentIndex()
            if idx.isValid():
                while idx.parent().isValid():
                    idx = idx.parent()
                x = self.wfman.get_item(idx).data
            else:
                idx = self.ui.op_tree.currentIndex()
                if idx.isValid():# and self.opman.get_item(idx).data is not None:
                    x = self.opman.get_item(idx).data
        existing_op_flag = isinstance(x,Operation)
        try:
            new_op_flag = issubclass(x,Operation)
        except:
            new_op_flag = False
        #print 'existing op: {}'.format(existing_op_flag)
        #print 'new op: {}'.format(new_op_flag)
        if new_op_flag: 
            #print 'new op'
            uiman = self.start_op_ui_manager(self.opman,idx)
            uiman.ui.op_selector.setCurrentIndex(idx)
            uiman.ui.show()
            return
        elif existing_op_flag: 
            #print 'existing op'
            uiman = self.start_op_ui_manager(self.wfman,idx)
            uiman.ui.wf_selector.setCurrentIndex(idx)
            uiman.ui.show()
            return
        else:
            # if we are here, there was either an invalid index selected,
            # or the selection did not point to a valid Operation
            uiman = self.start_op_ui_manager(None,QtCore.QModelIndex())
            uiman.ui.show()

    def edit_op(self,item_indx=None):
        """
        interact with user to edit and re-save an existing Operation 
        """
        print 'Operation editing is not yet implemented'

    def add_op(self,item_indx=None):
        """
        interact with user to enable an existing Operation 
        """
    #    if not item_indx:
    #        item_indx = self.ui.op_tree.currentIndex()
    #    if item_indx.isValid(): 
    #        if self.opman.get_item(item_indx).data is not None:
    #            x = self.opman.get_item(item_indx).data
    #            try:
    #                new_op_flag = issubclass(x,Operation)
    #            except:
    #                new_op_flag = False
    #            if new_op_flag:
    #                uiman = self.start_op_ui_manager(self.opman,item_indx)
    #                uiman.ui.op_selector.setCurrentIndex(item_indx)
    #                uiman.ui.show()
    #                return
    #    # if we are here, there was either an invalid index selected,
    #    # or the selection was not an Operation
    #    uiman = self.start_op_ui_manager(None,QtCore.QModelIndex())
    #    uiman.ui.show()
        print 'this function is now deprecated. use the Edit button in the right panel. '
        print 'soon this button will be repurposed to add Operations to the Operation tree.'    

    def start_op_ui_manager(self,trmod,indx):
        """
        Create a QFrame window from ui/op_builder.ui, then return it
        """
        uiman = OpUiManager(self.wfman,self.opman)
        if trmod and indx.isValid():
            uiman.get_op(trmod,indx)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        return uiman

    def display_item(self,indx):
        """
        Display selected item from the workflow tree in image_viewer 
        """
        if indx: 
            if self.wfman.get_item(indx).data is not None:
                to_display = self.wfman.get_item(indx).data
                uri = self.wfman.build_uri(indx)
                data_viewer.display_item(to_display,uri,self.ui.image_viewer,None)

    def final_setup(self):
        # Let the message board be read-only
        self.ui.message_board.setReadOnly(True)
        # Let the message board ignore line wrapping
        #self.ui.message_board.setLineWrapMode(self.ui.message_board.NoWrap)
        # Tell the status bar that we are ready.
        self.show_status('Ready')
        # Tell the message board that we are ready.
        self.ui.message_board.insertPlainText('--- MESSAGE BOARD ---\n') 
        self.msg_board_log('slacx is ready',timestamp=slacxtools.dtstr) 
        # Clear any default tabs out of image_viewer
        #self.ui.center_frame.setMinimumWidth(200)
        self.ui.op_tree.resizeColumnToContents(0)
        self.ui.wf_tree.resizeColumnToContents(0)
        self.ui.wf_tree.resizeColumnToContents(1)
        self.ui.splitter.setStretchFactor(1,2)    

    def connect_actions(self):
        """Set up the works for buttons and menu items"""
        # TODO: Figure out how to get the display to follow
        # when I scroll through the tree with my arrow keys.
        #self.ui.wf_tree.activated.connect(self.display_item)
        self.ui.wf_tree.clicked.connect(self.display_item)
        self.ui.add_op_button.setText("&Add Operation")
        self.ui.add_op_button.clicked.connect(self.add_op)
        self.ui.edit_op_button.setText("Edit Operation")
        self.ui.edit_op_button.clicked.connect(self.edit_op)
        self.ui.load_wf_button.setText("&Load")
        self.ui.load_wf_button.clicked.connect( partial(self.load_from_file,slacxtools.rootdir+'/test.wfl') )
        #self.ui.load_wf_button.clicked.connect( self.load_from_file )
        self.ui.edit_wf_button.setText("&Edit")
        self.ui.edit_wf_button.clicked.connect( partial(self.edit_wf,self.wfman) )
        self.ui.run_wf_button.setText("&Run")
        self.ui.run_wf_button.clicked.connect(self.run_wf)
        self.ui.save_wf_button.setText("&Save")
        self.ui.save_wf_button.clicked.connect(self.save_to_file)
        # Connect self.ui.wf_tree (QTreeView) to self.wfman (WfManager(TreeModel))
        self.ui.wf_tree.setModel(self.wfman)
        #self.ui.wf_tree.hideColumn(1)
        # Connect self.ui.op_tree (QTreeView) to self.opman (OpManager(TreeModel))
        self.ui.op_tree.setModel(self.opman)
        self.ui.op_tree.hideColumn(1)
        self.ui.op_tree.doubleClicked.connect( partial(self.edit_wf,self.opman) )
        self.ui.wf_tree.doubleClicked.connect( partial(self.edit_wf,self.wfman) )

    def make_title(self):
        """Display the slacx logo in the image viewer"""
        # Load the slacx graphic  
        slacx_img_file = os.path.join(slacxtools.rootdir, "slacxui/slacx_icon_white.png")
        # Make a QtGui.QPixmap from this file
        slacx_pixmap = QtGui.QPixmap(slacx_img_file)
        # Make a QtGui.QGraphicsPixmapItem from this QPixmap
        slacx_pixmap_item = QtGui.QGraphicsPixmapItem(slacx_pixmap)
        # Add this QtGui.QGraphicsPixmapItem to a QtGui.QGraphicsScene 
        slacx_scene = QtGui.QGraphicsScene()
        slacx_scene.addItem(slacx_pixmap_item)
        qwhite = QtGui.QColor(255,255,255,255)
        textitem = slacx_scene.addText("v{}".format(slacxtools.version))
        textitem.setPos(100,35)
        textitem.setDefaultTextColor(qwhite)
        # Add the QGraphicsScene to self.ui.image_viewer layout 
        logo_view = QtGui.QGraphicsView()
        logo_view.setScene(slacx_scene)
        #logo_view.setStyleSheet( "QTextEdit { color: white  }" + self.ui.styleSheet() )
        #logo_view.setStyleSheet( "QGraphicsTextItem { color: white  }" + self.ui.styleSheet() )
        #logo_view.setStyleSheet( "QGraphicsView { color: white  }" + self.ui.styleSheet() )
        #textitem.setStyleSheet( "QGraphicsTextItem { color: white  }" + self.ui.styleSheet() )
        self.ui.image_viewer.addWidget(logo_view,0,0,1,1)
        #self.ui.title_box.setScene(slacx_scene)
        # Set the main window title and icon
        self.ui.setWindowTitle("slacx v{}".format(slacxtools.version))
        self.ui.setWindowIcon(slacx_pixmap)


    def msg_board_log(self,msg,timestamp=slacxtools.timestr):
        """Print timestamped message to msg board"""
        self.ui.message_board.insertPlainText(
        '- ' + timestamp() + ': ' + msg + '\n') 
        self.ui.message_board.verticalScrollBar().setValue(self.ui.message_board.verticalScrollBar().maximum())
      
    def show_status(self,msg):
        self.ui.statusbar.showMessage(msg)

    #def export_image(self):
    #    """export the image in the currently selected tab"""
    #    pass

    #def edit_image(self):
    #    """open an image editor for the current tab"""
    #    pass

    # A QtCore.Slot for closing tabs from image_viewer
    #@QtCore.Slot(int)
    #def close_tab(self,indx):
    #    self.ui.image_viewer.removeTab(indx)

