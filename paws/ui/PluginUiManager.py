import importlib
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from ..core.models.ListModel import PluginListModel
from ..core import plugins 
from ..core import pawstools
from ..core.plugins.PawsPlugin import PawsPlugin
from ..core.operations import Operation as op
from ..core.operations import optools
from .InputLoader import InputLoader
from . import uitools

class PluginUiManager(QtCore.QObject):
    # TODO: API cleanup: hide refs to self.qplugman.plugman._tree

    def __init__(self,qplugman):
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/plugin_control.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        # set self.ui to be deleted and to emit destroyed() signal when its window is closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.qplugman = qplugman 
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
        self.invalid_sources = [op.batch_input,op.plugin_input,op.wf_input]

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
        self.ui.plugins_loaded.setModel(self.qplugman)
        self.ui.plugins_loaded.hideColumn(1)
        self.ui.plugins_loaded.hideColumn(2)
        self.ui.plugins_loaded.setRootIndex(self.qplugman.root_index())
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
        # TODO: clean up the following
        self.ui.uri_entry.setText(
        self.qplugman.plugman._tree.make_unique_uri(type(self.pgin).__name__))
        
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
                src = op.no_input
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
            if self.pgin.input_type[name] not in op.invalid_types[src]:
                type_widget.setCurrentIndex(self.pgin.input_type[name])
            else:
                # set sensible defaults
                if src == op.fs_input:
                    new_type_widget.setCurrentIndex(op.path_type)
                elif src == op.text_input:
                    new_type_widget.setCurrentIndex(op.str_type)
        #if type_widget.currentIndex() in op.invalid_types[src]:
        #    type_widget.setCurrentIndex(op.none_type)
        #if src in [op.wf_input,op.plugin_input]:
        #    type_widget.setCurrentIndex(op.ref_type)
        #if src == op.fs_input:
        #    type_widget.setCurrentIndex(op.path_type)
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
        if src == op.no_input or tp == op.none_type: 
            btn_widget.setText('no input')
            btn_widget.setEnabled(False)
            val_widget.setText('None')
        #elif src in [op.wf_input,op.fs_input,op.plugin_input,op.text_input]:
        elif src in [op.fs_input,op.text_input]:
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
        if src == op.fs_input:
            trmod = QtGui.QFileSystemModel()
            inp_loader = InputLoader(name,src,trmod,self.ui)
        elif src == op.text_input:
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
        inp_loader.ui.show()

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
        elif src == op.text_input:
            val = self.val_widgets[name].text()
            self.pgin.inputs[name] = optools.cast_type_val(tp,val)

    def load_plugin(self):
        """
        Package the finished Plugin, ship to plugin manager
        """ 
        for name in self.pgin.inputs.keys():
            self.set_input(name)
        uri = self.ui.uri_entry.text()
        # Plugin setup occurs here via PawsPlugin.start()
        self.pgin.start()
        if self.qplugman.plugman.is_uri_valid(uri):
            self.qplugman.add_plugin(uri,self.pgin) 
            self.clear_input()
        else:
            # Request a different uri 
            msg_ui = uitools.message_ui(self.ui)
            msg_ui.setWindowTitle("Tag Error")
            msg_ui.message_box.setPlainText(
            self.qplugman.plugman._tree.tag_error(uri))
            msg_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            msg_ui.show()

    def stop_plugin(self,idx=QtCore.QModelIndex()):
        """
        remove the selected plugin from self.plugman 
        """
        if not idx.isValid():
            idx = self.ui.plugins_loaded.currentIndex()
        if idx.isValid(): 
            while idx.internalPointer().parent.isValid():
                idx = idx.internalPointer().parent
            pgin_tag = self.qplugman.get_uri_of_index(idx)
            self.qplugman.remove_plugin(pgin_tag)


