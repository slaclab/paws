import string 

from PySide import QtCore

class ListModel(QtCore.QAbstractListModel):
    """
    Class for list management with a QAbstractListModel.
    Implements required virtual methods index(), parent(), rowCount(), and data().
    Resizeable ListModels must implement insertRows(), removeRows().
    If a nicely labeled header is desired, one should implement headerData().
    """

    def __init__(self,input_list=[],parent=None):
        super(ListModel,self).__init__(parent)
        self.list_data = []
        self.enabled = []
        for thing in input_list:
            self.append_item(thing)
            self.enabled.append(True)
        

    def append_item(self,thing):
        ins_row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(),ins_row,ins_row+1)
        self.list_data.append(thing) 
        self.endInsertRows()

    def set_disabled(self,row):
        """Change self.flags() for idx such that it does not allow the item to be selected"""
        self.enabled[row] = False

    def flags(self,idx):
        if self.enabled[idx.row()]:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.NoItemFlags

    # Subclass of QAbstractListModel must implement rowCount()
    def rowCount(self,parent=QtCore.QModelIndex()):
        return len(self.list_data)

    # QAbstractListModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,idx,data_role):
        return self.list_data[idx.row()]
        #if data_role == QtCore.Qt.DisplayRole:
        #else:
        #    return None

    # Expandable QAbstractItemModel subclass should implement
    # insertRows(row,count[,parent=QModelIndex()])
    def insertRows(self,row,count):
        # Signal listeners that rows are about to be born
        self.beginInsertRows(QtCore.QModelIndex(),row,row+count-1)
        for j in range(row,row+count):
            self.list_data.insert(j,None)
        # Signal listeners that we are done inserting rows
        self.endInsertRows()

    # Shrinkable QAbstractItemModel subclass should implement
    # removeRows(row,count[,parent=QModelIndex()])
    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        # Signal listeners that rows are about to die
        self.beginRemoveRows(parent,row,row+count-1)
        for j in range(row,row+count)[::-1]:
            self.list_items.pop(j)
        # Signal listeners that we are done removing rows
        self.endRemoveRows()

    # QAbstractItemModel subclass should implement 
    # headerData(int section,Qt.Orientation orientation[,role=Qt.DisplayRole])
    # note: section arg indicates row or column number, depending on orientation
    def headerData(self,section,orientation,data_role):
        return None


