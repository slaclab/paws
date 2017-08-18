import os
from functools import partial
from collections import OrderedDict

from PySide import QtGui, QtCore, QtUiTools
import yaml

from ..core.operations.Operation import Operation
from . import uitools
from . import widgets 
from ..core import pawstools
from ..core import plugins as pgns
from .WfUiManager import WfUiManager
from .OpUiManager import OpUiManager
from .PluginUiManager import PluginUiManager
from ..core.models.ListModel import ListModel
from ..qt.QWfManager import QWfManager
from ..qt.QOpManager import QOpManager
from ..qt.QPluginManager import QPluginManager

class UiManager(QtCore.QObject):
    """
    Uses the QPawsAPI and PySide Qt to provide a widget that controls PAWS.
    """

    def __init__(self,qpaw,app):
        super(UiManager,self).__init__()
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/basic.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        qpaw.set_logmethod( self.msg_board_log )
        #paws_api._op_manager.logmethod = self.msg_board_log
        #paws_api._wf_manager.logmethod = self.msg_board_log
        #paws_api._plugin_manager.logmethod = self.msg_board_log

        # TODO: replace all refs to these with refs to qpaw
        #self.qplugman = QPluginManager(paws_api._plugin_manager)
        #self.qopman = QOpManager(paws_api._op_manager)
        #self.qwfman = QWfManager(paws_api._wf_manager,app)

        self.paw = qpaw
        self.make_title()
        self.build()
        #self.add_wf('new_workflow')

    #@QtCore.Slot(str)
    #def update_wfman_plugin(self,wfname):
    #    self.qplugman.update_plugin('wf_manager')

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
        self.ui.viewer_tabwidget.clear()
        tab_idx = self.ui.viewer_tabwidget.addTab(logo_view,'paws viewer') 
        self.ui.setWindowTitle("paws v{}".format(pawstools.version))
        self.ui.setWindowIcon(pixmap)

    def build(self):
        """
        Set up QObjects and model views 
        for communicating with paws objects 
        """
        self.ui.app_control_box.setTitle('Application Controls')
        self.ui.save_state_button.setText("&Save")
        self.ui.save_state_button.clicked.connect(self.save_state)
        self.ui.load_state_button.setText("&Load")
        self.ui.load_state_button.clicked.connect(self.load_state)

        # Workflows ui stuff
        self.ui.workflows_box.setTitle('Workflows')
        if uitools.have_qt47:
            self.ui.wf_name_entry.setPlaceholderText('(enter a name)')
        else:
            self.ui.wf_name_entry.setText('(enter a name)')
        self.ui.wf_name_header.setText('New workflow:')
        self.ui.wf_name_header.setReadOnly(True)
        self.ui.wf_name_header.setAlignment(QtCore.Qt.AlignRight)
        self.ui.wf_name_header.setStyleSheet( "QLineEdit { background-color: transparent }"
        + self.ui.wf_name_header.styleSheet() )
        self.ui.wf_name_header.setStyleSheet( "QLineEdit { border: none }" 
        + self.ui.wf_name_header.styleSheet() )
        self.ui.wf_name_entry.setSizePolicy(QtGui.QSizePolicy.Minimum,
        self.ui.wf_name_entry.sizePolicy().verticalPolicy())
        self.ui.wf_name_header.setSizePolicy(QtGui.QSizePolicy.Minimum,
        self.ui.wf_name_header.sizePolicy().verticalPolicy())
        self.ui.add_workflow_button.setText('Add')
        self.ui.add_workflow_button.clicked.connect( self.add_wf )
        lm = ListModel(['(select workflow)']+self.paw.list_wf_tags())
        self.ui.wf_selector.setModel(lm)
        self.ui.wf_selector.currentIndexChanged.connect( partial(self.set_wf) )
        self.ui.run_wf_button.setText("&Run")
        self.ui.run_wf_button.clicked.connect(self.toggle_run_wf)
        #self.qwfman.wfdone.connect(self.update_run_wf_button)

        # Plugins ui stuff
        self.ui.plugins_box.setTitle('Plugins')
        self.ui.plugin_tree.setModel(self.paw._plugin_manager)
        self.ui.plugin_tree.clicked.connect( self.display_plugin_item )
        self.ui.plugin_tree.setRootIndex(self.paw._plugin_manager.root_index())
        if uitools.have_qt47:
            self.ui.plugin_name_entry.setPlaceholderText('(enter a name)')
        else:
            self.ui.plugin_name_entry.setText('(enter a name)')
        self.ui.add_plugin_header.setText('New plugin:')
        self.ui.add_plugin_header.setReadOnly(True)
        self.ui.add_plugin_header.setAlignment(QtCore.Qt.AlignRight)
        self.ui.add_plugin_header.setStyleSheet( "QLineEdit { background-color: transparent }"
        + self.ui.add_plugin_header.styleSheet() )
        self.ui.add_plugin_header.setStyleSheet( "QLineEdit { border: none }" 
        + self.ui.add_plugin_header.styleSheet() )
        self.ui.plugin_name_entry.setSizePolicy(QtGui.QSizePolicy.Minimum,
        self.ui.plugin_name_entry.sizePolicy().verticalPolicy())
        self.ui.add_plugin_header.setSizePolicy(QtGui.QSizePolicy.Minimum,
        self.ui.add_plugin_header.sizePolicy().verticalPolicy())
        pgin_lm = ListModel(['(select plugin)']+pgns.plugin_name_list)
        self.ui.plugin_selector.setModel(pgin_lm)
        self.ui.add_plugin_button.setText('Add')
        self.ui.plugin_tree.hideColumn(1)
        self.ui.plugin_tree.hideColumn(2)
        self.ui.plugin_tree.setColumnWidth(0,200)
        self.ui.add_plugin_button.clicked.connect( self.add_plugin )

        #self.ui.add_wf_button.clicked.connect( partial(self.add_wf,'new_workflow') )
        self.ui.op_tree.setModel(self.paw._op_manager)
        #self.ui.op_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.op_tree) ) 
        self.ui.op_tree.setRootIndex(self.paw._op_manager.root_index())
        #self.ui.wf_tree.clicked.connect( partial(uitools.toggle_expand,self.ui.wf_tree) )
        self.ui.op_tree.clicked.connect( self.display_op_item )
        self.ui.wf_tree.clicked.connect( self.display_wf_item )
        #self.ui.wf_tree.doubleClicked.connect( partial(self.edit_wf) )
        #self.ui.edit_ops_button.setText("Edit operations")
        #self.ui.edit_ops_button.clicked.connect(self.edit_ops)
        #self.ui.add_wf_button.setText("&New workflow")
        #self.ui.setup_wf_button.setText("&Workflow setup...")
        #self.ui.setup_wf_button.clicked.connect(self.edit_wf)
        #self.ui.save_plugins_button.setText("Save plugins")
        #self.ui.save_plugins_button.clicked.connect(self.save_plugins)
        #self.ui.load_plugins_button.setText("Load plugins")
        #self.ui.load_plugins_button.clicked.connect(self.load_plugins)
        #self.ui.setup_plugins_button.setText("Plugin setup...")
        #self.ui.setup_plugins_button.clicked.connect(self.start_plugins_ui)

        self.ui.message_board.setReadOnly(True)
        self.ui.message_board.insertPlainText('--- MESSAGE BOARD ---') 
        self.ui.op_info_box.insertPlainText('Operation info: click an Operation above to see its documentation here')
        self.msg_board_log('paws is ready') 
        #self.ui.op_tree.hideColumn(1)
        #self.ui.op_tree.hideColumn(2)
        self.ui.op_tree.setColumnWidth(0,200)
        self.ui.hsplitter.setStretchFactor(0,2)    
        self.ui.hsplitter.setStretchFactor(1,3)    
        self.ui.hsplitter.setStretchFactor(2,1)    
        self.ui.left_vsplitter.setStretchFactor(0,1)    
        self.ui.left_vsplitter.setStretchFactor(1,3)    
        self.ui.left_vsplitter.setStretchFactor(2,3)    
        self.ui.center_vsplitter.setStretchFactor(0,1)    

    def set_wf(self,wf_selector_idx):
        wfname = self.ui.wf_selector.model().list_data()[wf_selector_idx]
        self.paw.select_wf(wfname)
        wf = self.paw.get_wf(wfname)
        self.ui.wf_tree.setModel(wf)
        self.ui.wf_tree.setRootIndex(wf.root_index())
        self.update_run_wf_button()

    def add_plugin(self):
        pgin_name = self.ui.plugin_name_entry.text()
        if pgin_name in self.paw.list_plugin_tags():
            msg_ui = uitools.message_ui(self.ui)
            msg_ui.setWindowTitle("Plugin Name Error")
            msg = '[{}] Name {} already assigned to a Plugin. '.format(
                __name__,pgin_name) + 'Loaded plugins: {}'.format(
                self.paw.list_plugin_tags())
            msg_ui.message_box.setPlainText(msg)
            msg_ui.show()
        else:
            try:
                idx = self.ui.plugin_selector.currentIndex()
                pgin_uri = self.ui.plugin_selector.model().list_data()[idx]
                pgin = self.paw.get_plugin(pgin_uri)
            except pawstools.PluginLoadError as ex:
                msg_ui = uitools.message_ui(self.ui)
                msg_ui.setWindowTitle("Plugin Load Error")
                msg_ui.message_box.setPlainText(ex.message)
                msg_ui.show()
            try:
                #pgin = self.paw.get_plugin(pgin_uri)
                self.paw.add_plugin(pgin_name,pgin)
            except pawstools.PluginNameError as ex:
                # Request a different tag 
                msg_ui = uitools.message_ui(self.ui)
                msg_ui.setWindowTitle("Plugin Name Error")
                msg_ui.message_box.setPlainText(ex.message)
                msg_ui.show()

    def add_wf(self):
        """
        Method for adding workflows through the main UI.
        For this case, the workflow name is inspected
        to ensure that it doesn't clobber an existing workflow.
        """
        wfname = self.ui.wf_name_entry.text()
        #if wfname in self.wfman.workflows.keys():
        #    wfname = self.wfman.auto_name(wfname)
        if wfname in self.paw.list_wf_tags():
            msg_ui = uitools.message_ui(self.ui)
            msg_ui.setWindowTitle("Workflow Name Error")
            msg = '[{}] Name {} already assigned to a Workflow. '.format(
                __name__,wfname) + 'Loaded workflows: {}'.format(
                self.paw.list_wf_tags())
            msg_ui.message_box.setPlainText(msg)
            msg_ui.show()
        else:
            try:
                self.paw.add_wf(wfname)
            except pawstools.WfNameError as ex:
                # Request a different tag 
                msg_ui = uitools.message_ui(self.ui)
                msg_ui.setWindowTitle("Workflow Name Error")
                msg_ui.message_box.setPlainText(ex.message)
                msg_ui.show()
            self.ui.wf_selector.model().append_item(wfname)
            # if this is the first workflow loaded, hide the selection flag column.
            self.ui.wf_selector.setCurrentIndex(self.paw.n_wf())
            if self.paw.n_wf() == 1:
                self.ui.wf_tree.hideColumn(1)
                self.ui.wf_tree.setColumnWidth(0,200)
                #self.ui.wf_tree.hideColumn(2)

    def display_op_item(self,idx):
        """
        Display selected item from the op tree in viewer layout 
        """
        if idx.isValid(): 
            # If the user is clicking a check box (idx.column()!=0),
            # leave the central display unchanged... ?
            #if idx.column() == 0:
                itm_data = self.paw.get_op_from_index(idx)
                itm_uri = self.paw.get_op_uri_from_index(idx)
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
                    t = t + self.paw._op_manager.print_cat(itm_uri) 
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
            itm_data = self.paw.get_plugin_from_index(idx)
            widg = widgets.make_widget(itm_data)
            self.display_widget(widg)

    def display_wf_item(self,idx):
        """
        Display selected item from the workflow tree in viewer layout 
        """
        if idx.isValid(): 
            itm_data = self.paw.current_wf().get_data_from_index(idx)
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

    def toggle_run_wf(self,wfname=None):
        if wfname is None:
            wfname = self.paw.current_wf_name()
        if wfname is not None:
            wf = self.paw.get_wf(wfname)
            if self.paw.is_wf_running(wfname): 
                self.paw.stop_wf(wfname)
                self.ui.run_wf_button.setText("&Run")
                #self.requestStopWorkflow.emit(wfname)
            else:
                self.ui.run_wf_button.setText("S&top")
                self.paw.execute(wfname)

    def update_run_wf_button(self):
        wfname = self.paw.current_wf_name() 
        if self.paw.is_wf_running(wfname):
            self.ui.run_wf_button.setText("S&top")
        else:
            self.ui.run_wf_button.setText("&Run")

    #def edit_wf(self,itm_idx=QtCore.QModelIndex()):
    #    """
    #    Interact with user to edit the workflow.
    #    Pass in QModelIndex to open the editor 
    #    with the item at that index loaded.
    #    """
    #    wf = self.paw.current_wf()
    #    #if wf is None:
    #    #    self.add_wf('new_workflow')
    #    #    wf = self.current_wf()
    #    if itm_idx.isValid():
    #        # valid index in workflow tree: percolate up to root ancestor
    #        while itm_idx.parent().isValid():
    #            itm_idx = itm_idx.parent()
    #    if itm_idx.isValid():
    #        uiman = self.start_wf_editor(wf,itm_idx)
    #    else:
    #        uiman = self.start_wf_editor(wf)
    #    uiman.ui.show()

    #def start_wf_editor(self,qwf=None,idx=QtCore.QModelIndex()):
    #    """
    #    Create a WfUiManager (QMainWindow), return it 
    #    """
    #    uiman = WfUiManager(self.qwfman,self.qopman,self.qplugman)
    #    uiman.ui.wf_selector.setCurrentIndex(self.ui.wf_selector.currentIndex())
    #    #uiman.set_wf()
    #    if qwf and idx.isValid():
    #        uiman.get_op(qwf,idx)
    #    uiman.ui.setParent(self.ui,QtCore.Qt.Window)
    #    return uiman

    #def edit_ops(self,itm_idx=None):
    #    """
    #    interact with user to enable existing Operations
    #    and edit or develop new Operations 
    #    """
    #    uiman = OpUiManager(self.qopman)
    #    uiman.ui.setParent(self.ui,QtCore.Qt.Window)
    #    uiman.ui.show()

    #def start_plugins_ui(self):
    #    uiman = PluginUiManager(self.qplugman)
    #    uiman.ui.setParent(self.ui,QtCore.Qt.Window)
    #    uiman.ui.show()

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
        self.paw.load_from_wfl(fname)
        # Some additional effort to update Qt objects.
        #f = open(wfl_filename,'r')
        #d = yaml.load(f)
        #f.close()
        #if 'OP_LOAD_FLAGS' in d.keys():
        #    # this should update the operation enable/disable fields
        #    self.qopman.tree_datachanged(self.qopman.root_index())
        #if 'WORKFLOWS' in d.keys():
        #    wf_dict = d['WORKFLOWS']
        #    for wfname,wfspec in wf_dict:
        #        # NOTE: this part duplicates effort
        #        self.qwfman.load_from_dict(wfname,self.qopman.opman,wfspec)
        #        # the rest is mundane widget handling
        #        if not wfname in self.ui.wf_selector.model().list_data():
        #            self.ui.wf_selector.model().append_item(wfname)
        #        if self.qwfman.n_wf() == 1:
        #            self.ui.wf_tree.hideColumn(1)
        #if 'PLUGINS' in d.keys():
        #    pgin_dict = d['PLUGINS']
        #    for pgin_name,pginspec in pgin_dict:
        #        # NOTE: this part duplicates effort
        #        self.qplugman.load_from_dict(pgin_name,pgin_dict)

