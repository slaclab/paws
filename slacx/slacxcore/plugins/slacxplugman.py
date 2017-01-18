from PySide import QtCore

from ..treemodel import TreeModel
from ..treeitem import TreeItem

from .. import plugins as pgns

class PluginManager(TreeModel):
    """
    Tree structure for managing slacx plugins.
    """

    # TODO: Render plugin content as subtree

    def __init__(self,**kwargs):
        super(PluginManager,self).__init__()

    # Overloaded headerData() for PluginManager 
    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "Plugins: {} active".format(len(self.root_items))
        else:
            return None

    # Overloaded data() for OpManager
    def data(self,itm_idx,data_role):
        if (not itm_idx.isValid()):
            return None
        itm = itm_idx.internalPointer()
        if data_role == QtCore.Qt.DisplayRole:
            return itm.tag()
        #elif (data_role == QtCore.Qt.ToolTipRole 
        #    or data_role == QtCore.Qt.StatusTipRole
        #    or data_role == QtCore.Qt.WhatsThisRole):
        #        return item.data.description()
        else:
            return None
    
    def add_plugin(self,uri,pgin):
        """Add a Plugin to the tree as a new top-level TreeItem."""
        ins_row = self.rowCount(QtCore.QModelIndex())
        itm = TreeItem(ins_row,0,QtCore.QModelIndex())
        itm.set_tag( uri )
        self.beginInsertRows(QtCore.QModelIndex(),ins_row,ins_row)
        self.root_items.insert(ins_row,itm)
        self.endInsertRows()
        idx = self.index(ins_row,0,QtCore.QModelIndex()) 
        self.tree_dataChanged(idx)

    def remove_plugin(self,rm_idx):
        """Remove a Plugin from the tree"""
        rm_row = rm_idx.row()
        self.beginRemoveRows(QtCore.QModelIndex(),rm_row,rm_row)
        item_removed = self.root_items.pop(rm_row)
        self.endRemoveRows()
        self.tree_dataChanged(rm_idx)

