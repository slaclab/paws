from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from ..core.operations import Operation as op
from ..core import pawstools
from ..core.models.ListModel import ListModel
from .InputLoader import InputLoader
from . import uitools

class WfUiManager(QtCore.QObject):
    # TODO: remove calls to workflow instance methods.
    # Replace with calls to workflow manager.

    def __init__(self,qwfman,qopman,qplugman):
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/wf_editor.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        # set self.ui to be deleted and to signal destroyed()
        # when its window is closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.qwfman = qwfman
        self.qopman = qopman 
        self.qplugman = qplugman 
        self.op = None
        self.setup_ui()
        # Dicts to keep track of input widgets, keyed by input variable names
        self.src_widgets = {} 
        self.type_widgets = {} 
        self.val_widgets = {} 
        self.btn_widgets = {} 
        self.input_loaders = {} 
        # Column definitions for the io layout        
        self.name_col = 0
        self.eq_col = 1
        self.src_col = 2
        self.type_col = 3
        self.val_col = 4
        self.btn_col = 5
        self.set_wf()

    def set_wf(self,wf_idx=None):
        if wf_idx is None:
            wf_idx = self.ui.wf_selector.currentIndex()
        wfname = self.ui.wf_selector.model().list_data()[wf_idx]
        self.ui.wf_browser.setModel(self.qwfman.qworkflows[wfname])
        self.ui.wf_browser.setRootIndex(self.qwfman.qworkflows[wfname].root_index())
        self.ui.wf_browser.hideColumn(1)
        self.ui.wf_browser.hideColumn(2)

    def current_wf(self):
        wfname = self.current_wfname()
        if wfname:
            return self.qwfman.qworkflows[wfname]

    def current_wfname(self):
        current_wf_idx = self.ui.wf_selector.currentIndex()
        if current_wf_idx > -1:
            return self.ui.wf_selector.model().list_data()[current_wf_idx]
        else:
            return None

    def get_op(self,src_qtree=None,itm_idx=QtCore.QModelIndex()):
        if src_qtree is None:
            src_qtree = self.current_wf()
        x = src_qtree.get_data_from_index(itm_idx)
        if x is not None:
            try:
                new_op_flag = issubclass(x,op.Operation)
            except:
                new_op_flag = False
            try:
                existing_op_flag = isinstance(x,op.Operation)
            except:
                existing_op_flag = False
            if not new_op_flag and not existing_op_flag:  
                self.op = None
                self.clear_io()
                #self.ui.op_info.setPlainText('Selected item: {}'.format(x))
            elif new_op_flag:
                # Create a new Operation 
                self.create_op(x)
            elif existing_op_flag:
                # Copy the setup of existing Operation
                op_dict = self.qwfman.wfman.op_setup_dict(x)
                # Get a new op with the same setup
                op_copy = self.qwfman.wfman.build_op_from_dict(op_dict,self.qopman.opman)
                op_tag = src_qtree.get_uri_of_index(itm_idx)
                self.set_op(op_copy,op_tag)

    def set_op(self,op,op_tag):
        """Set up ui elements around input op"""
        self.op = op
        #self.ui.op_info.setPlainText(self.op.description())
        self.build_io()
        self.ui.tag_entry.setText(op_tag)

    def create_op(self,op):
        """Instantiate op, call self.set_op()"""
        new_op = op()
        new_op_tag = self.current_wf()._tree.make_unique_uri(type(new_op).__name__)
        new_op.load_defaults()
        self.set_op(new_op,new_op_tag)

    def remove_op(self):
        """
        remove the selected operation from the workflow
        """
        idx = self.ui.wf_browser.currentIndex()
        if idx.isValid():
            itm = self.current_wf().get_from_index(idx) 
            while not itm.parent == self.current_wf()._tree._root_item:
                itm = itm.parent
            self.current_wf().remove_item(itm.tag)
            self.qwfman.wf_updated.emit(self.current_wfname())

    def load_op(self):
        """
        Package the finished Operation, put it in self.current_wf()
        """ 
        # Make sure all inputs are loaded
        for name in self.op.inputs.keys():
            self.set_input(name)
        tag = str(self.ui.tag_entry.text())
        if self.current_wf()._tree.is_tag_valid(tag):
            self.current_wf().set_item(tag,self.op)
            #import pdb; pdb.set_trace()
        else:
            # Request a different tag 
            msg_ui = uitools.message_ui(self.ui)
            msg_ui.setWindowTitle("Tag Error")
            msg_ui.message_box.setPlainText(self.current_wf()._tree.tag_error(tag))
            msg_ui.show()
        self.op = None
        self.clear_io()
        self.qwfman.wf_updated.emit(self.current_wfname())
        #replace_op_flag = self.current_wf().wf.contains_uri(tag)
        #if replace_op_flag: 
        #    self.current_wf().update_op(tag,self.op)
        #    self.op = None
        #else:
        #    self.current_wf().add_op(tag,self.op) 
        #    self.op = None
        #    self.clear_io()

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
        if src == op.no_input:
            il = op.InputLocator() 
        elif src == op.batch_input:
            if tp == op.auto_type:
                val = 'batch_input' 
            else:
                val = None
            il = op.InputLocator(src,tp,val) 
        else:
            # all other input sources use a ui for loading
            if ui:
                val = self.fetch_from_input_ui(ui) 
                il = op.InputLocator(src,tp,val)
                self.val_widgets[name].setText(str(il.val))
                ui.close()
                ui.deleteLater()
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
                    il = op.InputLocator(src,tp,val)
        return il

    def fetch_from_input_ui(self,ui):
        # no matter the input source, 
        # ui.values_list.model().list_data()
        # should be a list of strings.
        val = ui.values_list.model().list_data()
        # if ui.list_toggle is not checked,
        # the value should be unpacked. 
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
        input_loader_title = self.ui.tag_entry.text()+'.'+op.inputs_tag+'.'+name
        if src == op.wf_input:
            inp_loader = InputLoader(input_loader_title,src,self.qwfman,self.ui)
            inp_loader.ui.wf_selector.setCurrentIndex(self.ui.wf_selector.currentIndex())
            inp_loader.set_wf()
        elif src == op.fs_input:
            trmod = QtGui.QFileSystemModel()
            inp_loader = InputLoader(input_loader_title,src,trmod,self.ui)
        elif src == op.plugin_input:
            inp_loader = InputLoader(input_loader_title,src,self.qplugman,self.ui)
        elif src == op.text_input:
            inp_loader = InputLoader(input_loader_title,src,None,self.ui)
        if self.op.input_locator[name].src == src and self.op.input_locator[name].val is not None:
            if isinstance(self.op.input_locator[name].val,list):
                inp_loader.set_list_toggle()
                #for v in self.op.input_locator[name].val:
                inp_loader.add_values(self.op.input_locator[name].val)
            else:
                inp_loader.add_values([self.op.input_locator[name].val])
        inp_loader.ui.finish_button.clicked.connect( partial(self.set_input,name,inp_loader.ui) )
        self.input_loaders[name] = inp_loader
        #These do not need to be deleted on close. 
        #They will be deleted on clear_io() or when WfUiManager is closed.
        #inp_loader.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        inp_loader.ui.show()

    def clear_io(self):
        self.ui.op_name.setText('')
        self.ui.tag_entry.setText('')
        self.ui.load_button.setEnabled(False)
        # clean up internal objects via deleteLater()
        for nm,widg in (self.src_widgets.items()+self.type_widgets.items()
        +self.val_widgets.items()+self.btn_widgets.items()):
            if widg:
                widg.close()
                widg.deleteLater()
        for nm,il in self.input_loaders.items():
            if il:
                il.ui.close()
                il.ui.deleteLater()
        # dereference them to ensure they are collected
        self.src_widgets = {}
        self.type_widgets = {}
        self.val_widgets = {}
        self.btn_widgets = {}
        self.input_loaders = {}
        n_inp_widgets = self.ui.input_layout.count()
        for i in range(n_inp_widgets-1,-1,-1):
            item = self.ui.input_layout.takeAt(i)
            item.widget().close()
            item.widget().deleteLater()
        n_out_widgets = self.ui.output_layout.count()
        for i in range(n_out_widgets-1,-1,-1):
            item = self.ui.output_layout.takeAt(i)
            item.widget().close()
            item.widget().deleteLater()
    
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
                src = op.no_input 
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
        if not self.op.input_locator[name].src == op.no_input:
            if (self.op.input_locator[name].tp not in op.invalid_types[src]
            and self.op.input_locator[name].src == src):
                # load operation defaults
                new_type_widget.setCurrentIndex(self.op.input_locator[name].tp)
            else:
                # set sensible defaults
                if src == op.fs_input:
                    new_type_widget.setCurrentIndex(op.path_type)
                elif src in [op.wf_input,op.plugin_input]:
                    new_type_widget.setCurrentIndex(op.ref_type)
                elif src == op.batch_input:
                    new_type_widget.setCurrentIndex(op.auto_type)
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
        if src == op.no_input or tp == op.none_type: 
            btn_widget.setText('no input')
            btn_widget.setEnabled(False)
            val_widget.setText('None')
        elif src == op.batch_input:
            btn_widget.setText('auto')
            btn_widget.setEnabled(False)
            val_widget.setText('auto (batch)')
        elif src in [op.wf_input,op.fs_input,op.plugin_input,op.text_input]:
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
        # LABELS and STYLES
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )
        self.ui.setWindowTitle("workflow setup")
        self.ui.input_box.setTitle("INPUTS")
        self.ui.output_box.setTitle("OUTPUTS")
        self.ui.finish_box.setTitle("FINISH / LOAD")
        self.ui.wf_box.setTitle("WORKFLOWS")
        self.ui.op_box.setTitle("OPERATIONS")
        self.ui.tag_prompt.setText('operation tag:')
        self.ui.tag_prompt.setReadOnly(True)
        self.ui.op_name.setText('-select an operation to begin setup-')
        self.ui.op_name.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.tag_prompt.setAlignment(QtCore.Qt.AlignRight)
        self.ui.tag_prompt.setStyleSheet( "QLineEdit { background-color: transparent }" 
        + self.ui.tag_prompt.styleSheet() )
        self.ui.load_button.setText("&Finish")
        self.ui.rm_op_button.setText("&Remove selected operation")
        # SIGNALS, SLOTS, MODELS, VIEWS 
        lm = ListModel(self.qwfman.qworkflows.keys())
        self.ui.wf_selector.setModel(lm)
        self.ui.wf_selector.currentIndexChanged.connect(self.set_wf)
        #self.ui.wf_selector.currentIndexChanged.connect( partial(self.set_wf) )
        self.ui.wf_selector.activated.connect(self.set_wf)
        self.ui.wf_browser.clicked.connect( partial(self.get_op,None) )
        self.ui.rm_op_button.clicked.connect(self.remove_op)
        self.ui.op_selector.setModel(self.qopman)
        self.ui.op_selector.hideColumn(1)
        self.ui.op_selector.hideColumn(2)
        self.ui.op_selector.clicked.connect( partial(self.get_op,self.qopman) )
        self.ui.op_selector.clicked.connect( partial(uitools.toggle_expand,self.ui.op_selector) ) 
        self.ui.op_selector.setRootIndex(self.qopman.root_index())
        self.ui.load_button.clicked.connect(self.load_op)
        self.ui.load_button.setDefault(True)
        self.ui.load_button.setEnabled(False)
        # LAYOUT AND SIZING 
        szp = QtGui.QSizePolicy()
        szp.setHorizontalPolicy(QtGui.QSizePolicy.Preferred)
        szp.setVerticalPolicy(QtGui.QSizePolicy.Preferred)
        szp.setHorizontalStretch(3)
        szp.setVerticalStretch(1)
        self.ui.input_frame.setSizePolicy(szp)
        finish_box_szp = QtGui.QSizePolicy()
        finish_box_szp.setHorizontalPolicy(QtGui.QSizePolicy.Preferred)
        finish_box_szp.setVerticalPolicy(QtGui.QSizePolicy.Maximum)
        self.ui.finish_box.setSizePolicy(finish_box_szp)
        io_box_szp = QtGui.QSizePolicy()
        io_box_szp.setHorizontalPolicy(QtGui.QSizePolicy.Preferred)
        io_box_szp.setVerticalPolicy(QtGui.QSizePolicy.Maximum)
        self.ui.input_box.setSizePolicy(io_box_szp)
        self.ui.output_box.setSizePolicy(io_box_szp)
        self.ui.load_button.setMinimumWidth(100)
        self.ui.tag_prompt.setMaximumWidth(150)

