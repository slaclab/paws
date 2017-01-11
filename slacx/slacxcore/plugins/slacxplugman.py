from PySide import QtCore

from ..treemodel import TreeModel
from ..treeitem import TreeItem

from .. import plugins as pgns

class PluginManager(TreeModel):
    """
    Tree structure for managing slacx plugins.
    """

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
            return item.tag()
        #elif (data_role == QtCore.Qt.ToolTipRole 
        #    or data_role == QtCore.Qt.StatusTipRole
        #    or data_role == QtCore.Qt.WhatsThisRole):
        #        return item.data.description()
        else:
            return None
    



