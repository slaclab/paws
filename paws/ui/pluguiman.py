import importlib
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from ..core.listmodel import ListModel
from ..core import plugins 
from ..core import pawstools
from ..core.plugins.plugin import PawsPlugin
from ..core.operations import optools
from .input_loader import InputLoader
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
        ui_file = QtCore.QFile(pawstools.rootdir+"/ui/qtui/plugin_control.ui")
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
        self.input_loaders = {} 
        self.name_col = 0
        self.eq_col = 1
        self.src_col = 2
        self.type_col = 3
        self.val_col = 4
        self.btn_col = 5
        self.invalid_sources = [optools.batch_input,optools.plugin_input,optools.wf_input]

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
        self.ui.load_button.setEnabled(False)
        #self.ui.splitter.setStretchFactor(0,1000)    
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )

    def start_plugin(self,idx):
        pkg = plugins.__name__
        pgin_name = self.plugin_list_model.get_item(idx)
        #print 'start plugin {} from package {}'.format(pgin_name,pkg)
        mod = importlib.import_module('.'+pgin_name,pkg)
        for nm, itm in mod.__dict__.items():
            if isinstance(itm,type):
                if issubclass(itm,PawsPlugin) and not nm == 'PawsPlugin':
                    pgin = getattr(mod,nm)
                    self.set_plugin(pgin())
                    return

    def set_plugin(self,pgin):
        self.pgin = pgin
        self.ui.plugin_info.setPlainText(self.pgin.description())
        self.build_input()
        self.ui.uri_entry.setText(self.plugman.auto_tag(type(self.pgin).__name__))
        
    def clear_input(self):
        self.ui.plugin_name.setText('')
        self.ui.uri_entry.setText('')
        self.ui.load_button.setEnabled(False)
        n_inp_widgets = self.ui.input_layout.count()
        for i in range(n_inp_widgets-1,-1,-1):
            item = self.ui.input_layout.takeAt(i)
            item.widget().close()
        self.src_widgets = {}
        self.type_widgets = {}
        self.val_widgets = {}
        self.btn_widgets = {}
        self.input_loaders = {}

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
        self.ui.load_button.setEnabled(True)
        for i,name in zip(range(1,len(self.pgin.inputs)+1),self.pgin.inputs.keys()):
            # name 
            name_widget = uitools.name_widget(name)
            self.ui.input_layout.addWidget( name_widget,i,self.name_col,1,1 )
            # '=' 
            eq_widget = uitools.smalltext_widget('=')
            self.ui.input_layout.addWidget(eq_widget,i,self.eq_col,1,1)
            # source 
            src_widget = uitools.src_selection_widget()
            for s in self.invalid_sources:
                src_widget.model().set_disabled(s)
            src = self.pgin.input_src[name]
            if src in self.invalid_sources:
                src = optools.no_input
            src_widget.setCurrentIndex(src)
            self.ui.input_layout.addWidget( src_widget,i,self.src_col,1,1 )
            self.src_widgets[name] = src_widget 
            self.src_widgets[name].currentIndexChanged.connect( partial(self.reset_type_widget,name,i) )
            # type 
            self.reset_type_widget(name,i,src)
            #tp = self.type_widgets[name].currentIndex()
            # val 
            #self.reset_val_widget(name,i,src,tp)

    def reset_type_widget(self,name,row,src=None):
        if name in self.type_widgets.keys():
            if self.type_widgets[name]:
                self.type_widgets[name].close()
        if not src:
            src = self.src_widgets[name].currentIndex()
        type_widget = uitools.type_selection_widget(src)
        if self.pgin.input_type[name]:
            if self.pgin.input_type[name] not in optools.invalid_types[src]:
                type_widget.setCurrentIndex(self.pgin.input_type[name])
            else:
                # set sensible defaults
                if src == optools.fs_input:
                    new_type_widget.setCurrentIndex(optools.path_type)
                elif src == optools.text_input:
                    new_type_widget.setCurrentIndex(optools.str_type)
        #if type_widget.currentIndex() in optools.invalid_types[src]:
        #    type_widget.setCurrentIndex(optools.none_type)
        #if src in [optools.wf_input,optools.plugin_input]:
        #    type_widget.setCurrentIndex(optools.ref_type)
        #if src == optools.fs_input:
        #    type_widget.setCurrentIndex(optools.path_type)
        type_widget.currentIndexChanged.connect( partial(self.reset_val_widget,name,row,src) )            
        self.type_widgets[name] = type_widget  
        self.ui.input_layout.addWidget(type_widget,row,self.type_col,1,1)
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
        if src == optools.no_input or tp == optools.none_type: 
            btn_widget.setText('no input')
            btn_widget.setEnabled(False)
            val_widget.setText('None')
        #elif src in [optools.wf_input,optools.fs_input,optools.plugin_input,optools.text_input]:
        elif src in [optools.fs_input,optools.text_input]:
            btn_widget.setText('edit...')
            btn_widget.clicked.connect( partial(self.fetch_data,name) )
            if self.pgin.inputs[name] is not None:
                val_widget.setText(str(self.pgin.inputs[name]))
        val_widget.setReadOnly(True)
        self.ui.input_layout.addWidget(val_widget,row,self.val_col,1,1)
        self.ui.input_layout.addWidget(btn_widget,row,self.btn_col,1,1)
        self.val_widgets[name] = val_widget
        self.btn_widgets[name] = btn_widget
       
    def fetch_data(self,name):
        if name in self.input_loaders.keys():
            if self.input_loaders[name]:
                self.input_loaders[name].ui.close()
                self.input_loaders[name] = None
        src = self.src_widgets[name].currentIndex()
        if src == optools.fs_input:
            trmod = QtGui.QFileSystemModel()
            trmod.setRootPath(QtCore.QDir.currentPath())
            inp_loader = InputLoader(name,src,trmod,self.ui)
        elif src == optools.text_input:
            inp_loader = InputLoader(name,src,None,self.ui)
        if self.pgin.input_src[name] == src and self.pgin.inputs[name] is not None:
            if isinstance(self.pgin.inputs[name],list):
                inp_loader.set_list_toggle()
                for v in self.pgin.inputs[name]:
                    inp_loader.add_value(str(v))
            else:
                inp_loader.add_value(str(self.pgin.inputs[name]))
        inp_loader.ui.finish_button.clicked.connect( partial(self.set_input,name,inp_loader.ui) )
        self.input_loaders[name] = inp_loader

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

    def set_input(self,name,src_ui=None):
        src = self.src_widgets[name].currentIndex()
        tp = self.type_widgets[name].currentIndex()
        if src_ui:
            val = self.fetch_from_input_ui(src_ui) 
            self.pgin.inputs[name] = val 
            self.val_widgets[name].setText(val)
            src_ui.close()
            # dereference the ui now that it is closed...
            self.input_loaders[name] = None
            #src_ui.deleteLater()
        elif src == optools.text_input:
            val = self.val_widgets[name].text()
            self.pgin.inputs[name] = optools.cast_type_val(tp,val)

    def load_plugin(self):
        """
        Package the finished Plugin, ship to self.plugman
        """ 
        for name in self.pgin.inputs.keys():
            self.set_input(name)
        uri = self.ui.uri_entry.text()
        # Plugin setup occurs here via PawsPlugin.start()
        self.pgin.start()
        result = self.plugman.is_good_tag(uri)
        if result[0]:
            self.plugman.add_plugin(uri,self.pgin) 
            self.clear_input()
            #self.ui.close()
            #self.ui.deleteLater()
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


