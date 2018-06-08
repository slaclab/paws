from PySide import QtCore

class ListModel(QtCore.QAbstractListModel):
    """
    Class for list management with a QAbstractListModel.
    Implements required virtual methods rowCount() and data().
    Resizeable ListModels must implement insertRows(), removeRows().
    If a nicely labeled header is desired, implement headerData().
    """

    def __init__(self,input_list=[],parent=None):
        super(ListModel,self).__init__(parent)
        self._list_data = []
        self._enabled = []
        if input_list is not None:
            for thing in input_list:
                self.append_item(thing)
        
    def append_item(self,thing):
        ins_row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(),ins_row,ins_row)
        self._list_data.insert(ins_row,thing) 
        self.endInsertRows()
        self._enabled.insert(ins_row,True)
        idx = self.index(ins_row,0,QtCore.QModelIndex())

    def remove_item(self,row):
        self.beginRemoveRows(QtCore.QModelIndex(),row,row)
        self._list_data.pop(row) 
        self.endRemoveRows()
        self._enabled.pop(row) 

    #def list_data_changed(self):
    #    for r in range(len(self._list_data)):
    #        idx = self.index(r,0,QtCore.QModelIndex())
    #        self.dataChanged.emit(idx,idx)

    def set_enabled(self,row):
        self._enabled[row] = True

    def set_disabled(self,row):
        self._enabled[row] = False

    def list_data(self):
        return self._list_data

    def flags(self,idx):
        if self._enabled[idx.row()]:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.NoItemFlags

    def n_items(self):
        return self.rowCount()

    def rowCount(self,parent=QtCore.QModelIndex()):
        return len(self._list_data)

    def columnCount(self,parent=QtCore.QModelIndex()):
        return 1

    def data(self,idx,data_role):
        if not idx.isValid():
            return None
        elif (data_role == QtCore.Qt.DisplayRole
        or data_role == QtCore.Qt.ToolTipRole 
        or data_role == QtCore.Qt.StatusTipRole
        or data_role == QtCore.Qt.WhatsThisRole):
            return str(self._list_data[idx.row()])
        else:
            return None
        #    print 'data at row {}: {}'.format(idx.row(),self._list_data[idx.row()])
        #    print 'DATA IS NONE'

    def get_item(self,idx):
        return self._list_data[idx.row()]

    def insertRows(self,row,count):
        self.beginInsertRows(QtCore.QModelIndex(),row,row+count-1)
        for j in range(row,row+count):
            self._list_data.insert(j,None)
        self.endInsertRows()

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if all([r in range(self.rowCount(parent)) for r in range(row,count)]):
            self.beginRemoveRows(parent,row,row+count-1)
            for j in range(row,row+count)[::-1]:
                self._list_data.pop(j)
            self.endRemoveRows()
            return True
        else:
            return False

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "list: {} item(s)".format(self.rowCount(QtCore.QModelIndex()))
        else:
            return None

class PluginListModel(ListModel):
    """Just a ListModel with overloaded headerData"""

    def __init__(self,input_list=[],parent=None):
        super(PluginListModel,self).__init__(input_list,parent)

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} plugin(s) available".format(self.rowCount(QtCore.QModelIndex()))
        else:
            return None



