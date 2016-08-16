import os
from datetime import datetime as dt

from PySide import QtGui, QtCore, QtUiTools
import fabio

class UiManager():
    """
    Stores a reference to a QMainWindow,
    performs operations on it
    """

    def __init__(self,ui_file):
        """Make a UI from ui_file, save a reference to it"""
        # Pick a UI definition, load it up
        ui_file.open(QtCore.QFile.ReadOnly)
        # load() produces a QMainWindow(QWidget).
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()

    def dtstr(self):
        """Return date and time as a string"""
        return dt.strftime(dt.now(),'%Y %m %d, %H:%M:%S')

    def msg_board_log(self,msg):
        """Print timestamped message with space to msg board"""
        self.ui.message_board.insertPlainText(
        self.dtstr() + '\n' + msg + '\n\n') 

    def show_status(self,msg):
        self.ui.statusbar.showMessage(msg)

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
 
    def close_image(self):
        """Close a selected image out of the slacx image list"""
        pass

    def open_image(self):
        """Open an image for slacx, add it to image views"""
        # Open a file browser window, select a *.tif
        # API: getOpenFileName(parent(Widget), caption, dir, extension regexp)
        imgfile, ext = QtGui.QFileDialog.getOpenFileName(
        self.ui, 'Open file', os.getcwd(), ['*.tif','*.raw','*.edf'])
        if imgfile:
            msg='[{}] Opening file: {}'.format(__name__,imgfile)
            self.msg_board_log(msg) 
        # Make a QtGui.QPixmap from this file
        img_pixmap = QtGui.QPixmap(imgfile)
        # Make a QtGui.QGraphicsPixmapItem from this QPixmap
        img_pixmap_item = QtGui.QGraphicsPixmapItem(img_pixmap)
        # Add this QtGui.QGraphicsPixmapItem to a QtGui.QGraphicsScene 
        img_scene = QtGui.QGraphicsScene()
        img_scene.addItem(img_pixmap_item)
        # TODO: Put the image in the image list
        # TODO: Put the image in the I/O list
        # TODO: If this is the top image in the image list:
        if True:
            # add the QGraphicsScene to the QGraphicsView
            self.ui.image_1.setScene(img_scene)
            # TODO: Ensure the image fits in the view

    def final_setup(self):
        # Let the message board be read-only
        self.ui.message_board.setReadOnly(True)
        # Tell the status bar that we are ready.
        self.show_status('Ready')
        # Tell the message board that we are ready.
        self.msg_board_log('slacx ready') 


