from PySide import QtGui, QtCore

# TODO: Get QtGui out of this module - it is a core module

##### DEFINITIONS OF SOURCES FOR OPERATION INPUTS
input_sources = ['None','Filesystem','Operations','Text'] 
no_input = 0
fs_input = 1
op_input = 2
text_input = 3
valid_sources = [no_input,fs_input,op_input,text_input]

##### VALID TYPES FOR TEXT BASED OPERATION INPUTS 
input_types = ['None','string','integer','float','boolean']
none_type = 0
str_type = 1
int_type = 2
float_type = 3
bool_type = 4
valid_types = [none_type,str_type,int_type,float_type,bool_type]
# TODO: implement some kind of builder/loader for data structs, like arrays or dicts
#array_type = 5
        
##### IMAGE LOADER EXTENSIONS    
def loader_extensions():
    return str(
    "ALL (*.*);;"
    + "TIFF (*.tif *.tiff);;"
    + "RAW (*.raw);;"
    + "MAR (*.mar*)"
    )

##### CONVENIENCE METHOD FOR PRINTING DOCUMENTATION
def parameter_doc(name,value,doc):
    if type(value).__name__ == 'InputLocator':
        val_str = str(value.val)
    else:
        val_str = str(value)
    return "- name: {} \n- value: {} \n- doc: {}".format(name,val_str,doc) 

##### CONVENIENCE CLASS FOR STORING OR LOCATING OPERATION INPUTS
class InputLocator(object):
    """
    This object is used as a container for an input to an Operation.
    Objects of this class contain the information needed to find the relevant input data.
    If raw textual input is provided, it is stored in self.val after typecasting.
    """
    def __init__(self,src,val):
        if src < 0 or src > len(input_sources):
            msg = 'found input source {}, should be between 0 and {}'.format(
            src, len(input_sources))
            raise ValueError(msg)
        self.src = src
        self.val = val 
        self.data = None 

def text_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignHCenter)
    return widg 

def src_selection_widget():
    widg = QtGui.QComboBox()
    widg.addItems(input_sources)
    widg.setMinimumWidth(120)
    return widg 

#def item_selection_widget(self):
#    widg = QtGui.QPushButton('Select...')
#    return widg

#def vert_hdr_widget(self,text):
#    # TODO: Fix this, some day.
#    widg = VertQLineEdit(text)
#    return widg 

def hdr_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignHCenter)
    widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
    return widg 

def smalltext_widget(text):
    widg = text_widget(text)
    widg.setMaximumWidth( 20 )
    widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
    return widg

def bigtext_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setMinimumWidth(7*len(text))
    # TODO: Truncate the text?
    widg.setAlignment(QtCore.Qt.AlignLeft)
    return widg

def namewidget(name):
    name_widget = QtGui.QLineEdit(name)
    name_widget.setReadOnly(True)
    name_widget.setAlignment(QtCore.Qt.AlignRight)
    name_widget.setMinimumWidth(7*len(name))
    #name_widget.setMaximumWidth(15*len(name))
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

