import copy

from PySide import QtCore

from .QTreeModel import QTreeModel

class QTreeSelectionModel(QTreeModel):
    """
    QTreeSelectionModel extends QTreeModel 
    by using TreeItem.flags to handle tree item selection.
    """

    def __init__(self,flag_defaults={},trmod=QTreeModel()):
        super(QTreeSelectionModel,self).__init__(trmod)
        self.flag_defaults = flag_defaults 

    def create_tree_item(self,parent_itm,itm_tag):
        """
        Build a TreeItem for use in this tree.
        Reimplemented for QTreeSelectionModel to set its flag_defaults
        as the flags for any new TreeItems.
        """
        itm = self._tree.create_tree_item(parent_itm,itm_tag)
        itm.flags = copy.copy(self.flag_defaults)
        return itm

    def n_flags(self):
        return len(self.flag_defaults)

    def is_flagged(self,itm,flag_key):
        if flag_key in itm.flags.keys():
            return bool(itm.flags[flag_key])

    def children_flagged(self,itm,flag_key):
        if flag_key in itm.flags.keys():
            if itm.n_children() > 0:
                return any([self.children_flagged(c_itm,flag_key) for c_itm in itm.children])
            else:
                return bool(itm.flags[flag_key])

    def set_flagged(self,itm,flag_key,val):
        itm.flags[flag_key] = bool(val)

    def set_all_flagged(self,flag_key,val,itm=None):
        if itm is None:
            itm = self._tree._root_item
        self.set_flagged(itm,flag_key,val)
        for c_itm in itm.children:
            self.set_all_flagged(flag_key,val,c_itm)

    def get_flagged_idxs(self,flag_key,idx=None,val=True):
        if idx is None:
            idx = self.root_index()
        itm = self.get_from_index(idx) 
        flagged_idxs = []
        if self.is_flagged(itm,flag_key) == val:
            if not idx == self.root_index():
                flagged_idxs.append(idx)
        for c_row in range(itm.n_children()):
            c_idx = self.index(c_row,0,idx)
            flagged_idxs = flagged_idxs + self.get_flagged_idxs(flag_key,c_idx,val)
        return flagged_idxs

    def columnCount(self,parent):
        """
        Let QTreeSelectionModel have n_flags+1 columns:
        one for the TreeItem tag, the rest for flags 
        """
        return 1+self.n_flags() 

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return super(QTreeSelectionModel,self).headerData(section,orientation,data_role) 
        elif (data_role == QtCore.Qt.DisplayRole and section < self.n_flags()+1):
            return self.flag_defaults.keys()[section-1]
        else:
            return None
        #elif (data_role == QtCore.Qt.DisplayRole and section == 1):
        #    return "selected"
        #elif (data_role == QtCore.Qt.DisplayRole and section == 2):
        #    return "enabled"

    def data(self,idx,data_role):
        if (not idx.isValid()):
            return None
        itm = idx.internalPointer()
        if idx.column() == 0:
            return super(QTreeSelectionModel,self).data(idx,data_role)
        elif data_role == QtCore.Qt.CheckStateRole: 
            return self.check_state(itm,self.flag_defaults.keys()[idx.column()-1])
        else:
            # Not column 0, not CheckStateRole: return None
            return None

    def check_state(self,itm,flag_key):
        if self.is_flagged(itm,flag_key):
            return QtCore.Qt.Checked
        elif self.children_flagged(itm,flag_key):
            return QtCore.Qt.PartiallyChecked
        else:
            return QtCore.Qt.Unchecked

    # Need flags to reflect checkability
    def flags(self, idx):
        if not idx.isValid():
            return None
        elif idx.column() == 0:
            return super(QTreeSelectionModel,self).flags(idx)
        else:
            return super(QTreeSelectionModel,self).flags(idx) | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate

    # Ui-editable QAbstractItemModel subclasses must implement setData(index,value[,role])
    def setData(self,idx,val,data_role):
        if idx.column() == 0:
            return super(QTreeSelectionModel,self).setData(index,val,data_role)
        elif data_role == QtCore.Qt.CheckStateRole:
            itm = self.get_from_index(idx)
            self.set_flagged(itm,self.flag_defaults.keys()[idx.column()-1],val)
            self.dataChanged.emit(idx,idx)
            return True
        else:
            return super(QTreeSelectionModel,self).setData(index,val,data_role)

