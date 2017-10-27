from collections import OrderedDict

from PySide import QtCore

from ..qt.QTreeSelectionModel import QTreeSelectionModel
from ..core.operations.OpManager import OpManager

class QOpManager(OpManager,QTreeSelectionModel):
    """
    A QTreeSelectionModel for interacting with TreeModel OpManager.
    """

    def __init__(self):
        super(QOpManager,self).__init__()

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operations available".format(self.n_ops())
        else:
            return super(QOpManager,self).headerData(section,orientation,data_role) 

    def flags(self,idx):
        d = self.get_data_from_index(idx)
        if isinstance(d,dict) and not idx.column()==0:
            # Don't allow user to control enable flag on categories, at least for now
            # TODO: Consider allowing user to enable/disable entire categories
            #return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsTristate
            return QtCore.Qt.NoItemFlags
        else:
            return super(QOpManager,self).flags(idx)

    # Override setData to handle operation enable/disable via check boxes. 
    def setData(self,idx,val,data_role):
        if idx.column() == 0:
            return super(QOpManager,self).setData(index,val,data_role)
        elif data_role == QtCore.Qt.CheckStateRole:
            itm = self.get_from_index(idx)
            op_uri = self.get_uri_of_index(idx)
            try:
                self.set_op_enabled(op_uri,bool(val))
            except Exception as ex:
                msg = str('Failed to enable Operation {}. '.format(op_uri)
                + 'Error message: {}'.format(ex.message))
                self.logmethod(msg)
                return False
            self.set_flagged(itm,self.default_flags.keys()[idx.column()-1],val)
            self.dataChanged.emit(idx,idx)
            return True
        else:
            return super(QTreeSelectionModel,self).setData(index,val,data_role)


