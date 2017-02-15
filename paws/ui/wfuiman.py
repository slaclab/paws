from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from ..core.operations import optools
from ..core.operations.operation import Operation 
from ..core import pawstools
from ..core.operations.optools import InputLocator
from .input_loader import InputLoader
from . import uitools

class WfUiManager(object):

    def __init__(self,wfman,opman,plugman):
        ui_file = QtCore.QFile(pawstools.rootdir+"/ui/qtui/wf_editor.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.wfman = wfman 
        self.opman = opman 
        self.plugman = plugman 
        self.op = None
        # Dicts to keep track of input widgets, keyed by input variable names
        self.src_widgets = {} 
        self.type_widgets = {} 
        self.val_widgets = {} 
        self.btn_widgets = {} 
        self.input_loaders = {} 
        self.setup_ui()
        # Column definitions for the io layout        
        self.name_col = 0
        self.eq_col = 1
        self.src_col = 2
        self.type_col = 3
        self.val_col = 4
        self.btn_col = 5

    def get_op(self,trmod,itm_idx):
        xitem = trmod.get_item(itm_idx)
        if xitem.data:
            x = xitem.data
            try:
                new_op_flag = issubclass(x,Operation)
            except:
                new_op_flag = False
            try:
                existing_op_flag = isinstance(x,Operation)
            except:
                existing_op_flag = False
            if not new_op_flag and not existing_op_flag:  
                self.clear_io()
                self.ui.op_info.setPlainText('Selected item: {}'.format(x))
            elif new_op_flag:
                # Create a new Operation 
                self.create_op(x)
            elif existing_op_flag:
                # Load existing Operation
                self.set_op(x,xitem.tag())

    def set_op(self,op,uri):
        """Set up ui elements around existing input op"""
        # TODO: Instead, copy the input op, then load it,
        # and ensure that the workflow updates properly when finished
        self.op = op
        self.ui.op_info.setPlainText(self.op.description())
        self.build_io()
        self.ui.uri_entry.setText(uri)

    def create_op(self,op):
        """Instantiate op, call self.set_op()"""
        new_op = op()
        new_op_tag = self.wfman.auto_tag(type(new_op).__name__)
        new_op.load_defaults()
        self.set_op(new_op,new_op_tag)

    def rm_op(self):
        """
        remove the selected operation from the workflow
        """
        idx = self.ui.wf_selector.currentIndex()
        if idx.isValid(): 
            while idx.internalPointer().parent.isValid():
                idx = idx.internalPointer().parent
            self.wfman.remove_op(idx)
        self.clear_io()

    def load_op(self):
        """
        Package the finished Operation, ship to self.wfman
        """ 
        # Make sure all inputs are loaded
        for name in self.op.inputs.keys():
            self.set_input(name)
        uri = self.ui.uri_entry.text()
        result = self.wfman.is_good_tag(uri)
        if result[0]:
            self.wfman.add_op(uri,self.op) 
            self.clear_io()
        elif result[1] == 'Tag not unique':
            self.wfman.update_op(uri,self.op)
            self.clear_io()
        else:
            # Request a different uri 
            msg_ui = uitools.message_ui(self.ui)
            msg_ui.setWindowTitle("Tag Error")
            msg_ui.message_box.setPlainText(self.wfman.tag_error(uri,result[1]))
            msg_ui.show()

    def set_input(self,name,src_ui=None):
        """
        Call build_input_locator to package an InputLocator for named input. 
        Store it in self.op.input_locator[name].
        This is called on all inputs when an Operation is loaded,
        so it should not alter an identical already-loaded input.
        """
        il = self.build_input_locator(name,src_ui)
        self.op.input_locator[name] = il
        # dereference the old input
        self.op.inputs[name] = None 

    def build_input_locator(self,name,ui=None):
        """
        Create an InputLocator for named input.
        If a ui is provided, it should be an input_loader.ui,
        and this should load data from that ui.
        """
        src = self.src_widgets[name].currentIndex()
        tp = self.type_widgets[name].currentIndex()
        il = None
        if src == optools.no_input:
            il = optools.InputLocator() 
        elif src == optools.batch_input:
            if tp == optools.ref_type:
                # TODO: set val to indicate which batch (if any) will set this input 
                val = 'auto' 
            else:
                val = None
            il = optools.InputLocator(src,tp,val) 
        else:
            # all other input sources use a ui for loading
            if ui:
                val = self.fetch_from_input_ui(ui) 
                il = optools.InputLocator(src,tp,val)
                self.val_widgets[name].setText(str(il.val))
                ui.close()
                #ui.deleteLater()
                # dereference the ui now that it is closed...
                self.input_loaders[name] = None
            else:
                # else, the input has already been loaded.
                # if src, tp, and val match, do nothing.
                val = self.val_widgets[name].text()
                if (self.op.input_locator[name].src == src 
                and self.op.input_locator[name].tp == tp 
                and str(self.op.input_locator[name].val) == val):
                    il = self.op.input_locator[name]
                else:
                    il = optools.InputLocator(src,tp,val)
        return il

    def fetch_from_input_ui(self,ui):
        # no matter the input source, ui.values_list.model().list_data() should be a list of strings.
        val = ui.values_list.model().list_data()
        # if ui.list_toggle is not checked, the value should be unpacked. 
        if not ui.list_toggle.isChecked():
            if len(val) == 0:
                val = None
            else:
                val = val[0]
        return val

    def fetch_data(self,name):
        if name in self.input_loaders.keys():
            if self.input_loaders[name]:
                self.input_loaders[name].ui.close()
                self.input_loaders[name] = None
        src = self.src_widgets[name].currentIndex()
        if src == optools.wf_input:
            inp_loader = InputLoader(name,src,self.wfman,self.ui)
        elif src == optools.fs_input:
            trmod = QtGui.QFileSystemModel()
            #trmod.setRootPath(QtCore.QDir.currentPath())
            #trmod.setRootPath('.')
            inp_loader = InputLoader(name,src,trmod,self.ui)
        elif src == optools.plugin_input:
            inp_loader = InputLoader(name,src,self.plugman,self.ui)
        elif src == optools.text_input:
            inp_loader = InputLoader(name,src,None,self.ui)
        if self.op.input_locator[name].src == src and self.op.input_locator[name].val is not None:
            if isinstance(self.op.input_locator[name].val,list):
                inp_loader.set_list_toggle()
                for v in self.op.input_locator[name].val:
                    inp_loader.add_value(str(v))
            else:
                inp_loader.add_value(str(self.op.input_locator[name].val))
        inp_loader.ui.finish_button.clicked.connect( partial(self.set_input,name,inp_loader.ui) )
        self.input_loaders[name] = inp_loader

    def clear_io(self):
        self.ui.op_name.setText('')
        self.ui.uri_entry.setText('')
        self.ui.load_button.setEnabled(False)
        n_inp_widgets = self.ui.input_layout.count()
        for i in range(n_inp_widgets-1,-1,-1):
            item = self.ui.input_layout.takeAt(i)
            item.widget().close()
            #item.widget().deleteLater()
        n_out_widgets = self.ui.output_layout.count()
        for i in range(n_out_widgets-1,-1,-1):
            item = self.ui.output_layout.takeAt(i)
            item.widget().close()
            #item.widget().deleteLater()
        self.src_widgets = {}
        self.type_widgets = {}
        self.val_widgets = {}
        self.btn_widgets = {}
        self.input_loaders = {}
    
    def reset_input_headers(self):
        if len(self.op.inputs) > 0:
            self.ui.input_layout.addWidget(uitools.r_hdr_widget('name'),0,self.name_col,1,1)
            self.ui.input_layout.addWidget(uitools.hdr_widget('source'),0,self.src_col,1,1)
            self.ui.input_layout.addWidget(uitools.hdr_widget('type'),0,self.type_col,1,1)
            self.ui.input_layout.addWidget(uitools.hdr_widget('value'),0,self.val_col,1,1)

    def reset_output_headers(self):
        if len(self.op.outputs) > 0:
            self.ui.output_layout.addWidget(uitools.r_hdr_widget('name'),0,self.name_col,1,1)
            self.ui.output_layout.addWidget(uitools.hdr_widget('description'),0,self.src_col,1,self.btn_col-self.src_col)

    def build_io(self):
        self.clear_io()
        self.reset_input_headers()
        self.reset_output_headers()
        self.ui.op_name.setText(type(self.op).__name__)
        self.ui.load_button.setEnabled(True)
        for i,name in zip(range(1,len(self.op.inputs)+1),self.op.inputs.keys()):
            # name 
            name_widget = uitools.name_widget(name)
            self.ui.input_layout.addWidget( name_widget,i,self.name_col,1,1 )
            # '=' 
            eq_widget = uitools.smalltext_widget('=')
            self.ui.input_layout.addWidget(eq_widget,i,self.eq_col,1,1)
            # source 
            src_widget = uitools.src_selection_widget()
            if self.op.input_locator[name] is not None:
                src = self.op.input_locator[name].src
            else:
                src = optools.no_input 
            src_widget.setCurrentIndex(src)
            self.ui.input_layout.addWidget( src_widget,i,self.src_col,1,1 )
            self.src_widgets[name] = src_widget 
            self.src_widgets[name].currentIndexChanged.connect( partial(self.reset_type_widget,name,i) )
            self.reset_type_widget(name,i,src)
        # Now handle outputs, much easier
        for i,name in zip(range(1,len(self.op.outputs)+1),self.op.outputs.keys()):
            # TODO: allow multiple lines for the desc_widgets.
            name_widget = uitools.name_widget(name)
            self.ui.output_layout.addWidget(name_widget,i,self.name_col)
            eq_widget = uitools.smalltext_widget('=')
            self.ui.output_layout.addWidget(eq_widget,i,self.eq_col)
            if self.op.output_doc[name]:
                desc_widget = uitools.bigtext_widget(self.op.output_doc[name])
            else:
                desc_widget = uitools.bigtext_widget('No description found.')
            self.ui.output_layout.addWidget(desc_widget,i,self.src_col,1,self.btn_col-self.src_col)

    def reset_type_widget(self,name,row,src=None):
        if name in self.type_widgets.keys():
            if self.type_widgets[name]:
                self.type_widgets[name].close()
        if not src:
            src = self.src_widgets[name].currentIndex()
        new_type_widget = uitools.type_selection_widget(src)
        if not self.op.input_locator[name].src == optools.no_input:
            if (self.op.input_locator[name].tp not in optools.invalid_types[src]
            and self.op.input_locator[name].src == src):
                # load operation defaults
                new_type_widget.setCurrentIndex(self.op.input_locator[name].tp)
            else:
                # set sensible defaults
                if src == optools.fs_input:
                    new_type_widget.setCurrentIndex(optools.path_type)
                elif src in [optools.wf_input,optools.plugin_input]:
                    new_type_widget.setCurrentIndex(optools.ref_type)
                elif src == optools.batch_input:
                    new_type_widget.setCurrentIndex(optools.auto_type)
        new_type_widget.currentIndexChanged.connect( partial(self.reset_val_widget,name,row,src) )            
        self.type_widgets[name] = new_type_widget  
        self.ui.input_layout.addWidget(new_type_widget,row,self.type_col,1,1)
        tp = self.type_widgets[name].currentIndex()
        self.reset_val_widget(name,row,src,tp)

    def reset_val_widget(self,name,row,src=None,tp=None):
        # TODO: Make val widgets expand height according to their content 
        if name in self.val_widgets.keys():
            if self.val_widgets[name]:
                self.val_widgets[name].close()
        if name in self.btn_widgets.keys():
            if self.btn_widgets[name]:
                self.btn_widgets[name].close()
        if name in self.input_loaders.keys():
            if self.input_loaders[name]:
                self.input_loaders[name].ui.close()
                self.input_loaders[name] = None
        if not src:
            src = self.src_widgets[name].currentIndex()
        if not tp:
            tp = self.type_widgets[name].currentIndex()
        btn_widget = QtGui.QPushButton()
        val_widget = QtGui.QLineEdit()
        #val_widget = QtGui.QTextEdit()
        if src == optools.no_input or tp == optools.none_type: 
            btn_widget.setText('no input')
            btn_widget.setEnabled(False)
            val_widget.setText('None')
        elif src == optools.batch_input:
            btn_widget.setText('auto')
            btn_widget.setEnabled(False)
            val_widget.setText('auto (batch)')
        elif src in [optools.wf_input,optools.fs_input,optools.plugin_input,optools.text_input]:
            btn_widget.setText('edit...')
            btn_widget.clicked.connect( partial(self.fetch_data,name) )
            if self.op.input_locator[name]:
                if self.op.input_locator[name].src == src:# and self.op.input_locator[name].tp == tp:
                    val_widget.setText(str(self.op.input_locator[name].val))
        val_widget.setReadOnly(True)
        self.ui.input_layout.addWidget(val_widget,row,self.val_col,1,1)
        self.ui.input_layout.addWidget(btn_widget,row,self.btn_col,1,1)
        self.val_widgets[name] = val_widget
        self.btn_widgets[name] = btn_widget

    def setup_ui(self):
        # TODO: constrain the height of the FINISH/LOAD box
        self.ui.setWindowTitle("workflow setup")
        self.ui.input_box.setTitle("INPUTS")
        self.ui.output_box.setTitle("OUTPUTS")
        self.ui.finish_box.setTitle("FINISH / LOAD")
        ht = self.ui.op_frame.sizeHint().height()
        self.ui.op_frame.sizeHint = lambda: QtCore.QSize(400,ht)
        self.ui.op_frame.setSizePolicy(
        QtGui.QSizePolicy.Minimum,self.ui.op_frame.sizePolicy().verticalPolicy())
        self.ui.wf_selector.setModel(self.wfman)
        self.ui.wf_selector.hideColumn(1)
        self.ui.wf_selector.clicked.connect( partial(self.get_op,self.wfman) )
        self.ui.rm_op_button.setText("&Remove selected operation")
        self.ui.rm_op_button.clicked.connect(self.rm_op)
        self.ui.op_selector.setModel(self.opman)
        self.ui.op_selector.hideColumn(1)
        self.ui.op_selector.clicked.connect( partial(self.get_op,self.opman) )
        self.ui.op_selector.clicked.connect( partial(uitools.toggle_expand,self.ui.op_selector) ) 
        self.ui.wf_selector.clicked.connect( partial(uitools.toggle_expand,self.ui.wf_selector) )
        self.ui.uri_prompt.setMaximumWidth(150)
        self.ui.uri_prompt.setText('operation tag:')
        self.ui.uri_prompt.setReadOnly(True)
        self.ui.op_name.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.op_name.setText('-select an operation to begin setup-')
        self.ui.uri_prompt.setAlignment(QtCore.Qt.AlignRight)
        self.ui.uri_prompt.setStyleSheet( "QLineEdit { background-color: transparent }" 
        + self.ui.uri_prompt.styleSheet() )
        self.ui.load_button.setText("&Finish")
        self.ui.load_button.clicked.connect(self.load_op)
        self.ui.load_button.setDefault(True)
        self.ui.load_button.setEnabled(False)
        self.ui.load_button.setMinimumWidth(100)
        self.ui.splitter.setStretchFactor(0,1000)    
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )


