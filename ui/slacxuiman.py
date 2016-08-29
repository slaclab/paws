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

    def rm_op_from_workflow(self):
        """
        remove the selected operation in the workflow list from the workflow
        """
        pass

    def add_op_to_workflow(self):
        """
        add the selected operation in the operation list to the workflow
        """
        pass

    def apply_workflow(self):
        """
        run the workflow
        """
        pass

    def create_operation(self):
        """add a new operation to the operation list"""
        new_op = self.build_operation()
        self.opman.add_op(new_op)

    def build_operation(self):
        """
        Interact with the user to select and provide parameters 
        for a new operation.
        """
        # TODO: interact with the user to build the right operation
        # FORNOW: always give the identity operation on a null image.
        return ops.identity.Identity({'img':None})

    def remove_operation(self):
        """remove an existing operation from the operation list"""
        selected_indxs = self.ui.operation_list.selectedIndexes()
        for indx in selected_indxs:
            self.opman.remove_op(indx)

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
            # create new SlacxImage object
            new_img = slacximg.SlacxImage(imgfile)
            # Add this SlacxImage to ImgManager self.imgman
            self.imgman.add_image(new_img)
            insertion_row = self.imgman.rowCount(QtCore.QModelIndex())-1
            # set self.ui.image_tree selection to be the new image
            self.ui.image_tree.setCurrentIndex(
                self.imgman.index(insertion_row,0,QtCore.QModelIndex()))

    def display_item(self):
        """
        Display selected item from the image tree 
        in a new tab in image_viewer
        """
        if self.ui.image_tree.selectedIndexes():
            # get selected item from image_tree
            indx = self.ui.image_tree.selectedIndexes()[0]
            to_display = self.imgman.get_item(indx)
            # Don't proceed unless the item has something interesting to show.
            if to_display.tag() == self.imgman.pixel_data_tag():
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
        self.ui.create_operation_button.setText("Create operation...")
        self.ui.create_operation_button.clicked.connect(self.create_operation)
        # Connect self.ui.remove_operation_button:
        self.ui.remove_operation_button.setText("Remove operation")
        self.ui.remove_operation_button.clicked.connect(self.remove_operation)
        # Connect self.ui.add_op_to_workflow_button:
        self.ui.add_op_to_workflow_button.setText("Add to workflow")
        self.ui.add_op_to_workflow_button.clicked.connect(self.add_op_to_workflow)
        # Connect self.ui.rm_op_from_workflow_button:
        self.ui.rm_op_from_workflow_button.setText("Remove from workflow")
        self.ui.rm_op_from_workflow_button.clicked.connect(self.rm_op_from_workflow)
        # Connect self.ui.apply_workflow_button:
        self.ui.apply_workflow_button.setText("Apply workflow")
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
        # Connect self.ui.operation_list (QListView) 
        # to self.opman (OpManager(QAbstractListModel))
        self.ui.operation_list.setModel(self.opman)

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

    #def pixmap_from_data(self,data_in):
    #    # downsample img_data? we are getting segfaults...
    #    data_in = data_in[0::8,0::8]
    #    height, width = data_in.shape
    #    data_out = np.zeros((height,width),dtype=long)
    #    for y in range(0,height):
    #        for x in range(0,width):
    #            mag = data_in[y,x]
    #            data_out[y,x] = QtGui.QColor(mag,mag,mag).rgb() 
    #    qimg = QtGui.QImage(data_out,width,height,QtGui.QImage.Format_RGB32)
    #    return QtGui.QPixmap(qimg)

    #        #pil_imqt = ImageQt.ImageQt(item_in.pil_img)
    #        #qimg = QtGui.QImage(pil_imqt)
    #        #img_pixmap = QtGui.QPixmap(qimg) 

    #        # Make a QtImage from item_in.img_data
    #        #height, width = item_in.img_data.shape
    #        #qt_img = QtGui.QImage(item_in.img_data,
    #        #width, height, QtGui.QImage.Format_Mono)
    #        # Make a QPixmap from this QImage
    #        #img_pixmap = QtGui.QPixmap(qt_img)

    #        # Cast image as PIL.ImageQt.ImageQt object
    #        #qtimg = item_in.qt_image() #works but leads to segfaults later on
    #        # Cast ImageQt as pixmap
    #        #img_pixmap = QtGui.QPixmap(qtimg)

    #    #with open('img_load_output.txt','w') as sys.stdout:
    #    #    item_in.load_img_data()

    #    #img_pixmap = QtGui.QPixmap(img_url)
    #    # Make a QtGui.QGraphicsPixmapItem from this QPixmap
    #    #img_pixmap_item = QtGui.QGraphicsPixmapItem(img_pixmap)
    #    # Add this QtGui.QGraphicsPixmapItem to a QtGui.QGraphicsScene 
    #    #pixmap_scene = QtGui.QGraphicsScene()
    #    #pixmap_scene.addItem(img_pixmap_item)
    #    #return pixmap_scene

                # add the QGraphicsScene to the QGraphicsView
                #new_view.setScene(qpix_scene)
                #new_view.fitInView(qpix_scene.sceneRect(),
                #QtCore.Qt.KeepAspectRatioByExpanding)

    #def render_pixmap(self,item_in):
        #"""
        #Render the input item as a QGraphicsPixmapItem,
        #and return a QGraphicsScene with this QGraphicsPixmapItem in it
        #"""
        #
        # TODO: Handle rendering of all sorts of item_in types
        # if item_in is a 2d array:
        #
        #if item_in is a SlacxImage:
        #if isinstance(item_in,slacximg.SlacxImage):
        #    # load the image data
        #    item_in.load_img_data()
        #    # make a QtGui.QPixmap from item_in.img_data
        #    img_pixmap = self.pixmap_from_data(item_in.img_data)
        #else:
        #    msg = '[{}] TODO: handle rendering for things like {}'.format(
        #        __name__,type(item_in).__name__)
        #    raise slacxex.LazyCodeError(msg)
        # Package the QPixmap in a QGraphicsPixmapItem
        #img_pixmap_item = QtGui.QGraphicsPixmapItem(img_pixmap)
        # Put pixmap item in a QGraphicsScene 
        #qpix_scene = QtGui.QGraphicsScene()
        #qpix_scene.addItem(img_pixmap_item)
        #return qpix_scene

