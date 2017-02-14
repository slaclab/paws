from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from . import uitools
from ..core import pawstools
from ..core.operations.operation import Operation

class OpUiManager(object):

    def __init__(self,opman):
        ui_file = QtCore.QFile(pawstools.rootdir+"/ui/qtui/op_editor.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.opman = opman 
        self.setup_ui()

    def get_op(self,idx):
        itm = self.opman.get_item(idx)
        x = itm.data
        try:
            op_flag = issubclass(x,Operation)
            #op_flag = isinstance(x,Operation)
        except:
            op_flag = False
        if op_flag:
            self.clear_op()
            self.set_op(x())
        else:
            self.clear_op()
            self.ui.op_info.setPlainText('Selected item: {}'.format(x))
    
    def clear_op(self):
        self.ui.op_name.setText('')
        n_widg = self.ui.op_source_layout.count()
        for i in range(n_widg-1,-1,-1):
            itm = self.ui.op_source_layout.takeAt(i)
            itm.widget().close()

    def set_op(self,op):
        """Set up ui elements around existing input op"""
        self.op = op
        self.ui.op_info.setPlainText(self.op.description())
        self.build_source()

    def build_source(self):
        self.ui.op_name.setText(type(self.op).__name__)

    def edit_op(self):
        print 'edit op'

    def enable_ops(self):
        print 'enable ops'

    def setup_ui(self):
        self.ui.setWindowTitle("operation setup")
        self.ui.op_selector.setModel(self.opman)
        self.ui.op_selector.hideColumn(1)
        self.ui.op_selector.clicked.connect( partial(self.get_op) )
        self.ui.edit_op_button.setText("&Edit operation")
        self.ui.enable_op_button.setText("&Enable operations")
        self.ui.edit_op_button.clicked.connect(self.edit_op)
        self.ui.enable_op_button.clicked.connect(self.enable_ops)
        self.ui.op_selector.clicked.connect( partial(uitools.toggle_expand,self.ui.op_selector) ) 
        self.ui.op_name.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.op_name.setText('-select an operation to view source-')
        self.ui.splitter.setStretchFactor(1,1000)    
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )

