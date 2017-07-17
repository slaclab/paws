from __future__ import print_function
import inspect
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from . import uitools
from ..core import pawstools
from ..core.operations.Operation import Operation

class OpUiManager(QtCore.QObject):

    def __init__(self,qopman):
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/op_editor.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        # set self.ui to be deleted and to emit destroyed() signal when its window is closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.qopman = qopman 
        self.setup_ui()
        self.op = None
        self.filepath = ''
        self.opname_widget = None
        self.path_widget = None
        self.run_widget = None
        self.import_widgets = []
        self.name_widgets = {}
        self.src_widgets = {}
        self.type_widgets = {}
        self.val_widgets = {}
        self.outname_widgets = {}
        self.outdesc_widgets = {}
        self._edit_mode = False

    def get_op(self,idx):
        x = self.qopman.get_data_from_index(idx)
        try:
            op_flag = issubclass(x,Operation)
        except:
            op_flag = False
        if op_flag:
            op_uri = self.qopman.opman.get_uri_of_index(idx)
            self.filepath = pawstools.sourcedir + '/core/operations'
            for uri_piece in op_uri.split('.'):
                self.filepath = self.filepath + '/' + uri_piece
            self.filepath = self.filepath + '.py'
            self.clear_op()
            self.set_op(x())
        else:
            self.clear_op()
            self.ui.op_info.setPlainText('Selected item: {}'.format(x))
    
    def clear_op(self):
        #self.ui.op_name.setText('')
        n_widg = self.ui.op_source_layout.count()
        for i in range(n_widg-1,-1,-1):
            itm = self.ui.op_source_layout.takeAt(i)
            itm.widget().close()
            itm.widget().deleteLater()
        self.name_widgets = {}
        self.src_widgets = {}
        self.type_widgets = {}
        self.val_widgets = {}
        self.outname_widgets = {}
        self.outdesc_widgets = {}

    def set_op(self,op):
        """Set up ui elements around existing input op"""
        self.op = op
        self.op.load_defaults()
        self.ui.op_info.setPlainText(self.op.description())
        self.build_source()

    def build_source(self):
        src_font = QtGui.QFont("Courier New", 10)
        self.opname_widget = QtGui.QLineEdit()
        self.opname_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.opname_widget.setText(type(self.op).__name__)
        # if op is not enabled, display a message
        # else, inspect the op
        path_box = QtGui.QGroupBox('PATH')
        path_lo = QtGui.QGridLayout(path_box)
        self.path_widget = QtGui.QTextEdit()
        self.path_widget.setText(self.filepath)
        self.path_widget.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.path_widget.setMaximumHeight(50)
        # TODO: Make so that name widget is updated when path widget is edited
        path_lo.addWidget(self.path_widget,0,0,1,1)
        #self.path_widget.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.MinimumExpanding)
        imports_box = QtGui.QGroupBox('IMPORTS',self.ui)
        imports_lo = QtGui.QGridLayout(imports_box)
        imp_lines = []
        for line in open(self.filepath,'r').readlines():
            if line.find('import') >= 0:
                imp_lines.append(line)
        for ii in range(len(imp_lines)):
            # TODO: try to separate imports: standard, 3rd-party, local
            imp_widget = QtGui.QTextEdit()
            imp_widget.setCurrentFont(src_font)
            imp_widget.setMaximumHeight(30)
            #imp_widget.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
            imp_widget.setText(imp_lines[ii].strip())
            imports_lo.addWidget(imp_widget,ii,0,1,1)
            self.import_widgets.append(imp_widget)
        #mod_src = inspect.getsource(self.op)
        # set widgets for operation inputs
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
            inputs_lo.addWidget( eq_widget,rowii,1,1,1 )
            # src
            src_widget = uitools.src_selection_widget()
            if self.op.input_src[name] is not None:
                src = self.op.input_locator[name].src
            else:
                src = op.no_input 
            src_widget.setCurrentIndex(src)
            inputs_lo.addWidget( src_widget,rowii,2,1,1 )
            # type
            type_widget = uitools.type_selection_widget(src)
            if self.op.input_type[name] is not None:
                tp = self.op.input_locator[name].tp
            else:
                tp = op.none_type
            type_widget.setCurrentIndex(tp)
            inputs_lo.addWidget( type_widget,rowii,3,1,1 )
            # value
            val_widget = QtGui.QLineEdit()
            if self.op.inputs[name] is not None:
                valtext = str(self.op.inputs[name])
            else:
                valtext = 'None'
            inputs_lo.addWidget( val_widget,rowii,4,1,1 )
            self.name_widgets[name] = name_widget 
            self.src_widgets[name] = src_widget
            self.type_widgets[name] = type_widget
            self.val_widgets[name] = val_widget
        inputs_box.setLayout(inputs_lo)
        # set widgets for operation outputs
        outputs_box = QtGui.QGroupBox('OUTPUTS',self.ui)
        outputs_lo = QtGui.QGridLayout(outputs_box)
        if len(self.op.outputs) > 0:
            outputs_lo.addWidget(uitools.r_hdr_widget('name'),0,0,1,1)
            outputs_lo.addWidget(uitools.hdr_widget('description'),0,2,1,1)
        for ii in range(len(self.op.outputs)):
            rowii = ii+1
            # name
            name = self.op.outputs.keys()[ii] 
            name_widget = uitools.name_widget(name)
            outputs_lo.addWidget( name_widget,rowii,0,1,1 )
            # = 
            eq_widget = uitools.smalltext_widget('=')
            outputs_lo.addWidget( eq_widget,rowii,1,1,1 )
            # description 
            desc_widget = uitools.bigtext_widget(self.op.output_doc[name])
            outputs_lo.addWidget( desc_widget,rowii,2,1,1 )
            self.outname_widgets[name] = name_widget 
            self.outdesc_widgets[name] = desc_widget 
        outputs_box.setLayout(outputs_lo)
        # set a widget for the run() function
        #run_widget = QtGui.QTextEdit()
        run_box = QtGui.QGroupBox('RUN METHOD')
        run_lo = QtGui.QGridLayout(run_box)
        self.run_widget = uitools.QSourceEdit()
        run_text = inspect.getsource(self.op.run)
        self.run_widget.setCurrentFont(src_font)
        self.run_widget.setText(run_text)
        self.run_widget.setTabStopWidth(40)
        self.run_widget.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.run_widget.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.MinimumExpanding)
        run_lo.addWidget(self.run_widget,0,0,1,1)
        # finally, add the widgets to op_source_layout
        self.ui.op_source_layout.addWidget( self.opname_widget,0,0,1,1 )
        self.ui.op_source_layout.addWidget( path_box,1,0,1,1 )
        self.ui.op_source_layout.addWidget( imports_box,2,0,1,1 )
        self.ui.op_source_layout.addWidget( inputs_box,3,0,1,1 )
        self.ui.op_source_layout.addWidget( outputs_box,4,0,1,1 )
        self.ui.op_source_layout.addWidget( run_box,5,0,1,1 )
        self.set_read_mode()

    def edit_save_op(self):
        if self._edit_mode:
            save_status = self.attempt_save()
            if save_status:
                self.set_read_mode()
        else:
            self.set_edit_mode() 

    def attempt_save(self):
        print('save op')
        ####
        # SAVE
        ####
        saved = True
        return saved

    def set_read_mode(self):
        print('setting to read mode')
        self._edit_mode = False
        #self.ui.op_name.setReadOnly(True)
        for widg in self.import_widgets:
            widg.setReadOnly(True)
        self.ui.edit_save_button.setText("&Edit operation")

    def set_edit_mode(self):
        print('setting to edit mode')
        self._edit_mode = True
        self.ui.edit_save_button.setText("&Save operation")

    def enable_ops(self):
        print('enable ops')

    def setup_ui(self):
        self.ui.setWindowTitle("operation setup")
        self.ui.op_selector.setModel(self.qopman)
        self.ui.op_selector.hideColumn(1)
        self.ui.op_selector.hideColumn(2)
        self.ui.op_selector.clicked.connect( partial(self.get_op) )
        self.ui.edit_save_button.setText("&Edit operation")
        self.ui.enable_op_button.setText("&Enable operations")
        self.ui.edit_save_button.clicked.connect(self.edit_save_op)
        self.ui.enable_op_button.clicked.connect(self.enable_ops)
        self.ui.op_selector.clicked.connect( partial(uitools.toggle_expand,self.ui.op_selector) ) 
        #self.ui.op_name.setAlignment(QtCore.Qt.AlignCenter)
        #self.ui.op_name.setText('-select an operation to view source-')
        self.ui.splitter.setStretchFactor(1,1000)    
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )

