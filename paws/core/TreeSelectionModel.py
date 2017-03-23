import string 
from collections import OrderedDict

from PySide import QtCore

from .TreeModel import TreeModel

class TreeSelectionModel(TreeModel):

    def __init__(self):
        super(TreeSelectionModel,self).__init__()

    def columnCount(self,parent):
        """
        Let TreeSelectionModel have three columns:
        one for the TreeItem tag, 
        one for enabled/disabled switch,
        one for selection use.
        """
        return 3

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return super(TreeSelectionModel,self).data(section,orientation,data_role) 
        elif (data_role == QtCore.Qt.DisplayRole and section == 1):
            return "selected"
        elif (data_role == QtCore.Qt.DisplayRole and section == 2):
            return "enabled"

    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,itm_idx,data_role):
        if (not itm_idx.isValid()):
            return None
        itm = itm_idx.internalPointer()
        if ((data_role == QtCore.Qt.DisplayRole
        or data_role == QtCore.Qt.ToolTipRole 
        or data_role == QtCore.Qt.StatusTipRole
        or data_role == QtCore.Qt.WhatsThisRole)
        and itm_idx.column() == 0):
            return itm.tag()
        elif data_role == QtCore.Qt.CheckStateRole and itm_idx.column() == 1:
            if itm.is_checked():
                return QtCore.Qt.Checked
            elif itm.children_checked():
                return QtCore.Qt.PartiallyChecked
            else:
                return QtCore.Qt.Unchecked
        elif data_role == QtCore.Qt.CheckStateRole and itm_idx.column() == 2:
            if itm.is_checked():
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.Unchecked
        else:
            return None

    # Need flags to reflect checkability
    def flags(self, idx):
        if not idx.isValid():
            return None
        elif idx.column() == 1:
            return super(TreeSelectionModel,self).flags(idx) | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate
        else:
            return super(TreeModel, self).flags(idx)

    # Ui-editable QAbstractItemModel subclasses must implement setData(index,value[,role])
    def setData(self,idx,value,data_role):
        if idx.column() == 1:
            #if role == Qt.EditRole:
            #    return False
            if data_role == QtCore.Qt.CheckStateRole:
                itm = self.get_item(idx)
                itm.set_checked(value)
                self.dataChanged.emit(idx, idx)
                return True
            else:
                return super(TreeModel, self).setData(index, value, data_role)
        else:
            return super(TreeModel, self).setData(index, value, data_role)

    def set_all_unselected(self,idx=QtCore.QModelIndex()):
        if idx.isValid():
            itm = self.get_item(idx)
            itm.set_checked(False)
            for c_row in range(itm.n_children()):
                c_idx = self.index(c_row,0,idx)
                self.set_all_unselected(c_idx)
        else:
            for r_row in range(self.rowCount()):
                r_idx = self.index(r_row,0,idx)
                self.set_all_unselected(r_idx)
            
    def get_all_selected(self,idx=QtCore.QModelIndex()):
        sel_idxs = []
        if idx.isValid():
            itm = self.get_item(idx)
            if itm.is_checked():
                sel_idxs.append(idx)
            for c_row in range(itm.n_children()):
                c_idx = self.index(c_row,0,idx)
                sel_idxs = sel_idxs + self.get_all_selected(c_idx)
        else:
            for r_row in range(self.rowCount()):
                r_idx = self.index(r_row,0,idx)
                sel_idxs = sel_idxs + self.get_all_selected(r_idx)
        return sel_idxs




