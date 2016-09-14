import sys
import os
from datetime import datetime as dt
import time
from functools import partial

from PySide import QtGui, QtCore, QtUiTools
import numpy as np

from core import slacximg 
from ui import plotmaker
from ui.opuiman import OpUiManager

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
        # Set up the self.ui widget to delete itself when closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.imgman = None    
        self.opman = None    
        self.wfman = None
        #self.op_uimans = [] 

    def apply_workflow(self):
        """
        run the workflow
        """
        pass

    def edit_op(self):
        """
        Edit the selected operation in the workflow list.
        Do this by opening an OpUiManager,
        loading it with the selected operation,
        and then setting the finish/load button
        to perform an update rather than appendage.
        """
        uiman = self.open_op_ui_manager()
        # set OpUiManager's operation to the one selected in self.ui.workflow_tree
        selected_indxs = self.ui.workflow_tree.selectedIndexes()
        uiman.set_op( self.wfman.get_item(selected_indxs[0]).data[0] )
        # connect uiman.ui.finish_button to an operation updater method
        uiman.ui.finish_button.clicked.disconnect()
        uiman.ui.finish_button.clicked.connect( partial(uiman.update_op,selected_indxs[0]) )
        uiman.ui.show()

    def rm_op(self):
        """
        remove the selected operation in the workflow list from the workflow
        """
        # TODO: implement multiple selection 
        # TODO: take out the garbage
        selected_indxs = self.ui.workflow_tree.selectedIndexes()
        #for indx in selected_indxs:
        self.wfman.remove_op(selected_indxs[0])

    def add_op(self):
        """
        interact with user to build an operation into the workflow
        """
        uiman = self.open_op_ui_manager()
        uiman.ui.show()

    def open_op_ui_manager(self):
        """
        Create a QFrame window from ui/op_builder.ui, then return it
        """
        ui_file = QtCore.QFile(os.getcwd()+"/ui/op_builder.ui")
        uiman = OpUiManager(ui_file)
        uiman.imgman = self.imgman
        uiman.wfman = self.wfman
        uiman.set_op_manager(self.opman)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        return uiman

    def close_image(self):
        """Remove selected items from the image tree"""
        # TODO: implement multiple selection  
        # TODO: take out the garbage
        selected_indxs = self.ui.image_tree.selectedIndexes()
        #for indx in selected_indxs:
        self.imgman.remove_image(selected_indxs[0])

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
            # Add this SlacxImage to ImgManager tree, self.imgman
            self.imgman.add_image(new_img)
            indx = self.imgman.index(ins_row,0,QtCore.QModelIndex())
            # Render the image pixel data
            new_img.load_img_data()
            # Add data and tags
            self.imgman.add_image_data(indx,new_img.img_data,'img_data',new_img.size_tag())
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
        self.ui.workflow_tree.setMinimumWidth(350)
        self.ui.workflow_tree.resizeColumnToContents(0)
        self.ui.workflow_tree.resizeColumnToContents(1)
        self.ui.image_tree.setMinimumWidth(350)
        self.ui.image_tree.resizeColumnToContents(0)
        self.ui.image_tree.resizeColumnToContents(1)
        #self.ui.workflow_tree.setColumnWidth(0,200)
        #self.ui.workflow_tree.setColumnWidth(1,150)
        self.ui.image_tree.setColumnWidth(0,180)

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

    def export_image(self):
        """export the image in the currently selected tab"""
        pass

    def edit_image(self):
        """open an image editor for the current tab"""
        pass


