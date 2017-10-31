import copy

from PySide import QtCore

from .QTreeModel import QTreeModel

class QTreeSelectionModel(QTreeModel):
    """
    QTreeSelectionModel extends QTreeModel 
    by using TreeItem.flags to handle tree item selection.
    """

    def __init__(self,flag_dict):
        super(QTreeSelectionModel,self).__init__(flag_dict)
        #self.flag_defaults = flag_defaults 

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
            return self.default_flags.keys()[section-1]
        else:
            return None

    def data(self,idx,data_role):
        if (not idx.isValid()):
            return None
        itm = idx.internalPointer()
        if idx.column() == 0:
            return super(QTreeSelectionModel,self).data(idx,data_role)
        elif data_role == QtCore.Qt.CheckStateRole: 
            return self.check_state(itm,self.default_flags.keys()[idx.column()-1])
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
            self.set_flagged(itm,self.default_flags.keys()[idx.column()-1],val)
            self.dataChanged.emit(idx,idx)
            return True
        else:
            return super(QTreeSelectionModel,self).setData(index,val,data_role)

