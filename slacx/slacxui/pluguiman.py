import importlib
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from ..slacxcore.listmodel import ListModel
from ..slacxcore import plugins as pgns 
from ..slacxcore import slacxtools
from ..slacxcore.plugins.slacxplug import SlacxPlugin

#import time
#import os

#import qdarkstyle
#import numpy as np

#from ..slacxcore.operations import optools
#from ..slacxcore.operations.slacxop import Operation 
#from ..slacxcore.workflow.slacxwfman import WfManager
#from ..slacxcore.operations.optools import InputLocator
#from . import uitools

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
        self.plugin_list_model = PluginListModel(pgns.plugin_list,self.ui)
        self.current_plugin = None
        self.setup_ui()
        #self.src_widgets = {} 
        #self.type_widgets = {} 
        #self.val_widgets = {} 
        #self.btn_widgets = {} 
        #self.inp_src_windows = {} 

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
        self.ui.rm_plugin_button.clicked.connect(self.remove_plugin)
        self.ui.rm_plugin_button.setText("&Stop selected plugin")
        self.ui.uri_prompt.setText('plugin uri:')
        self.ui.plugin_name.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.uri_prompt.setAlignment(QtCore.Qt.AlignRight)
        self.ui.uri_prompt.setStyleSheet( "QLineEdit { background-color: transparent }" 
        + self.ui.uri_prompt.styleSheet() )
        self.ui.load_button.setText("&Finish")
        self.ui.load_button.clicked.connect(self.load_plugin)
        #self.ui.splitter.setStretchFactor(0,1000)    
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )

    def remove_plugin(self):
        print 'remove plugin!'

    def start_plugin(self,idx):
        pkg = pgns.__name__
        pgin_name = self.plugin_list_model.get_item(idx)
        #print 'start plugin {} from package {}'.format(pgin_name,pkg)
        mod = importlib.import_module('.'+pgin_name,pkg)
        try:
            for nm, itm in mod.__dict__.items():
                #print 'try {}'.format(nm)
                if isinstance(itm,type):
                    if issubclass(itm,SlacxPlugin) and not nm == 'SlacxPlugin':
                        pgin = getattr(mod,nm)
                        #print 'starting module[{}] = {}'.format(nm,itm.__name__)
                        self.set_plugin(pgin())
                        return
        except:
            print 'failed to load plugin.'

    def set_plugin(self,pgin):
        self.current_plugin = pgin
        self.ui.plugin_info.setPlainText(self.current_plugin.description())
        self.ui.plugin_name.setText(type(self.current_plugin).__name__)
        self.build_input()
        self.ui.uri_entry.setText(self.plugman.auto_uri(type(self.current_plugin).__name__))
        self.ui.uri_entry.setReadOnly(False)
        
    def load_plugin(self):
        print 'load plugin {}'.format(self.current_plugin)        

    def clear_input(self):
        print 'clear input!'

    def reset_input_headers(self):
        print 'reset input headers!'

    def build_input(self):
        self.clear_input()
        self.reset_input_headers()
        #inp_count = len(self.current_plugin.inputs)
        #if inp_count:
        #    uitools.input_header_widgets(self.ui.input_layout,0)
        #    i=1
        #    for name in self.current_plugin.inputs.keys():
        #        uitools.input_widgets(name,i)
        #        i+=1



