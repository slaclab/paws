from PySide import QtCore

import core.operations as ops

class OpManager(QtCore.QAbstractListModel):
    """
    Class for managing operations.
    Should be able to add operations to the list
    and remove selected operations from the list.
    Operations will be displayed in operation builder ui,
    use data() to ensure that the display is intelligible
    """

    def __init__(self,**kwargs):
        # TODO: build operation list from core/operations/__init__.py 
        self._op_list = [] 
        super(OpManager,self).__init__()

    def load_ops(self,op_list):
        for op in op_list:
            self.add_op(op)

    # add an Operation to the list
    def add_op(self,new_op):
        insertion_row = self.rowCount()
        self.beginInsertRows(
        QtCore.QModelIndex(),insertion_row,insertion_row)
        # Insertion occurs between notification methods
        self._op_list.insert(insertion_row,new_op)
        self.endInsertRows()

    # remove an Operation from the list 
    def remove_op(self,removal_indx):
        removal_row = removal_indx.row()
        self.beginRemoveRows(
        QtCore.QModelIndex(),removal_row,removal_row)
        # Removal occurs between notification methods
        self._op_list.pop(removal_row)
        self.endRemoveRows()

    def list_ops(self):
        return [op.__name__ for op in self._op_list]

    # get an Operation from the list by its name 
    def get_op_byname(self,op_name):
        for op in self._op_list:
            if op.__name__ == op_name:
                return op
        return None

    # get index of an operation by its name
    def get_index_byname(self,op_name):
        for i in range(len(self._op_list)):
            op = self._op_list[i]
            if op.__name__ == op_name:
                return i 
        return None

    # get an Operation from the list by its QModelIndex
    def get_op(self,indx):
        return self._op_list[indx.row()]
 
    # QAbstractItemModel subclass must implement rowCount()
    def rowCount(self,parent=QtCore.QModelIndex()):
        return len(self._op_list)
 
    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,indx,data_role):
        if (not indx.isValid()
            or indx.row() > len(self._op_list)):
            return None
        if data_role == QtCore.Qt.DisplayRole:
            return self._op_list[indx.row()].__name__
        elif data_role == QtCore.Qt.ToolTipRole:
            return self._op_list[indx.row()]().description()
        else:
            return None

    # QAbstractItemModel subclass should implement 
    # headerData(int section,Qt.Orientation orientation[,role=Qt.DisplayRole])
    def headerData(self,section_dummy,orientation_dummy,data_role):
        # TODO: ensure this header is visible.
        if data_role == QtCore.Qt.DisplayRole:
            return "{} operation(s) loaded".format(self.rowCount())
        else:
            return None

    # Expandable QAbstractItemModel subclass should implement
    # insertRows(row,count[,parent=QModelIndex()])
    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        # Signal listeners that rows are about to be born
        self.beginInsertRows(parent,row,row+count-1)
        for indx in range(row,row+count):
            self._op_list.insert(indx,None)
        # Signal listeners that we are done inserting rows
        self.endInsertRows()

    # Shrinkable QAbstractItemModel subclass should implement
    # removeRows(row,count[,parent=QModelIndex()])
    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        # Signal listeners that rows are about to die
        self.beginRemoveRows(parent,row,row+count-1)
        for indx in range(row,row+count):
            self._op_list.pop(indx)
        # Signal listeners that we are done removing rows
        self.endRemoveRows()

    # Editable QAbstractItemModel subclasses must implement
    # setData(index,value[,role])
    #def setData(self,index,value):
    #    self._img_list.insert(index,value)


