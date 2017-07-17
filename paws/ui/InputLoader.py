import os
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from ..core import pawstools
from ..core.models.ListModel import ListModel
from ..core.operations import Operation as op

class InputLoader(object):
    """This class controls the input_loader.ui to select inputs from various sources."""

    def __init__(self,name,src,src_manager=None,parent=None):
        super(InputLoader,self).__init__()
        self.input_name = name
        self.src = src
        self.src_manager = src_manager 
        self.setup_ui()
        if parent:
            self.ui.setParent(parent,QtCore.Qt.Window)

    def setup_ui(self):
        if self.src == op.text_input:
            ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/text_input_loader.ui")
        elif self.src in [op.plugin_input,op.fs_input]:
            ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/tree_input_loader.ui")
        elif self.src == op.wf_input:
            ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/wf_input_loader.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.ui.setWindowTitle("input loader")
        self.ui.input_box.setTitle(self.input_name)
        if self.src in [op.plugin_input,op.fs_input]:
            self.ui.source_treeview.setModel(self.src_manager)
        elif self.src == op.wf_input:
            lm = ListModel(self.src_manager.qworkflows.keys())
            self.ui.wf_selector.setModel(lm)
            self.ui.wf_selector.currentIndexChanged.connect( partial(self.set_wf) )
        if self.src == op.fs_input:
            self.src_manager.setRootPath(QtCore.QDir.currentPath())
            idx = self.src_manager.index(QtCore.QDir.currentPath())
            while idx.isValid():
                self.ui.source_treeview.setExpanded(idx,True)
                idx = idx.parent()
            self.ui.source_treeview.setExpanded(self.src_manager.index(pawstools.sourcedir),True)
            self.ui.source_treeview.hideColumn(1)
            self.ui.source_treeview.hideColumn(3)
            self.ui.source_treeview.setColumnWidth(0,250)
        elif self.src in [op.plugin_input,op.wf_input]:
            self.ui.source_treeview.hideColumn(2)
            self.ui.source_treeview.setColumnWidth(0,250)
            self.tree_model().set_all_flagged('select',False)
        if self.src == op.plugin_input:
            self.ui.source_treeview.setRootIndex(self.src_manager.root_index())
        elif self.src == op.wf_input:
            self.set_wf() 
        if self.src == op.text_input:
            self.ui.set_button.setText("&Set entries")
            self.ui.add_button.setText("&Add entries")
        elif self.src in [op.wf_input,op.plugin_input,op.fs_input]:
            self.ui.set_button.setText("&Set selected")
            self.ui.add_button.setText("&Add selected")
        self.values_model = ListModel()
        self.ui.values_list.setModel(self.values_model)
        self.ui.finish_button.setText("&Finish")
        self.ui.clear_button.setText("&Clear all")
        self.ui.remove_button.setText("&Remove selected")
        self.ui.list_toggle.setText("Package as &list")
        self.ui.add_button.clicked.connect( partial(self.make_selection,True) )
        self.ui.set_button.clicked.connect( partial(self.make_selection,False) )
        self.ui.remove_button.clicked.connect(self.rm_selection)
        self.ui.clear_button.clicked.connect(self.clear_values)

    def tree_model(self):
        if self.src in [op.plugin_input,op.fs_input]:
            return self.src_manager
        elif self.src == op.wf_input:
            wf_idx = self.ui.wf_selector.currentIndex()
            wfname = self.ui.wf_selector.model().list_data()[wf_idx]
            return self.src_manager.qworkflows[wfname]
        else:
            return None

    def set_wf(self,wf_idx=None):
        if wf_idx is None:
            wf_idx = self.ui.wf_selector.currentIndex() 
        wfname = self.ui.wf_selector.model().list_data()[wf_idx]
        self.ui.source_treeview.setModel(self.src_manager.qworkflows[wfname])
        self.ui.source_treeview.setRootIndex(self.src_manager.qworkflows[wfname].root_index())
        self.ui.source_treeview.hideColumn(2)
        self.ui.source_treeview.setColumnWidth(0,250)

    def get_values(self):
        #import pdb; pdb.set_trace()
        if self.src == op.text_input:
            vals = self.ui.source_textedit.toPlainText().split(os.linesep)
        elif self.src in [op.plugin_input,op.wf_input]:
            # Get all items currently selected
            idxs = self.tree_model().get_flagged_idxs('select')
            if any(idxs) and all([idx.isValid() for idx in idxs]):
                vals = [str(self.tree_model().get_uri_of_index(idx)).strip() for idx in idxs]
            # If user did not use tree selection model, take currentIndex()
            else:
                idx = self.ui.source_treeview.currentIndex()
                vals = [str(self.tree_model().get_uri_of_index(idx)).strip()]
            # Reset all selections
            self.tree_model().set_all_flagged('select',False)
        elif self.src == op.fs_input:
            idx = self.ui.source_treeview.currentIndex()
            vals = [str(self.ui.source_treeview.model().filePath(idx)).strip()]
        return vals

    def make_selection(self,append=True):
        vals = self.get_values()
        if append:
            self.add_values(vals)
        else:
            self.set_values(vals)

    def clear_values(self):
        nvals = self.ui.values_list.model().rowCount()
        self.ui.values_list.model().removeRows(0,nvals)
        self.check_list_toggle()

    def set_values(self,vals):
        self.clear_values()
        self.add_values(vals)    
        self.check_list_toggle()

    def add_values(self,vals):
        if vals is not None:
            for val in vals:
                self.ui.values_list.model().append_item(str(val)) 
        self.check_list_toggle()

    def rm_selection(self):
        idx = self.ui.values_list.currentIndex()
        if idx.isValid():
            self.ui.values_list.model().remove_item(idx.row())
        self.check_list_toggle()

    def check_list_toggle(self):
        # if we have more than one selection, set and lock self.ui.list_toggle
        nvals = self.ui.values_list.model().rowCount()
        if nvals > 1:
            self.set_list_toggle()
            self.lock_list_toggle()
        # if we have one or less value, unset and unlock self.ui.list_toggle
        elif nvals <= 1:
            self.unset_list_toggle()
            self.unlock_list_toggle()

    def unset_list_toggle(self):
        self.ui.list_toggle.setCheckState(QtCore.Qt.Unchecked)
        
    def set_list_toggle(self):
        self.ui.list_toggle.setCheckState(QtCore.Qt.Checked)
        
    def lock_list_toggle(self):
        self.ui.list_toggle.setEnabled(False)

    def unlock_list_toggle(self):
        self.ui.list_toggle.setEnabled(True)

