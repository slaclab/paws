import os
from functools import partial
from collections import OrderedDict

from PySide import QtGui, QtCore, QtUiTools
import yaml

from ..core.operations.Operation import Operation
from . import uitools
from . import widgets 
from ..core import pawstools
from .WfUiManager import WfUiManager
from .OpUiManager import OpUiManager
from .PluginUiManager import PluginUiManager
from ..core.models.ListModel import ListModel
from ..core.plugins.WfManagerPlugin import WfManagerPlugin
from ..qt.QWfManager import QWfManager
from ..qt.QOpManager import QOpManager
from ..qt.QPluginManager import QPluginManager

class UiManager(QtCore.QObject):
    """
    Stores a reference to a QMainWindow,
    performs operations on it
    """

    def __init__(self,paws_api,app):
        super(UiManager,self).__init__()
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/basic.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        paws_api.logmethod = self.msg_board_log
        paws_api._op_manager.logmethod = self.msg_board_log
        paws_api._wf_manager.logmethod = self.msg_board_log
        paws_api._plugin_manager.logmethod = self.msg_board_log
        self.qplugman = QPluginManager(paws_api._plugin_manager)
        self.qopman = QOpManager(paws_api._op_manager)
        self.qwfman = QWfManager(paws_api._wf_manager,app)
        self.paw = paws_api
        self.make_title()
        self.build()
        self.add_wf('new_workflow')

    @QtCore.Slot(str)
    def update_wfman_plugin(self,wfname):
        self.qplugman.update_plugin('wf_manager')

    #requestStopWorkflow = QtCore.Signal(str)
    #requestRunWorkflow = QtCore.Signal(str)

    def msg_board_log(self,msg):
        """Print timestamped message to msg board"""
        if (self.ui.message_board.verticalScrollBar().value() == 
        self.ui.message_board.verticalScrollBar().maximum()):
            advance_scrollbar = True
        else:
            advance_scrollbar = False
        self.ui.message_board.appendPlainText(
        '- ' + pawstools.timestr() + ': ' + msg)#+ '\n') 
        if advance_scrollbar:
            self.ui.message_board.verticalScrollBar().setValue(
            self.ui.message_board.verticalScrollBar().maximum())

    def make_title(self):
        """Display the paws logo in the image viewer"""
        img_file = os.path.join(pawstools.sourcedir, "ui/graphics/paws_icon_white.png")
        pixmap = QtGui.QPixmap(img_file)
        pixmap_item = QtGui.QGraphicsPixmapItem(pixmap)
        scene = QtGui.QGraphicsScene()
        scene.addItem(pixmap_item)
        qwhite = QtGui.QColor(255,255,255,255)
        textitem = scene.addText("v{}".format(pawstools.version))
        textitem.setPos(100,35)
        textitem.setDefaultTextColor(qwhite)
        logo_view = QtGui.QGraphicsView()
        logo_view.setScene(scene)
        self.ui.viewer_layout.addWidget(logo_view,0,0,1,1)
        self.ui.setWindowTitle("paws v{}".format(pawstools.version))
        self.ui.setWindowIcon(pixmap)

    def build(self):
        """
        Set up QObjects and model views 
        for communicating with paws objects 
        """
        self.qwfman.wf_updated.connect( partial(self.update_wfman_plugin) )
        self.qwfman.wfdone.connect(self.update_run_wf_button)
        #self.requestRunWorkflow.connect(self.qwfman.runWorkflow)
        #self.requestStopWorkflow.connect(self.qwfman.stopWorkflow)
        self.ui.workflows_box.setTitle('Workflows')
        self.ui.plugins_box.setTitle('Plugins')
        lm = ListModel(self.qwfman.qworkflows.keys())
        self.ui.wf_selector.setModel(lm)
        self.ui.wf_selector.currentIndexChanged.connect( partial(self.set_wf) )
        #self.ui.add_wf_button.clicked.connect( partial(self.add_wf,'new_workflow') )
        self.ui.plugin_tree.setModel(self.qplugman)
        self.ui.op_tree.setModel(self.qopman)
        #self.ui.op_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.op_tree) ) 
        self.ui.op_tree.setRootIndex(self.qopman.root_index())
        #self.ui.wf_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.wf_tree) )
        self.ui.op_tree.clicked.connect( self.display_op_item )
        self.ui.wf_tree.clicked.connect( self.display_wf_item )
        #self.ui.wf_tree.doubleClicked.connect( partial(self.edit_wf) )
        self.ui.plugin_tree.clicked.connect( self.display_plugin_item )
        self.ui.plugin_tree.setRootIndex(self.qplugman.root_index())
        self.ui.run_wf_button.setText("&Run")
        self.ui.run_wf_button.clicked.connect(self.toggle_run_wf)
        #self.ui.edit_ops_button.setText("Edit operations")
        #self.ui.edit_ops_button.clicked.connect(self.edit_ops)
        #self.ui.add_wf_button.setText("&New workflow")
        self.ui.setup_wf_button.setText("&Workflow setup...")
        self.ui.setup_wf_button.clicked.connect(self.edit_wf)
        self.ui.save_state_button.setText("&Save")
        self.ui.save_state_button.clicked.connect(self.save_state)
        self.ui.load_state_button.setText("&Load")
        self.ui.load_state_button.clicked.connect(self.load_state)
        #self.ui.save_plugins_button.setText("Save plugins")
        #self.ui.save_plugins_button.clicked.connect(self.save_plugins)
        #self.ui.load_plugins_button.setText("Load plugins")
        #self.ui.load_plugins_button.clicked.connect(self.load_plugins)
        self.ui.setup_plugins_button.setText("Plugin setup...")
        self.ui.setup_plugins_button.clicked.connect(self.start_plugins_ui)
        self.ui.message_board.setReadOnly(True)
        self.ui.message_board.insertPlainText('--- MESSAGE BOARD ---') 
        self.msg_board_log('paws is ready') 
        #self.ui.op_tree.hideColumn(1)
        #self.ui.op_tree.hideColumn(2)
        self.ui.op_tree.setColumnWidth(0,200)
        self.ui.plugin_tree.hideColumn(1)
        self.ui.plugin_tree.hideColumn(2)
        self.ui.hsplitter.setStretchFactor(0,2)    
        self.ui.hsplitter.setStretchFactor(1,3)    
        self.ui.hsplitter.setStretchFactor(2,2)    
        self.ui.vsplitter.setStretchFactor(0,1)    

    def set_wf(self,wf_selector_idx):
        wfname = self.ui.wf_selector.model().list_data()[wf_selector_idx]
        self.paw.select_wf(wfname)
        self.ui.wf_tree.setModel(self.qwfman.qworkflows[wfname])
        self.ui.wf_tree.setRootIndex(self.qwfman.qworkflows[wfname].root_index())
        self.update_run_wf_button()

    def add_wf(self,wfname):
        #if wfname in self.wfman.workflows.keys():
        #    wfname = self.wfman.auto_name(wfname)
        if wfname in self.qwfman.qworkflows.keys():
            raise KeyError('[{}] Name {} already assigned to a Workflow. '
            .format(__name__,wfname) + 'Loaded workflows: {}'
            .format(self.qwfman.qworkflows.keys()))
        self.qwfman.add_wf(wfname)
        self.ui.wf_selector.model().append_item(wfname)
        # if this is the first workflow loaded, need to hide the treeview columns.
        if self.qwfman.n_wf() == 1:
            self.ui.wf_tree.hideColumn(1)
            self.ui.wf_tree.hideColumn(2)
        self.ui.wf_selector.setCurrentIndex(self.qwfman.n_wf()-1)

    def display_op_item(self,idx):
        """
        Display selected item from the op tree in viewer layout 
        """
        if idx.isValid(): 
            # If the user is clicking a check box (idx.column()!=0),
            # leave the central display unchanged... ?
            #if idx.column() == 0:
                itm_data = self.qopman.get_data_from_index(idx)
                itm_uri = self.qopman.get_uri_of_index(idx)
                op_widg = None
                if itm_data is None:
                    # this should be the condition for a not-enabled Operation
                    t = str('selected Operation: {} \n'.format(itm_uri)
                    + 'This Operation is not currently enabled. '
                    + 'Click the "enable" box to enable it. ')
                elif isinstance(itm_data,dict):
                    # this should be the condition for a category
                    t = str('selected category: {} \n\n'.format(itm_uri)
                    + '{}: '.format(itm_uri)) 
                    t = t + self.qopman.opman.print_cat(itm_uri) 
                else:
                    # the only remaining case is an enabled Operation
                    op = itm_data()
                    t = op.description()
                    op_widg = widgets.make_widget(op)
                    self.display_widget(op_widg)
                w = QtGui.QTextEdit()
                w.setText(t)
                self.ui.op_info_box.setText(t)
                self.display_widget(op_widg)

    def display_plugin_item(self,idx):
        """
        Display selected item from the plugin tree in viewer layout 
        """
        if idx.isValid(): 
            itm_data = self.qplugman.get_data_from_index(idx)
            widg = widgets.make_widget(itm_data)
            self.display_widget(widg)

    def display_wf_item(self,idx):
        """
        Display selected item from the workflow tree in viewer layout 
        """
        if idx.isValid(): 
            itm_data = self.current_wf().get_data_from_index(idx)
            widg = widgets.make_widget(itm_data)
            self.display_widget(widg)

    def display_widget(self,widg=None):
        # Loop through the viewer layout, last to first, clear the frame
        n_widgets = self.ui.viewer_layout.count()
        for i in range(n_widgets-1,-1,-1):
            # QLayout.takeAt returns a LayoutItem
            itm = self.ui.viewer_layout.takeAt(i)
            # get the QWidget of that LayoutItem and close it 
            itm.widget().close()
            #if itm.widget() is not None:
            #    itm.widget().deleteLater()
        if widg is not None:
            self.ui.viewer_layout.addWidget(widg,0,0,1,1) 

    def current_wf(self):
        wfname = self.current_wfname()
        if wfname:
            return self.qwfman.qworkflows[wfname]

    def current_wfname(self):
        idx = self.ui.wf_selector.currentIndex()
        if idx == -1:
            return None
        else:
            return self.ui.wf_selector.model().list_data()[idx]

    def toggle_run_wf(self,wfname=None):
        if wfname:
            qwf = self.qwfman.qworkflows[wfname]
        else:
            wfname = self.current_wfname()
            qwf = self.qwfman.qworkflows[wfname]
        if self.qwfman.wf_running[wfname]: 
            self.qwfman.stop_wf(wfname)
            self.ui.run_wf_button.setText("&Run")
            #self.requestStopWorkflow.emit(wfname)
        else:
            self.ui.run_wf_button.setText("S&top")
            self.qwfman.run_wf(wfname)
        #self.update_run_wf_button()

    def update_run_wf_button(self):
        wfname = self.current_wfname() 
        if self.qwfman.wf_running[wfname]:
            self.ui.run_wf_button.setText("S&top")
        else:
            self.ui.run_wf_button.setText("&Run")

    def edit_wf(self,itm_idx=QtCore.QModelIndex()):
        """
        Interact with user to edit the workflow.
        Pass in QModelIndex to open the editor 
        with the item at that index loaded.
        """
        wf = self.current_wf()
        #if wf is None:
        #    self.add_wf('new_workflow')
        #    wf = self.current_wf()
        if itm_idx.isValid():
            # valid index in workflow tree: percolate up to root ancestor
            while itm_idx.parent().isValid():
                itm_idx = itm_idx.parent()
        if itm_idx.isValid():
            uiman = self.start_wf_editor(wf,itm_idx)
        else:
            uiman = self.start_wf_editor(wf)
        uiman.ui.show()

    def start_wf_editor(self,qwf=None,idx=QtCore.QModelIndex()):
        """
        Create a WfUiManager (QMainWindow), return it 
        """
        uiman = WfUiManager(self.qwfman,self.qopman,self.qplugman)
        uiman.ui.wf_selector.setCurrentIndex(self.ui.wf_selector.currentIndex())
        #uiman.set_wf()
        if qwf and idx.isValid():
            uiman.get_op(qwf,idx)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        return uiman

    #def edit_ops(self,itm_idx=None):
    #    """
    #    interact with user to enable existing Operations
    #    and edit or develop new Operations 
    #    """
    #    uiman = OpUiManager(self.qopman)
    #    uiman.ui.setParent(self.ui,QtCore.Qt.Window)
    #    uiman.ui.show()

    def start_plugins_ui(self):
        uiman = PluginUiManager(self.qplugman)
        uiman.ui.setParent(self.ui,QtCore.Qt.Window)
        uiman.ui.show()

    #def save_plugins(self):
    #    """
    #    Start a modal window dialog to choose a .wfl to save the current set of plugins  
    #    """
    #    save_ui = uitools.start_save_ui(self.ui)
    #    save_ui.setWindowTitle('plugins saver')
    #    save_ui.tree_box.setTitle('Select or enter a .wfl file to save current plugins')
    #    save_ui.save_button.clicked.connect( partial(self.finish_save_plugins,save_ui) )
    #    save_ui.show()
    #    save_ui.activateWindow()

    #def load_plugins(self):
    #    """
    #    Start a modal window dialog to choose a .wfl to load a set of plugins 
    #    """
    #    load_ui = uitools.start_load_ui(self.ui)
    #    load_ui.setWindowTitle('plugins loader')
    #    load_ui.tree_box.setTitle('Select a .wfl file to load plugins')
    #    load_ui.load_button.clicked.connect( partial(self.finish_load_plugins,load_ui) )
    #    load_ui.show()
    #    load_ui.activateWindow()
      
    def save_state(self):
        """
        Start a modal window dialog to choose a .wfl to save the current configuration  
        """
        save_ui = uitools.start_save_ui(self.ui)
        save_ui.setWindowTitle('paws saver')
        #wf_idx = self.ui.wf_selector.currentIndex()
        #wfname = self.ui.wf_selector.model().list_data()[wf_idx]
        save_ui.tree_box.setTitle('Select or enter a .wfl file to save current configuration.')
        save_ui.save_button.clicked.connect( partial(self.finish_save_state,save_ui) )
        save_ui.show()
        save_ui.activateWindow()

    def load_state(self):
        """
        Start a modal window dialog to choose a .wfl to load a previously saved configuration 
        """
        load_ui = uitools.start_load_ui(self.ui)
        load_ui.setWindowTitle('paws loader')
        load_ui.tree_box.setTitle('Select a .wfl file to load a saved paws configuration.')
        load_ui.load_button.clicked.connect( partial(self.finish_load_state,load_ui) )
        load_ui.show()
        load_ui.activateWindow()
      
    #def finish_save_plugins(self,ui):
    #    fname = ui.filename.text()
    #    if not os.path.splitext(fname)[1] == '.wfl':
    #        fname = fname + '.wfl'
    #    self.msg_board_log( 'dumping current set of plugins to {}'.format(fname) )
    #    d = {} 
    #    pgin_dict = OrderedDict() 
    #    for pgin_name in self.qplugman.plugman.list_plugins():
    #        pgin = self.qplugman.plugman.get_data_from_uri(pgin_name)
    #        if not isinstance(pgin,WfManagerPlugin):
    #            pgin_dict[pgin_name] = self.qplugman.plugman.plugin_setup_dict(pgin)
    #    d['PLUGINS'] = pgin_dict
    #    pawstools.update_file(fname,d)
    #    ui.close()

    #def finish_load_plugins(self,ui):
    #    fname = ui.tree.model().filePath(ui.tree.currentIndex())
    #    f = open(fname,'r')
    #    d = yaml.load(f)
    #    f.close()
    #    fname_nopath = os.path.split(fname)[1]
    #    fname_noext = os.path.splitext(fname_nopath)[0]
    #    if 'PLUGINS' in d.keys():
    #        self.qplugman.load_from_dict(d['PLUGINS'])
    #    ui.close()

    def finish_save_state(self,ui):
        fname = ui.filename.text()
        self.paw.save_to_wfl(fname)
        ui.close()

    def finish_load_state(self,ui):
        fname = ui.tree.model().filePath(ui.tree.currentIndex())
        # NOTE: code duplication with paws.api.__init__
        #self.paw.load_from_wfl(fname)
        f = open(wfl_filename,'r')
        d = yaml.load(f)
        f.close()
        for pgin_name,pginspec in d:
            if not pgin_name == 'wf_manager':
                self.qplugman.load_from_dict(pgin_name,pgin_dict)
        wfman_dict = d['wf_manager']
        for wfname,wfspec in wfman_dict:
            self.qwfman.load_from_dict(wfname,self.qopman.opman,wfspec)
            if not wfname in self.ui.wf_selector.model().list_data():
                self.ui.wf_selector.model().append_item(wfname)
            if self.qwfman.n_wf() == 1:
                self.ui.wf_tree.hideColumn(1)
        ui.close()

