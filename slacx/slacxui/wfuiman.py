import time
import os
from functools import partial

from PySide import QtCore, QtGui, QtUiTools
import qdarkstyle
import numpy as np

from ..slacxcore.listmodel import ListModel
from ..slacxcore.operations import optools
from ..slacxcore.operations.slacxop import Operation 
from ..slacxcore.workflow.slacxwfman import WfManager
from ..slacxcore import slacxtools
from ..slacxcore.operations.optools import InputLocator
from . import uitools

class WfUiManager(object):
    """
    Stores a reference to the op_builder QGroupBox, 
    performs operations on it
    """

    def __init__(self,wfman,opman):
        ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/wf_editor.ui")
        # Load the op_builder popup
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.wfman = wfman 
        self.opman = opman 
        self.op = None
        # Dicts to keep track of input widgets,
        # keyed by input variable names
        self.src_widgets = {} 
        self.type_widgets = {} 
        self.val_widgets = {} 
        self.btn_widgets = {} 
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
        self.op = op
        self.ui.op_info.setPlainText(self.op.description())
        self.ui.op_name.setText(type(self.op).__name__)
        self.ui.uri_entry.setText(uri)
        self.ui.uri_entry.setReadOnly(True)
        self.build_io()

    def create_op(self,op):
        """Instantiate op, call self.set_op(op), and enable uri entry"""
        new_op = op()
        new_op_tag = self.wfman.auto_tag(type(new_op).__name__)
        new_op.load_defaults()
        self.set_op(new_op,new_op_tag)
        self.ui.uri_entry.setReadOnly(False)

    #def test_op(self):
    #    print 'Operation testing not yet implemented'

    def set_input(self,name,src_ui=None,itm_idx=None):
        """
        Call load_input to package an InputLocator for named input. 
        Store it in self.op.input_locator[name].
        This is called on all inputs when an Operation is loaded,
        so leaving the optional arguments as None should not change an already-loaded input.
        This is also called as a signal from data fetching ui's,
        in which case both optional arguments are expected (see self.load_input).
        """
        il = self.load_input(name,src_ui,itm_idx)
        self.op.input_locator[name] = il

    def load_input(self,name,ui=None,itm_idx=None):
        """
        Create an InputLocator for named input.
        If a ui is provided, then this is being signalled to load data from that ui.
        The ui should have a view called ui.tree, where ui.tree.model() contains the data of interest.
        itm_idx is then used to index ui.tree.model() and fetch the desired data.
        """
        src = self.src_widgets[name].currentIndex()
        tp = self.type_widgets[name].currentIndex()
        if src == optools.no_input:
            il = optools.InputLocator() 
        elif src == optools.batch_input:
            val = 'auto' 
            il = optools.InputLocator(src,tp,val) 
        elif src == optools.user_input:
            if tp == optools.list_type:
                val = ui.list_builder.list_data() 
            else:
                val = self.val_widgets[name].text()
            il = optools.InputLocator(src,tp,val)
        elif (src == optools.wf_input or src == optools.fs_input or src == optools.plugin_input):
            if not ui:
                # If we get to this point without a data loading ui,
                # it has either already been loaded, or should be left as None.
                if self.op.input_locator[name] is not None:
                    il = self.op.input_locator[name]
                else:
                    #val = self.op.inputs[name]
                    #if not val: 
                    if tp == optools.list_type:
                        val = []
                    else:
                        val = None
                    il = optools.InputLocator(src,tp,val)
            elif tp == optools.list_type:
                val = ui.list_view.model().list_data() 
                il = optools.InputLocator(src,tp,val)
            else:
                il = self.load_from_ui(ui,src,itm_idx)
            if not il: 
                if self.op.input_locator[name] is not None:
                    il = self.op.input_locator[name]
                else: 
                    val = None
                    il = optools.InputLocator(src,tp,val)
        else: 
            il = optools.InputLocator()
        self.val_widgets[name].setText(str(il.val))
        if ui:
            ui.close()
            ui.deleteLater()
        return il

    def load_from_ui(self,src_ui,src,itm_idx=None):
        """
        Construct a unique resource identifier (uri) for the selected item.
        return an optools.InputLocator(src,tp,uri).
        By design this should only be called when the corresponding input source window
        (containing a TreeView widget) is open.
        """
        trview = src_ui.tree
        if not itm_idx or not itm_idx.isValid():
            itm_idx = trview.currentIndex()
        if itm_idx.isValid():
            if src == optools.fs_input:
                item_uri = trview.model().filePath(itm_idx)
            elif src == optools.wf_input or src == optools.plugin_input:
                item_uri = trview.model().build_uri(itm_idx)
            il = optools.InputLocator(src,optools.auto_type,item_uri)
        else:
            il = None
        return il

    def rm_op(self):
        """
        remove the selected operation from the workflow
        """
        idx = self.ui.wf_selector.currentIndex()
        if idx.isValid(): 
            while idx.internalPointer().parent.isValid():
                idx = idx.internalPointer().parent
            self.wfman.remove_op(idx)

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
        elif result[1] == 'Tag not unique':
            self.wfman.update_op(uri,self.op)
        else:
            # Request a different uri 
            msg_ui = uitools.message_ui(self.ui)
            msg_ui.setWindowTitle("Tag Error")
            msg_ui.message_box.setPlainText(self.wfman.tag_error(uri,result[1]))
            msg_ui.show()

    def clear_io(self):
        self.ui.op_name.setText('')
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
        if not src:
            src = self.src_widgets[name].currentIndex()
        widg = None 
        new_type_widget = uitools.type_selection_widget(src,widg)
        if src in [optools.wf_input,optools.fs_input,optools.plugin_input,optools.batch_input]:
            new_type_widget.setCurrentIndex(optools.auto_type)
        if new_type_widget.currentIndex() in optools.invalid_types[src]:
            new_type_widget.setCurrentIndex(optools.none_type)
        if self.op.input_locator[name]:
            if (self.op.input_locator[name].tp not in optools.invalid_types[src]
            and self.op.input_locator[name].src == src):
                new_type_widget.setCurrentIndex(self.op.input_locator[name].tp)
        #elif self.op.input_type[name]:
        #    if self.op.input_type[name] not in optools.invalid_types[src]:
        #        new_type_widget.setCurrentIndex(self.op.input_type[name])
        #new_type_widget.activated.connect( partial(reset_val_widget,name,row) )            
        new_type_widget.currentIndexChanged.connect( partial(self.reset_val_widget,name,row,src) )            
        self.type_widgets[name] = new_type_widget  
        self.ui.input_layout.addWidget(new_type_widget,row,self.type_col,1,1)
        tp = self.type_widgets[name].currentIndex()
        self.reset_val_widget(name,row,src,tp)

    def reset_val_widget(self,name,row,src=None,tp=None):
        if name in self.val_widgets.keys():
            if self.val_widgets[name]:
                self.val_widgets[name].close()
        if name in self.btn_widgets.keys():
            if self.btn_widgets[name]:
                self.btn_widgets[name].close()
        if not src:
            src = self.src_widgets[name].currentIndex()
        if not tp:
            tp = self.type_widgets[name].currentIndex()
        btn_widget = QtGui.QPushButton()
        val_widget = QtGui.QLineEdit()
        if src == optools.no_input or tp == optools.none_type: 
            btn_widget.setText('no input')
            btn_widget.setEnabled(False)
            val_widget.setText('None')
            val_widget.setReadOnly(True)
        elif src == optools.batch_input:
            btn_widget.setText('auto')
            btn_widget.setEnabled(False)
            val_widget.setText('auto (batch)')
            val_widget.setReadOnly(True)
        elif src == optools.wf_input or src == optools.fs_input or src == optools.plugin_input:
            if tp == optools.none_type:
                btn_widget.setText('no input')
                btn_widget.setEnabled(False)
                val_widget.setText('None')
                val_widget.setReadOnly(True)
            else:
                if tp == optools.list_type:
                    btn_widget.setText("build list...")
                    btn_widget.clicked.connect( partial(self.build_list,name) )
                else:
                    btn_widget.setText('browse...')
                    data_handler = partial(self.set_input,name)
                    btn_widget.clicked.connect( partial(self.fetch_data,name,data_handler) )
                if self.op.input_locator[name]:
                    if self.op.input_locator[name].src == src and self.op.input_locator[name].tp == tp:
                        val_widget.setText(str(self.op.input_locator[name].val))
            #elif self.op.inputs[name] is not None:
            #    val_widget.setText(str(self.op.inputs[name]))
            val_widget.setReadOnly(True)
        elif (src == optools.user_input):
            if tp == optools.none_type:
                btn_widget.setText('no input')
                btn_widget.setEnabled(False)
                val_widget.setText('None')
                val_widget.setReadOnly(True)
            else:
                if self.op.input_locator[name]:
                    if self.op.input_locator[name].src == src and self.op.input_locator[name].tp == tp:
                        val_widget.setText(str(self.op.input_locator[name].val))
                #elif self.op.inputs[name]:
                #    # this clause is for displaying default values- 
                #    # only executes when no input locator has been loaded yet
                #    val_widget.setText(str(self.op.inputs[name]))
                if tp == optools.list_type:
                    val_widget.setReadOnly(True)
                    btn_widget.setText("Build list...")
                    btn_widget.clicked.connect( partial(self.build_list,name) )
                else:
                    btn_widget = QtGui.QPushButton('auto')
                    #btn_widget.clicked.connect( partial(self.set_input,name) )
                    #btn_widget.clicked.connect( partial(self.set_input,name) )
                    btn_widget.setEnabled(False)
        self.ui.input_layout.addWidget(val_widget,row,self.val_col,1,1)
        self.ui.input_layout.addWidget(btn_widget,row,self.btn_col,1,1)
        self.val_widgets[name] = val_widget
        self.btn_widgets[name] = btn_widget

    def build_list(self,name):
        """Use a popup to build a list of input data"""
        #ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/list_builder.ui")
        #ui_file.open(QtCore.QFile.ReadOnly)
        #list_ui = QtUiTools.QUiLoader().load(ui_file)
        #ui_file.close()
        #print 'build_list: list view model is {}'.format(list_ui.list_view.model())
        src = self.src_widgets[name].currentIndex()
        list_ui = uitools.start_list_builder(src,ListModel(),self.ui)
        if self.op.input_locator[name]:
            if self.op.input_locator[name].src == src and self.op.input_locator[name].tp == optools.list_type:
                lm = ListModel(self.op.input_locator[name].val,list_ui)
        list_ui = uitools.start_list_builder(src,lm,self.ui)
        data_handler = partial(self.load_path_to_list,src,list_ui)
        list_ui.browse_button.clicked.connect( partial(self.fetch_data,name,data_handler) )
        list_ui.finish_button.clicked.connect( partial(self.set_input,name,list_ui) )
        list_ui.show()

    def load_path_to_list(self,src,list_ui,src_ui,idx=None):
        if not idx:
            idx = src_ui.tree.currentIndex()
        if idx.isValid():
            if src == optools.wf_input:
                val = self.wfman.build_uri(idx) 
            if src == optools.plugin_input:
                val = self.plugman.build_uri(idx) 
            elif src == optools.fs_input:
                val = src_ui.tree.model().filePath(idx) 
            list_ui.value_entry.setText( val )
            uitools.load_value_to_list(list_ui)
        src_ui.close()
        src_ui.deleteLater()

    def fetch_data(self,name,data_handler):
        """
        Use a popup to select the input data for named input.
        """
        src = self.src_widgets[name].currentIndex()
        src_ui = uitools.data_fetch_ui(self.ui)
        src_ui.setWindowTitle('data browser')
        src_ui.tree_box.setTitle(name+' - from '+optools.input_sources[src])
        if src == optools.wf_input:
            trmod = self.wfman
        elif src == optools.plugin_input:
            trmod = self.wfman.plugman
        elif src == optools.fs_input:
            trmod = QtGui.QFileSystemModel()
            trmod.setRootPath('.')
        src_ui.tree.setModel(trmod)
        src_ui.tree.clicked.connect( partial(uitools.toggle_expand,src_ui.tree) )
        src_ui.tree.expandAll()
        # add src_ui to the arguments of data_handler
        h = partial(data_handler,src_ui)
        # when the load button is clicked or tree is doubleclicked, call this augmented handler 
        src_ui.load_button.clicked.connect(h)
        src_ui.tree.doubleClicked.connect(h)
        if src == optools.fs_input:
            src_ui.tree.hideColumn(1)
            src_ui.tree.hideColumn(3)
            src_ui.tree.setColumnWidth(0,400)
        elif src == optools.wf_input or src == optools.plugin_input:
            src_ui.tree.hideColumn(1)
        src_ui.show()

    def setup_ui(self):
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
        #self.ui.test_button.setText("&Test")
        #self.ui.test_button.setEnabled(False)
        #self.ui.test_button.clicked.connect(self.test_op)
        self.ui.load_button.setText("&Finish")
        self.ui.load_button.clicked.connect(self.load_op)
        self.ui.load_button.setDefault(True)
        self.ui.load_button.setMinimumWidth(100)
        self.ui.splitter.setStretchFactor(0,1000)    
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )

