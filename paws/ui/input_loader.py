from PySide import QtCore, QtGui, QtUiTools

from ..core.operations import optools
from ..core import pawstools
from ..core.listmodel import ListModel

class InputLoader(object):
    """This class controls the input_loader.ui to select inputs from various sources."""

    def __init__(self,name,src,trmod=None,parent=None):
        super(InputLoader,self).__init__()
        self.src = src
        self.trmod = trmod
        self.setup_ui()
        if parent:
            self.ui.setParent(parent,QtCore.Qt.Window)
        self.ui.show()

    def setup_ui(self):
        if self.src == optools.text_input:
            ui_file = QtCore.QFile(pawstools.rootdir+"/ui/qtui/text_input_loader.ui")
        elif self.src in [optools.wf_input,optools.plugin_input,optools.fs_input]:
            ui_file = QtCore.QFile(pawstools.rootdir+"/ui/qtui/tree_input_loader.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.ui.setWindowTitle("input loader")
        if self.src in [optools.wf_input,optools.plugin_input,optools.fs_input]:
            self.ui.source_treeview.setModel(self.trmod)
        if self.src == optools.fs_input:
            self.trmod.setRootPath(QtCore.QDir.currentPath())
            self.ui.source_treeview.hideColumn(1)
            self.ui.source_treeview.hideColumn(3)
            self.ui.source_treeview.setColumnWidth(0,400)
        elif self.src in [optools.wf_input,optools.plugin_input]:
            self.ui.source_treeview.setColumnWidth(0,300)
            # Reset all selections
            self.trmod.set_all_unselected()
        if self.src == optools.text_input:
            self.ui.add_button.setText("&Add entries")
        elif self.src in [optools.wf_input,optools.plugin_input]:
            self.ui.add_button.setText("&Add selections")
        elif self.src == optools.fs_input:
            self.ui.add_button.setText("&Add selection")
        self.values_model = ListModel()
        self.ui.values_list.setModel(self.values_model)
        self.ui.finish_button.setText("&Finish")
        self.ui.remove_button.setText("&Remove selections")
        self.ui.list_toggle.setText("Package as &list")
        self.ui.add_button.clicked.connect(self.add_items)
        self.ui.remove_button.clicked.connect(self.rm_selection)

    def add_items(self):
        if self.src == optools.text_input:
            lines = self.ui.source_textedit.toPlainText().split()
            for l in lines:
                self.add_value(str(l).strip())
        elif self.src in [optools.wf_input,optools.plugin_input]:
            # Get all items currently selected
            idxs = self.trmod.get_all_selected()
            if all([_idx.isValid() for _idx in idxs]):
                for idx in idxs:
                    val = str(self.trmod.build_uri(idx)).strip()
                    self.add_value(val)
            else:
                # if user did not use selection model, take current index
                idx = self.ui.source_treeview.currentIndex()
                val = str(self.trmod.build_uri(idx)).strip()
                self.add_value(val)
            # Reset all selections
            self.trmod.set_all_unselected()
        elif self.src == optools.fs_input:
            idx = self.ui.source_treeview.currentIndex()
            val = str(self.ui.source_treeview.model().filePath(idx)).strip()
            self.add_value(val)

    def add_value(self,val):
        self.ui.values_list.model().append_item(val) 
        # if we end with more than one selection, set and lock self.ui.list_toggle
        nvals = self.ui.values_list.model().rowCount()
        if nvals > 1:
            self.set_list_toggle()
            self.lock_list_toggle()

    def rm_selection(self):
        # get selected index(es) in self.ui.values_list
        idx = self.ui.values_list.currentIndex()
        # remove them cleanly
        if idx.isValid():
            self.ui.values_list.model().remove_item(idx.row())
        # if we end with one or less value, unset and unlock self.ui.list_toggle
        nvals = self.ui.values_list.model().rowCount()
        if nvals <= 1:
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

