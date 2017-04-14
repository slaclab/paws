import string 
from collections import OrderedDict

from PySide import QtCore

from .TreeModel import TreeModel

class TreeSelectionModel(TreeModel):

    # TODO: reimplement add_item etc to ensure flags are added to TreeItems.

    def __init__(self,n_flags):
        super(TreeSelectionModel,self).__init__()
        self.flag_names = ['flag{}'.format(j) for j in range(n_flags)]
        self.flag_defaults = [False for j in range(n_flags)]

    def set_flag_names(self,flag_names,flag_defaults=None):
        if flag_defaults is None:
            flag_defaults = [False for j in range(len(flag_names))]
        if self.n_flags() == len(flag_names):
            self.flag_names = flag_names
        else:
            msg = 'expected {} flag names, got {}'.format(self.n_flags(),len(flag_names))
            raise ValueError(msg)

    def n_flags(self):
        return len(self.flag_names)

    @staticmethod
    def is_flagged(itm,flag_idx):
        if flag_idx in range(len(itm.flags)):
            return bool(itm.flags[flag_idx])

    @staticmethod  
    def children_flagged(itm,flag_idx):
        if flag_idx in range(len(itm.flags)):
            if itm.n_children() > 0:
                return any([self.children_flagged(c_itm,flag_idx) for c_itm in itm.children])
            else:
                return bool(itm.flags[flag_idx])

    @staticmethod
    def set_flagged(itm,flag_idx,val):
        itm.flags[flag_idx] = bool(val)

    def set_all_flagged(self,itm,flag_idx,val):
       self.set_flagged(itm,flag_idx,val)
       for c_itm in itm.children:
           self.set_all_flagged(c_itm,flag_idx,val)

    def get_flagged_idxs(self,flag_idx,idx=None,val=True):
        if idx is None:
            idx = self.root_index()
        itm = self.get_item(idx) 
        if self.is_flagged(itm,flag_idx) == val:
            sel_idxs.append(idx)
            for c_row in range(itm.n_children()):
                c_idx = self.index(c_row,0,idx)
                sel_idxs = sel_idxs + self.get_flagged_idxs(flag_idx,c_idx,val)
        return sel_idxs

    def columnCount(self,parent):
        """
        Let TreeSelectionModel have n_flags+1 columns:
        one for the TreeItem tag, the rest for flags 
        """
        return 1+self.n_flags() 

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return super(TreeSelectionModel,self).data(section,orientation,data_role) 
        elif (data_role == QtCore.Qt.DisplayRole and section < self.n_flags()+1):
            return self.flag_names[section-1]
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
            return super(TreeSelectionModel,self).data(idx,data_role)
        elif data_role == QtCore.Qt.CheckStateRole: 
            return self.check_state(itm,idx.column()-1)
        else:
            # Not column 0, not CheckStateRole: return None
            return None

    def check_state(self,itm,flag_idx):
        if self.is_flagged(itm,flag_idx):
            return QtCore.Qt.Checked
        elif self.children_flagged(itm,flag_idx):
            return QtCore.Qt.PartiallyChecked
        else:
            return QtCore.Qt.Unchecked

    # Need flags to reflect checkability
    def flags(self, idx):
        if not idx.isValid():
            return None
        elif idx.column() == 0:
            return super(TreeSelectionModel,self).flags(idx)
        else:
            return super(TreeSelectionModel,self).flags(idx) | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate
    
    # Ui-editable QAbstractItemModel subclasses must implement setData(index,value[,role])
    def setData(self,idx,value,data_role):
        if idx.column() == 0:
            return super(TreeSelectionModel,self).setData(index,value,data_role)
        elif data_role == QtCore.Qt.CheckStateRole:
            itm = self.get_item(idx)
            self.set_flagged(itm,idx.column()-1,value)
            self.dataChanged.emit(idx,idx)
            return True
        else:
            return super(TreeSelectionModel,self).setData(index,value,data_role)

