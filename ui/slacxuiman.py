import sys
import os
from datetime import datetime as dt
import time

from PIL import Image, ImageQt
from PySide import QtGui, QtCore, QtUiTools
import numpy as np

from core import slacximg 
import core.operations as ops
from ui import plotmaker

class UiManager(object):
    """
    Stores a reference to a QMainWindow,
    performs operations on it
    """

    # TODO: when the QImageView widget gets resized,
    # it will call QWidget.resizeEvent().
    # Try to use this to resize the images in the QImageView.

    def __init__(self,ui_file):
        """Make a UI from ui_file, save a reference to it"""
        # Pick a UI definition, load it up
        ui_file.open(QtCore.QFile.ReadOnly)
        # load() produces a QMainWindow(QWidget).
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.imgman = None    
        self.opman = None    
        self.wfman = None
        self.op_ui = None
        self.op_input_widgets = {} 

    def export_image(self):
        """export the image in the currently selected tab"""
        pass

    def edit_image(self):
        """open an image editor for the current tab"""
        pass

    def close_image(self):
        """Remove selected items from the image tree"""
        # TODO: implement multiple selection in image tree? 
        # TODO: close any related image_viewer tabs and take out the garbage
        selected_indxs = self.ui.image_tree.selectedIndexes()
        for indx in selected_indxs:
            self.imgman.remove_image(indx)

    def open_image(self):
        """Open an image, add it to image tree"""
        # TODO: implement loading multiple images in one call? 
        # getOpenFileName(parent(Widget), caption, dir, extension(s) regexp)
        imgfile, ext = QtGui.QFileDialog.getOpenFileName(
        self.ui, 'Open file', os.getcwd(), self.imgman.loader_extensions())
        if imgfile:
            # get row where new image will be placed
            ins_row = self.imgman.rowCount(QtCore.QModelIndex())
            # create new SlacxImage object
            new_img = slacximg.SlacxImage(imgfile)
            # Render the image pixel data
            new_img.load_img_data()
            # Add this SlacxImage to ImgManager tree, self.imgman
            self.imgman.add_image(new_img)
            indx = self.imgman.index(ins_row,0,QtCore.QModelIndex())
            # Add data and tags
            self.imgman.add_image_data(new_img.img_data,indx,'img_data',new_img.size_tag())
            # set self.ui.image_tree selection to be the new image
            self.ui.image_tree.setCurrentIndex(
                self.imgman.index(ins_row,0,QtCore.QModelIndex()))

    def display_item(self):
        """
        Display selected item from the image tree 
        in a new tab in image_viewer
        """
        if len(self.ui.image_tree.selectedIndexes())>0:
            # get selected item from image_tree
            indx = self.ui.image_tree.selectedIndexes()[0]
            to_display = self.imgman.get_item(indx)
            # Don't proceed unless the item has something interesting to show.
            #if to_display.tag() == self.pix_data_tag():
            if True:
                # TODO: run this portion in its own thread. 
                # render a QWidget containing a surface plot
                plot_widget = plotmaker.pqg_arraycontour(to_display.data[0])
                # add a new tab to image_viewer labeled with parent.tag().
                tab_indx = self.ui.image_viewer.addTab(
                    plot_widget,to_display.parent.internalPointer().tag())
                self.ui.image_viewer.setCurrentIndex(tab_indx)
            else:
                # TODO: dialog box: tell user the selected item is uninteresting.
                pass
        else:
            # TODO: dialog box: tell user to select an item first
            pass

    def final_setup(self):
        # Let the message board be read-only
        self.ui.message_board.setReadOnly(True)
        # Let the message board ignore line wrapping
        self.ui.message_board.setLineWrapMode(self.ui.message_board.NoWrap)
        # Tell the status bar that we are ready.
        self.show_status('Ready')
        # Tell the message board that we are ready.
        self.msg_board_log('slacx is ready') 
        # Clear any default tabs out of image_viewer
        self.ui.image_viewer.clear()
        # Set image viewer tabs to be closeable
        self.ui.image_viewer.setTabsClosable(True)
        # Set the image viewer to be kinda fat
        self.ui.image_viewer.setMinimumWidth(600)
        # Leave the textual parts kinda skinny?
        #self.ui.left_panel.setMaximumWidth(400)
        #self.ui.right_panel.setMaximumWidth(300)

    def connect_actions(self):
        """Set up the works for buttons and menu items"""
        # Connect self.ui.actionOpen (File menu):
        self.ui.actionOpen.triggered.connect(self.open_image)
        # Connect self.ui.open_images_button: 
        self.ui.open_images_button.setText("&Open images...")
        self.ui.open_images_button.clicked.connect(self.open_image)
        # Connect self.ui.close_images_button: 
        self.ui.close_images_button.setText("&Close images")
        self.ui.close_images_button.clicked.connect(self.close_image)
        # Connect self.ui.display_item_button:
        self.ui.display_item_button.setText("&Display selected item")
        self.ui.display_item_button.clicked.connect(self.display_item)
        # Connect self.ui.image_viewer tabCloseRequested to local close_tab slot
        self.ui.image_viewer.tabCloseRequested.connect(self.close_tab)
        # Make self.ui.image_viewer tabs elide (arg is a Qt.TextElideMode)
        self.ui.image_viewer.setElideMode(QtCore.Qt.ElideRight)
        # Connect self.ui.add_operation_button:
        #self.ui.add_operation_button.setText("Add operation...")
        #self.ui.add_operation_button.clicked.connect(self.add_operation)
        # Connect self.ui.remove_operation_button:
        #self.ui.remove_operation_button.setText("Remove operation")
        #self.ui.remove_operation_button.clicked.connect(self.remove_operation)
        # Connect self.ui.add_op_button:
        self.ui.add_op_button.setText("Add Operation")
        self.ui.add_op_button.clicked.connect(self.add_op)
        # Connect self.ui.rm_op_button:
        self.ui.rm_op_button.setText("Remove Operation")
        self.ui.rm_op_button.clicked.connect(self.rm_op)
        # Connect self.ui.edit_op_button:
        self.ui.edit_op_button.setText("Edit Operation")
        self.ui.edit_op_button.clicked.connect(self.edit_op)
        # Connect self.ui.apply_workflow_button:
        self.ui.apply_workflow_button.setText("Apply Workflow")
        self.ui.apply_workflow_button.clicked.connect(self.apply_workflow)
        # Connect self.ui.export_image_button:
        #self.ui.export_image_button.setText("Export Image")
        #self.ui.export_image_button.clicked.connect(self.export_image)
        # Connect self.ui.edit_image_button:
        #self.ui.edit_image_button.setText("Edit Image")
        #self.ui.edit_image_button.clicked.connect(self.edit_image)
        # Connect self.ui.image_tree (QListView) 
        # to self.imgman (ImgManager(QAbstractListModel))
        self.ui.image_tree.setModel(self.imgman)
        # Connect self.ui.workflow_tree (QTreeView) 
        # to self.wfman (WfManager(TreeModel))
        self.ui.workflow_tree.setModel(self.wfman)

    def make_title(self):
        """Display the slacx logo in the title box"""
        # Load the slacx graphic  
        slacx_img_file = os.path.join(os.getcwd(), "ui/slacx_icon.png")
        # Make a QtGui.QPixmap from this file
        slacx_pixmap = QtGui.QPixmap(slacx_img_file)
        # Make a QtGui.QGraphicsPixmapItem from this QPixmap
        slacx_pixmap_item = QtGui.QGraphicsPixmapItem(slacx_pixmap)
        # Add this QtGui.QGraphicsPixmapItem to a QtGui.QGraphicsScene 
        slacx_scene = QtGui.QGraphicsScene()
        slacx_scene.addItem(slacx_pixmap_item)
        # Add the QGraphicsScene to the QGraphicsView
        self.ui.title_box.setScene(slacx_scene)
        # Set the main window title and icon
        self.ui.setWindowTitle("slacx")
        self.ui.setWindowIcon(slacx_pixmap)
 
    # A QtCore.Slot for closing tabs from image_viewer
    @QtCore.Slot(int)
    def close_tab(self,indx):
        self.ui.image_viewer.removeTab(indx)

    # Various simple utilities
    @staticmethod 
    def dtstr():
        """Return date and time as a string"""
        return dt.strftime(dt.now(),'%Y %m %d, %H:%M:%S')

    def msg_board_log(self,msg):
        """Print timestamped message with space to msg board"""
        self.ui.message_board.insertPlainText(
        self.dtstr() + '\n' + msg + '\n\n') 

    def show_status(self,msg):
        self.ui.statusbar.showMessage(msg)

    def edit_op(self):
        """
        edit the selected operation in the workflow list 
        """
        pass

    def rm_op(self):
        """
        remove the selected operation in the workflow list from the workflow
        """
        pass

    def add_op(self):
        """
        interact with user to build an operation into the workflow
        """
        # Load the op_builder popup
        self.op_ui = self.activate_op_ui()
        # Load initial op and args
        if self.opman.rowCount() > 0:
            self.create_op(opman.index(0,0))
        # Connect self.op_ui.op_selector to opman (QAbstractListModel).
        self.op_ui.op_selector.setModel(self.opman)
        # Connect op selection with a slot that populates op_ui.op_info and op_ui.arg_frame
        self.op_ui.op_selector.activated.connect(self.create_op)
        # Connect op_ui.finish_button with self.opman.load_op 
        self.op_ui.finish_button.clicked.connect(self.load_op)
        # Show the op_builder popup
        self.op_ui.show()

    def load_op(self):
        """
        Parse the fields in self.op_ui, 
        package Operation, ship to self.wfman
        """ 
        
        self.op_ui.close()

    def activate_op_ui(self):
        # TODO: make so op_ui closes if main ui is closed
        ui_file = QtCore.QFile(os.getcwd()+"/ui/op_builder.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        op_ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        #op_ui.setParent(self.ui)
        op_ui.setTitle("slacx operation builder")
        op_ui.load_op_button.setText("Finish / Load to Workflow")
        op_ui.arg_frame.setMinimumWidth(400)
        op_ui.op_frame.setMinimumWidth(300)
        return op_ui

    def clear_nameval_list(self):
        self.nameval_dict = {}
        # Count the items in the current layout
        n_val_widgets = self.op_ui.nameval_layout.count()
        # Loop through them, last to first, clear the frame
        for i in range(n_val_widgets-1,-1,-1):
            # QLayout.takeAt returns a LayoutItem
            widg = self.op_ui.nameval_layout.takeAt(i)
            # get the QWidget of that LayoutItem and set it to deleteLater()
            widg.widget().deleteLater()

    def build_nameval_list(self,op):
        # Count the items in the current layout
        n_val_widgets = self.op_ui.nameval_layout.count()
        # Loop through them, last to first, clear the frame
        for i in range(n_val_widgets-1,-1,-1):
            # QLayout.takeAt returns a LayoutItem- set its widget to deleteLater()
            item = self.op_ui.nameval_layout.takeAt(i)
            item.widget().deleteLater()
        i=0
        self.op_ui.nameval_layout.addWidget(self.text_widget('--- INPUTS ---'),i,0,1,4) 
        i+=1
        self.op_ui.nameval_layout.addWidget(self.hdr_widget('(name)'),i,0,1,1) 
        self.op_ui.nameval_layout.addWidget(self.hdr_widget('(source)'),i,2,1,1) 
        self.op_ui.nameval_layout.addWidget(self.hdr_widget('(value)'),i,3,1,1) 
        i+=1 
        for name, val in op.inputs.items():
            self.add_nameval_widget(name,val,i)
            i+=1 
        self.op_ui.nameval_layout.addWidget(self.smalltext_widget(' '),i,0,1,4) 
        i+=1 
        self.op_ui.nameval_layout.addWidget(self.text_widget('--- OUTPUTS ---'),i,0,1,4) 
        i+=1 
        self.op_ui.nameval_layout.addWidget(self.hdr_widget('(name)'),i,0,1,1) 
        self.op_ui.nameval_layout.addWidget(self.hdr_widget('(value)'),i,2,1,2) 
        i+=1 
        for name, val in op.outputs.items():
            self.add_nameval_widget(name,val,i,output=True)
            i+=1 

    def create_op(self,op_indx):
        # TODO: align / distribute the widgets nicerly. 
        # TODO: add scrolling for when shit gets out of hand. 
        op = self.opman.get_op(op_indx)()
        # Set self.op_ui.op_info to op.description
        self.op_ui.op_info.setPlainText(op.description())
        # Clear the view of name-value widgets
        self.clear_nameval_list()
        self.build_nameval_list(op)

    def text_widget(self,text):
        widg = QtGui.QLineEdit(text)
        widg.setReadOnly(True)
        widg.setAlignment(QtCore.Qt.AlignHCenter)
        return widg 
    def hdr_widget(self,text):
        widg = QtGui.QLineEdit(text)
        widg.setReadOnly(True)
        widg.setAlignment(QtCore.Qt.AlignHCenter)
        widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
        return widg 

    def smalltext_widget(self,text):
        widg = self.text_widget(text)
        widg.setMaximumWidth( 20 )
        widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
        return widg

    def add_nameval_widget(self,name,val,row,output=False):
        """a widget for name-value pairs"""
        #widg = QtGui.QWidget()
        name_widget = QtGui.QLineEdit(name)
        name_widget.setReadOnly(True)
        name_widget.setAlignment(QtCore.Qt.AlignRight)
        self.op_ui.nameval_layout.addWidget(name_widget,row,0)
        eq_widget = self.smalltext_widget('=')
        self.op_ui.nameval_layout.addWidget(eq_widget,row,1)
        val_widget = QtGui.QLineEdit('None')
        if output:
            val_widget.setReadOnly(True)
            self.op_ui.nameval_layout.addWidget(val_widget,row,2,1,2)
        else:
            src_widget = QtGui.QLineEdit('None')
            self.op_ui.nameval_layout.addWidget(src_widget,row,2,1,1)
            self.op_ui.nameval_layout.addWidget(val_widget,row,3,1,1)

    def apply_workflow(self):
        """
        run the workflow
        """
        pass

