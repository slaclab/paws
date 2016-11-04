import re
import platform

from PySide import QtGui, QtCore

from ..slacxcore.operations import optools

## Test whether we have Qt >= 4.7 
have_qt47 = True
versionReq = [4, 7]
QtVersion = QtCore.__version__ 
m = re.match(r'(\d+)\.(\d+).*', QtVersion)
if m is not None and list(map(int, m.groups())) < versionReq:
    have_qt47 = False

## Test whether we are using Windows
if platform.system() == 'Windows':
    have_windows = True
else:
    have_windows = False

def text_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignHCenter)
    return widg 

def src_selection_widget():
    widg = QtGui.QComboBox()
    widg.addItems(optools.input_sources)
    return widg 

def hdr_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignHCenter)
    widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
    return widg 

def smalltext_widget(text):
    widg = text_widget(text)
    widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
    return widg

def bigtext_widget(text,trunc_limit=70):
    if len(text) > trunc_limit:
        display_text = text[:trunc_limit]+'...'
    else:
        display_text = text
    widg = QtGui.QLineEdit(display_text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignLeft)
    return widg

def namewidget(name):
    name_widget = QtGui.QLineEdit(name)
    name_widget.setReadOnly(True)
    name_widget.setAlignment(QtCore.Qt.AlignRight)
    return name_widget

##### MINIMAL CLASS FOR VERTICAL HEADERS
#class VertQLineEdit(QtGui.QLineEdit):
class VertQLineEdit(QtGui.QWidget):
    """QLineEdit, but vertical"""
    def __init__(self,text):
        super(VertQLineEdit,self).__init__()
        self.text = text
        #wid = self.geometry().width()
        #ht = self.geometry().height()
        #rt = self.geometry().right()
        #t = self.geometry().top()
        # QWidget.setGeometry(left,top,width,height)
        #self.setGeometry(t, rt, ht, wid)

    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.rotate(90)
        qp.drawText(0,0,self.text)
        qp.end()




