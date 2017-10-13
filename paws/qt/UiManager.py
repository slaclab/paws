import os
from functools import partial
from collections import OrderedDict

from PySide import QtGui, QtCore, QtUiTools
import yaml

from ..core.operations.Operation import Operation
from . import qttools
from . import widgets 
from ..core import pawstools
from ..core import plugins as pgns
from ..core.models.ListModel import ListModel
from .widgets import WorkflowGraphView

class UiManager(QtCore.QObject):
    """
    Uses the QPawsAPI and PySide Qt to provide a widget that controls PAWS.
    """

    def __init__(self,qpaw):
        super(UiManager,self).__init__()
        ui_file = QtCore.QFile(os.path.join(pawstools.sourcedir,'qt','qtui','main.ui'))
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        qpaw.set_logmethod( self.msg_board_log )
        qpaw._wf_manager.emitMessage.connect( self.logMessage )
        self.paw = qpaw
        self.make_viewer()
        self.build()
        self.threads = QtCore.QThreadPool()

    @QtCore.Slot(str)
    def logMessage(self,msg):
        self.msg_board_log(msg)

    def msg_board_log(self,msg):
        """Print timestamped message to msg board"""
        #if (self.ui.message_board.verticalScrollBar().value() == 
        #self.ui.message_board.verticalScrollBar().maximum()):
        #    advance_scrollbar = True
        #else:
        #    advance_scrollbar = False
        self.ui.message_board.appendPlainText(
        '- ' + pawstools.timestr() + ': ' + msg)#+ '\n') 
        #if advance_scrollbar:
        self.ui.message_board.verticalScrollBar().setValue(
        self.ui.message_board.verticalScrollBar().maximum())

    def make_viewer(self):
        """
        Set up the tab viewer widget 
        and display the paws logo 
        in the main viewer
        """
        self.ui.viewer_tabwidget.clear()
        self.viewer_widgets = {}

        self._viewer_frame = QtGui.QFrame()
        self._viewer_layout = QtGui.QGridLayout()
        self._viewer_frame.setLayout(self._viewer_layout)
        self.viewer_widgets['main viewer'] = self._viewer_frame 
        self.ui.viewer_tabwidget.addTab(self._viewer_frame,'main viewer')

        # logo scene:
        img_file = os.path.join(pawstools.rootdir,'graphics','paws_icon_white.png')
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
        self._viewer_layout.addWidget(logo_view,0,0)

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
        self.paw._wf_manager.wfStopped.connect(self.update_run_wf_button)
        self.ui.workflows_box.setTitle('Workflows')
        if qttools.have_qt47:
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
        # workflow name entry size policies
        self.ui.wf_name_header.setSizePolicy(QtGui.QSizePolicy.Maximum,
        self.ui.wf_name_header.sizePolicy().verticalPolicy())
        self.ui.wf_name_entry.setSizePolicy(QtGui.QSizePolicy.Minimum,
        self.ui.wf_name_entry.sizePolicy().verticalPolicy())
        self.ui.add_workflow_button.setText('Add')
        self.ui.add_workflow_button.clicked.connect( self.add_wf )
        self.paw._wf_manager.wfAdded.connect(self.append_to_wf_selector)
        lm = ListModel(self.paw.list_wf_tags())
        self.ui.wf_selector.setModel(lm)
        self.ui.wf_selector.currentIndexChanged.connect( partial(self.set_wf) )
        self.ui.run_wf_button.setText("&Run")
        self.ui.run_wf_button.clicked.connect(self.toggle_run_wf)
        #self.qwfman.wfdone.connect(self.update_run_wf_button)
        # If for some reason the QPawsAPI (self.paw) calls select_wf(),
        # the UI should also select that wf.
        self.paw.wfSelectionChanged.connect(self.select_wf)

        # Plugins ui stuff
        self.ui.plugins_box.setTitle('Plugins')
        self.ui.plugin_tree.setModel(self.paw._plugin_manager)
        self.ui.plugin_tree.clicked.connect( self.display_plugin_item )
        self.ui.plugin_tree.setRootIndex(self.paw._plugin_manager.root_index())
        if qttools.have_qt47:
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
        # plugin name entry size policies
        self.ui.add_plugin_header.setSizePolicy(QtGui.QSizePolicy.Maximum,
        self.ui.add_plugin_header.sizePolicy().verticalPolicy())
        self.ui.plugin_name_entry.setSizePolicy(QtGui.QSizePolicy.Maximum,
        self.ui.plugin_name_entry.sizePolicy().verticalPolicy())
        self.ui.plugin_selector.setMinimumWidth(160)
        self.ui.plugin_selector.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
        self.ui.plugin_selector.sizePolicy().verticalPolicy())
        pgin_lm = ListModel(pgns.plugin_name_list)
        self.ui.plugin_selector.setModel(pgin_lm)
        self.ui.add_plugin_button.setText('Add')
        self.ui.plugin_tree.hideColumn(1)
        self.ui.plugin_tree.hideColumn(2)
        self.ui.plugin_tree.setColumnWidth(0,200)
        self.ui.add_plugin_button.clicked.connect( self.add_plugin )

        self.ui.op_tree.setModel(self.paw._op_manager)
        self.ui.op_tree.setRootIndex(self.paw._op_manager.root_index())
        self.ui.op_tree.clicked.connect( self.display_op_item )
        self.ui.wf_tree.clicked.connect( self.display_wf_item )

        self.ui.message_board.setReadOnly(True)
        self.ui.message_board.insertPlainText('--- MESSAGE BOARD ---') 
        self.ui.op_info_box.insertPlainText('Operation info: click an Operation above to see its documentation here')
        self.msg_board_log('paws is ready') 
        self.ui.op_tree.setColumnWidth(0,200)
        # UI splitter sizing
        self.ui.hsplitter.setStretchFactor(0,3)    
        self.ui.hsplitter.setStretchFactor(1,5)    
        self.ui.hsplitter.setStretchFactor(2,2)    
        self.ui.left_vsplitter.setStretchFactor(0,1)    
        self.ui.left_vsplitter.setStretchFactor(1,3)    
        self.ui.left_vsplitter.setStretchFactor(2,3)    
        self.ui.center_vsplitter.setStretchFactor(0,1)    

    def append_to_wf_selector(self,new_wfname):
        self.ui.wf_selector.model().append_item(new_wfname)

    def select_wf(self,wfname):
        wf_idx = self.ui.wf_selector.model().list_data().index(wfname)
        self.ui.wf_selector.setCurrentIndex(wf_idx)
        self.set_wf_treeview(wfname)

    def set_wf_treeview(self,wfname):
        wf = self.paw.get_wf(wfname)
        self.ui.wf_tree.setModel(wf)
        self.ui.wf_tree.setRootIndex(wf.root_index())
        # hide the selection flag column.
        self.ui.wf_tree.hideColumn(1)
        self.ui.wf_tree.setColumnWidth(0,200)
        self.update_run_wf_button()

    def set_wf(self,wf_selector_idx):
        wfname = self.ui.wf_selector.model().list_data()[wf_selector_idx]
        if not wfname == self.paw.current_wf_name():
            self.paw.select_wf(wfname)
            self.set_wf_treeview(wfname)

    def add_plugin(self):
        pgin_name = self.ui.plugin_name_entry.text()
        if pgin_name in self.paw.list_plugin_tags():
            msg_ui = qttools.message_ui(self.ui)
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
                pgin = self.paw.load_plugin(pgin_uri)
            except pawstools.PluginLoadError as ex:
                msg_ui = qttools.message_ui(self.ui)
                msg_ui.setWindowTitle("Plugin Load Error")
                msg_ui.message_box.setPlainText(ex.message)
                msg_ui.show()
                return
            try:
                self.paw.add_plugin(pgin_name,pgin)
            except pawstools.PluginNameError as ex:
                msg_ui = qttools.message_ui(self.ui)
                msg_ui.setWindowTitle("Plugin Name Error")
                msg_ui.message_box.setPlainText(ex.message)
                msg_ui.show()
                return
            self.ui.plugin_name_entry.clear()

    def add_wf(self):
        """
        Method for adding workflows through the main UI.
        For this case, the workflow name is inspected
        to ensure that it doesn't clobber an existing workflow.
        """
        wfname = self.ui.wf_name_entry.text()
        if wfname in self.paw.list_wf_tags():
            msg_ui = qttools.message_ui(self.ui)
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
                msg_ui = qttools.message_ui(self.ui)
                msg_ui.setWindowTitle("Workflow Name Error")
                msg_ui.message_box.setPlainText(ex.message)
                msg_ui.show()
                return
            self.append_to_wf_selector(wfname)
            #self.ui.wf_selector.setCurrentIndex(self.paw.n_wf()-1)
            self.paw.set_wf(wfname)
            self.ui.wf_name_entry.clear()
            # Add a tab to the viewer for this workflow 
            self.add_wf_tab(wfname)

    def add_wf_tab(self,wfname):
        wf = self.paw.get_wf(wfname)
        g = WorkflowGraphView(wf,self.ui)
        tab_idx = self.ui.viewer_tabwidget.addTab(g,wfname) 

    def display_op_item(self,idx):
        """
        Display selected item from the op tree in viewer layout 
        """
        if idx.isValid(): 
            # Change the current selection to this index
            self.ui.op_tree.setCurrentIndex(idx.sibling(idx.row(),0))
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
            w = QtGui.QTextEdit()
            w.setText(t)
            self.ui.op_info_box.setText(t)

    def display_plugin_item(self,idx):
        """
        Display selected item from the plugin tree in viewer layout 
        """
        if idx.isValid(): 
            itm_data = self.paw.get_plugin_from_index(idx)
            widg = widgets.make_widget(itm_data)
            self.main_display(widg)

    def display_wf_item(self,idx):
        """
        Display selected item from the workflow tree in viewer layout 
        """
        if idx.isValid(): 
            itm_data = self.paw.current_wf().get_data_from_index(idx)
            widg = widgets.make_widget(itm_data)
            self.main_display(widg)

    def main_display(self,widg=None):
        # Bring up the main viewer from the viewer_tabwidget
        self.ui.viewer_tabwidget.setCurrentWidget(self._viewer_frame)
        # Loop through the viewer layout, last to first, clear the frame
        n_widgets = self._viewer_layout.count()
        for i in range(n_widgets-1,-1,-1):
            # QLayout.takeAt returns a LayoutItem
            itm = self._viewer_layout.takeAt(i)
            # get the QWidget of that LayoutItem and close it 
            itm.widget().close()
            del itm
        if widg is not None:
            self._viewer_layout.addWidget(widg,0,0) 

    def toggle_run_wf(self,wfname=None):
        if wfname is None:
            wfname = self.paw.current_wf_name()
        if wfname is not None:
            if self.paw.is_wf_running(wfname):
                self.stop_wf(wfname)
            else:
                self.start_wf(wfname)

    def start_wf(self,wfname):
        self.ui.run_wf_button.setText("S&top")
        # NOTE: this is where we choose between threaded or not.
        # TODO: consider exposing both run modes to the user.
        self.paw.run_wf(wfname,self.threads)
        #self.paw.run_wf(wfname,None)

    def stop_wf(self,wfname):
        # TODO: the interruption will have to be carried out by signals and slots.
        # the signal should be emitted in QPawsAPI.stop_wf and the slot should be in QWorkflow.
        # TODO: consider how to interrupt a running operation,
        # e.g. a batch execution controller.
        self.paw.stop_wf(wfname)
        self.ui.run_wf_button.setText("&Run")

    def update_run_wf_button(self,wfname=None):
        """
        If the input wfname indicates the currently selected workflow,
        make the self.ui.run_wf_button sane wrt this workflow's status.
        """
        if self.paw.current_wf_name() == wfname:
            if self.paw.is_wf_running(wfname):
                self.ui.run_wf_button.setText("S&top")
            else:
                self.ui.run_wf_button.setText("&Run")

    def save_state(self):
        """
        Start a modal window dialog to choose a .wfl to save the current configuration  
        """
        save_ui = qttools.start_save_ui(self.ui)
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
        load_ui = qttools.start_load_ui(self.ui)
        load_ui.setWindowTitle('paws loader')
        load_ui.tree_box.setTitle('Select a .wfl file to load a saved paws configuration.')
        load_ui.load_button.clicked.connect( partial(self.finish_load_state,load_ui) )
        load_ui.show()
        load_ui.activateWindow()
      
    def finish_save_state(self,ui):
        fname = ui.filename.text()
        self.paw.save_to_wfl(fname)
        ui.close()

    def finish_load_state(self,ui):
        fname = ui.tree.model().filePath(ui.tree.currentIndex())
        self.paw.load_from_wfl(fname)
        ui.close()

