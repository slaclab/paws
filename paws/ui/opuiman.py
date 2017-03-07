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
        self.op = None
        self.filepath = ''

    def get_op(self,idx):
        itm = self.opman.get_item(idx)
        x = itm.data
        try:
            op_flag = issubclass(x,Operation)
            #op_flag = isinstance(x,Operation)
        except:
            op_flag = False
        if op_flag:
            op_uri = self.opman.build_uri(idx)
            self.filepath = pawstools.sourcedir + '/' + 'paws/core/operations'
            for uri_piece in op_uri.split('.'):
                self.filepath = self.filepath + '/' + uri_piece
            self.filepath = self.filepath + '.py'
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
        # if op is not enabled, display a message
        # else, inspect the op
        path_display = QtGui.QTextEdit()
        path_display.setText('file path: ' + self.filepath)
        self.ui.op_source_layout.addWidget( path_display,0,0,1,1 )
        inputs_box = QtGui.QGroupBox('INPUTS',self.ui)
        inputs_lo = QtGui.QGridLayout(inputs_box)
        if len(self.op.inputs) > 0:
            inputs_lo.addWidget(uitools.r_hdr_widget('name'),0,0,1,1)
            inputs_lo.addWidget(uitools.hdr_widget('default source'),0,2,1,1)
            inputs_lo.addWidget(uitools.hdr_widget('default type'),0,3,1,1)
            inputs_lo.addWidget(uitools.hdr_widget('default value'),0,4,1,1)
        for ii in range(len(self.op.inputs)):
            rowii = ii+1
            # name
            name = self.op.inputs.keys()[ii] 
            name_widget = uitools.name_widget(name)
            inputs_lo.addWidget( name_widget,rowii,0,1,1 )
            # = 
            eq_widget = uitools.smalltext_widget('=')
            inputs_lo.addWidget(eq_widget,rowii,1,1,1)
            # src
            src_widget = uitools.src_selection_widget()
            if self.op.input_src[name] is not None:
                src = self.op.input_locator[name].src
            else:
                src = optools.no_input 
            src_widget.setCurrentIndex(src)
            inputs_lo.addWidget(src_widget,rowii,2,1,1)
            # type
            type_widget = uitools.type_selection_widget(src)
            if self.op.input_type[name] is not None:
                tp = self.op.input_locator[name].tp
            else:
                tp = optools.none_type
            type_widget.setCurrentIndex(tp)
            inputs_lo.addWidget(src_widget,rowii,3,1,1)
            # value
            val_widget = QtGui.QLineEdit()
            if self.op.inputs[name] is not None:
                valtext = str(self.op.inputs[name])
            else:
                valtext = 'None'
            inputs_lo.addWidget(src_widget,rowii,4,1,1)
        inputs_box.setLayout(inputs_lo)

    def edit_op(self):
        print 'edit op'

    def enable_ops(self):
        print 'enable ops'

    def setup_ui(self):
        self.ui.setWindowTitle("operation setup")
        self.ui.op_selector.setModel(self.opman)
        self.ui.op_selector.hideColumn(1)
        self.ui.op_selector.hideColumn(2)
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

