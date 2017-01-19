import importlib
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from ..slacxcore.listmodel import ListModel
from ..slacxcore import plugins 
from ..slacxcore import slacxtools
from ..slacxcore.plugins.slacxplug import SlacxPlugin
from ..slacxcore.operations import optools
from . import uitools

class PluginListModel(ListModel):
    """Just a ListModel with overloaded headerData"""

    def __init__(self,input_list=[],parent=None):
        super(PluginListModel,self).__init__(input_list,parent)

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} plugin(s) available".format(self.rowCount(QtCore.QModelIndex()))
        else:
            return None

class PluginUiManager(object):

    def __init__(self,plugman):
        ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/plugin_control.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.plugman = plugman 
        self.plugin_list_model = PluginListModel(plugins.plugin_name_list,self.ui)
        self.pgin = None
        self.setup_ui()
        self.src_widgets = {} 
        self.type_widgets = {} 
        self.val_widgets = {} 
        self.btn_widgets = {} 
        self.name_col = 0
        self.eq_col = 1
        self.src_col = 2
        self.type_col = 3
        self.val_col = 4
        self.btn_col = 5

    def setup_ui(self):
        self.ui.setWindowTitle("plugin setup")
        self.ui.input_box.setTitle("SETUP")
        self.ui.finish_box.setTitle("FINISH / LOAD")
        ht = self.ui.plugin_frame.sizeHint().height()
        self.ui.plugin_frame.sizeHint = lambda: QtCore.QSize(300,ht)
        self.ui.plugin_frame.setSizePolicy(
        QtGui.QSizePolicy.Minimum,self.ui.plugin_frame.sizePolicy().verticalPolicy())
        self.ui.plugins_available.clicked.connect( partial(self.start_plugin) )
        self.ui.plugins_available.setModel(self.plugin_list_model)
        self.ui.plugins_loaded.setModel(self.plugman)
        self.ui.stop_plugin_button.clicked.connect(self.stop_plugin)
        self.ui.stop_plugin_button.setText("&Stop selected plugin")
        self.ui.uri_prompt.setMaximumWidth(150)
        self.ui.uri_prompt.setText('plugin tag:')
        self.ui.plugin_name.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.plugin_name.setText('-select a plugin to begin setup-')
        self.ui.uri_prompt.setAlignment(QtCore.Qt.AlignRight)
        self.ui.uri_prompt.setStyleSheet( "QLineEdit { background-color: transparent }" 
        + self.ui.uri_prompt.styleSheet() )
        self.ui.load_button.setText("&Finish")
        self.ui.load_button.setMinimumWidth(100)
        self.ui.load_button.clicked.connect(self.load_plugin)
        #self.ui.splitter.setStretchFactor(0,1000)    
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )

    def start_plugin(self,idx):
        pkg = plugins.__name__
        pgin_name = self.plugin_list_model.get_item(idx)
        #print 'start plugin {} from package {}'.format(pgin_name,pkg)
        mod = importlib.import_module('.'+pgin_name,pkg)
        for nm, itm in mod.__dict__.items():
            if isinstance(itm,type):
                if issubclass(itm,SlacxPlugin) and not nm == 'SlacxPlugin':
                    pgin = getattr(mod,nm)
                    self.set_plugin(pgin())
                    return

    def set_plugin(self,pgin):
        self.pgin = pgin
        self.ui.plugin_info.setPlainText(self.pgin.description())
        self.build_input()
        self.ui.uri_entry.setText(self.plugman.auto_tag(type(self.pgin).__name__))
        self.ui.uri_entry.setReadOnly(False)
        
    def clear_input(self):
        self.ui.plugin_name.setText('')
        n_inp_widgets = self.ui.input_layout.count()
        for i in range(n_inp_widgets-1,-1,-1):
            item = self.ui.input_layout.takeAt(i)
            item.widget().close()

    def reset_input_headers(self):
        if len(self.pgin.inputs) > 0:
            self.ui.input_layout.addWidget(uitools.r_hdr_widget('name'),0,self.name_col,1,1)
            self.ui.input_layout.addWidget(uitools.hdr_widget('source'),0,self.src_col,1,1)
            self.ui.input_layout.addWidget(uitools.hdr_widget('type'),0,self.type_col,1,1)
            self.ui.input_layout.addWidget(uitools.hdr_widget('value'),0,self.val_col,1,1)

    def build_input(self):
        self.clear_input()
        self.reset_input_headers()
        self.ui.plugin_name.setText(type(self.pgin).__name__)
        for i,name in zip(range(1,len(self.pgin.inputs)+1),self.pgin.inputs.keys()):
            # name 
            name_widget = uitools.name_widget(name)
            self.ui.input_layout.addWidget( name_widget,i,self.name_col,1,1 )
            # '=' 
            eq_widget = uitools.smalltext_widget('=')
            self.ui.input_layout.addWidget(eq_widget,i,self.eq_col,1,1)
            # source 
            src_widget = uitools.src_selection_widget()
            src = self.pgin.input_src[name]
            src_widget.setCurrentIndex(src)
            self.ui.input_layout.addWidget( src_widget,i,self.src_col,1,1 )
            self.src_widgets[name] = src_widget 
            self.src_widgets[name].currentIndexChanged.connect( partial(self.reset_type_widget,name,i) )
            # type 
            self.reset_type_widget(name,i,src)
            tp = self.type_widgets[name].currentIndex()
            # val 
            self.reset_val_widget(name,i,src,tp)

    def reset_type_widget(self,name,row,src):
        if name in self.type_widgets.keys():
            if self.type_widgets[name]:
                self.type_widgets[name].close()
        type_widget = uitools.type_selection_widget(src)
        type_widget.model().set_disabled(optools.list_type)
        if type_widget.currentIndex() in optools.invalid_types[src]:
            type_widget.setCurrentIndex(optools.none_type)
        if self.pgin.input_type[name]:
            if self.pgin.input_type[name] not in optools.invalid_types[src]:
                type_widget.setCurrentIndex(self.pgin.input_type[name])
        if src in [optools.wf_input,optools.fs_input,optools.plugin_input]:
            type_widget.setCurrentIndex(optools.auto_type)
        type_widget.currentIndexChanged.connect( partial(self.reset_val_widget,name,row,src) )            
        self.type_widgets[name] = type_widget  
        self.ui.input_layout.addWidget(type_widget,row,self.type_col,1,1)
       
    def reset_val_widget(self,name,row,src,tp):
        if name in self.val_widgets.keys():
            if self.val_widgets[name]:
                self.val_widgets[name].close()
        if name in self.btn_widgets.keys():
            if self.btn_widgets[name]:
                self.btn_widgets[name].close()
        btn_widget = QtGui.QPushButton()
        val_widget = QtGui.QLineEdit()
        if src == optools.no_input or tp == optools.none_type: 
            btn_widget.setText('no input')
            btn_widget.setEnabled(False)
            val_widget.setText('None')
            val_widget.setReadOnly(True)
        elif src in [optools.plugin_input,optools.wf_input,optools.fs_input]:
            btn_widget.setText('browse...')
            data_handler = partial(self.set_input,name)
            btn_widget.clicked.connect( partial(self.fetch_data,name,data_handler) )
            if self.pgin.inputs[name] is not None:
                val_widget.setText(str(self.pgin.inputs[name]))
            val_widget.setReadOnly(True)
        elif (src == optools.user_input):
            if self.pgin.inputs[name]:
                val_widget.setText(str(self.pgin.inputs[name]))
            btn_widget = QtGui.QPushButton('auto')
            #btn_widget.clicked.connect( partial(self.load_input,name) )
            btn_widget.setEnabled(False)
        self.ui.input_layout.addWidget(val_widget,row,self.val_col,1,1)
        self.ui.input_layout.addWidget(btn_widget,row,self.btn_col,1,1)
        self.val_widgets[name] = val_widget
        self.btn_widgets[name] = btn_widget

    def load_input(self,name,ui=None,itm_idx=None):
        src = self.src_widgets[name].currentIndex()
        tp = self.type_widgets[name].currentIndex()
        #if src == optools.no_input:
        #    il = optools.InputLocator() 
        #elif src == optools.batch_input:
        #    val = 'auto' 
        #    il = optools.InputLocator(src,tp,val) 
        if src == optools.user_input:
            val = self.val_widgets[name].text()
        elif src in [optools.wf_input,optools.fs_input,optools.plugin_input]:
            if ui:
                val = self.load_from_ui(ui,src,itm_idx)
            else:
                val = self.pgin.inputs[name]
        self.val_widgets[name].setText(str(val))
        if ui:
            ui.close()
            ui.deleteLater()

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
                item_uri = trview.model().filePath(item_indx)
            elif src == optools.wf_input or src == optools.plugin_input:
                item_uri = trview.model().build_uri(itm_idx)

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
            trmod = self.plugman
        elif src == optools.fs_input:
            trmod = QtGui.QFileSystemModel()
            trmod.setRootPath('.')
        src_ui.tree.setModel(trmod)
        src_ui.tree.expandAll()
        src_ui.tree.clicked.connect( partial(uitools.toggle_expand,src_ui.tree) )
        # add src_ui to the arguments of data_handler
        h = partial(data_handler,src_ui)
        # when the load button is clicked or tree is doubleclicked, call data_handler
        src_ui.load_button.clicked.connect(h)
        src_ui.tree.doubleClicked.connect(h)
        if src == optools.fs_input:
            src_ui.tree.hideColumn(1)
            src_ui.tree.hideColumn(3)
            src_ui.tree.setColumnWidth(0,400)
        elif src == optools.wf_input or src == optools.plugin_input:
            src_ui.tree.hideColumn(1)
        src_ui.show()

    def set_input(self,name,src_ui=None,itm_idx=None):
        src = self.src_widgets[name].currentIndex()
        tp = self.type_widgets[name].currentIndex()
        if src_ui:
            trview = src_ui.tree
            if not itm_idx or not itm_idx.isValid():
                itm_idx = trview.currentIndex()
            if itm_idx.isValid():
                if src == optools.fs_input:
                    val = trview.model().filePath(itm_idx)
                elif src == optools.wf_input or src == optools.plugin_input:
                    val = trview.model().build_uri(itm_idx)
            self.pgin.inputs[name] = val 
            self.val_widgets[name].setText(val)
            src_ui.close()
            src_ui.deleteLater()
        elif src == optools.user_input:
            val = self.val_widgets[name].text()
            self.pgin.inputs[name] = optools.cast_type_val(tp,val)

    def load_plugin(self):
        """
        Package the finished Plugin, ship to self.plugman
        """ 
        for name in self.pgin.inputs.keys():
            self.set_input(name)
        uri = self.ui.uri_entry.text()
        # Plugin setup occurs here via SlacxPlugin.start()
        self.pgin.start()
        result = self.plugman.is_good_tag(uri)
        if result[0]:
            self.plugman.add_plugin(uri,self.pgin) 
        else:
            # Request a different uri 
            msg_ui = uitools.message_ui(self.ui)
            msg_ui.setWindowTitle("Tag Error")
            msg_ui.message_box.setPlainText(self.plugman.tag_error(uri,result[1]))
            msg_ui.show()

    def stop_plugin(self):
        """
        remove the selected plugin from self.plugman 
        """
        idx = self.ui.plugins_loaded.currentIndex()
        if idx.isValid(): 
            while idx.internalPointer().parent.isValid():
                idx = idx.internalPointer().parent
            self.plugman.remove_plugin(idx)


