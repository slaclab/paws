from PySide import QtCore


class WfManager(QtCore.QAbstractListModel):
    """
    Class for managing a workflow built from slacx operations.
    """

    def __init__(self,**kwargs):
        self._wf = {}       # this will be a dict managed by a dask graph 
        self._n_ops = 0     # private op counter
        super(WfManager,self).__init__()

    def check_wf(self):
        """
        Check the dependencies of the workflow.
        Ensure that all loaded operations have inputs that make sense
        """
        pass

    def next_op(self):
        self._n_ops += 1
        return self._n_ops

    # add an Operation to the workflow 
    def add_op(self,new_op,op_input_tags):
        op_key = 'op'+str(self.next_op())
        op_computation = tuple([new_op.run] + [op_input_tags])

       ####### WE ARE HERE. #######

        insertion_row = self.rowCount()
        self.beginInsertRows(
        QtCore.QModelIndex(),insertion_row,insertion_row)
        # Insertion occurs between notification methods
        self._wf[op_key]=(new_op.run, new_op.inputs())
        self.endInsertRows()

    # remove an Operation from the workflow 
    def remove_op(self,removal_indx):
        removal_row = removal_indx.row()
        self.beginRemoveRows(
        QtCore.QModelIndex(),removal_row,removal_row)
        # Removal occurs between notification methods
        self._wf.pop(removal_row)
        self.endRemoveRows()

    # get an Operation from the workflow by its QModelIndex
    def get_op(self,indx):
        return self._wf[indx.row()]
 
    # QAbstractItemModel subclass must implement rowCount()
    def rowCount(self,parent=QtCore.QModelIndex()):
        return len(self._wf)
 
    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,indx,data_role):
        if (not indx.isValid()
            or indx.row() > len(self._wf)):
            return None
        if data_role == QtCore.Qt.DisplayRole:
            return type( self._wf[indx.row()] ).__name__
        elif data_role == QtCore.Qt.ToolTipRole:
            return self._wf[indx.row()].description()
        else:
            return None

    # QAbstractItemModel subclass should implement 
    # headerData(int section,Qt.Orientation orientation[,role=Qt.DisplayRole])
    def headerData(self,section_dummy,orientation_dummy,data_role):
        if data_role == QtCore.Qt.DisplayRole:
            return "workflow: {} total operation(s)".format(self.rowCount())
        else:
            return None

    # Expandable QAbstractItemModel subclass should implement
    # insertRows(row,count[,parent=QModelIndex()])
    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        # Signal listeners that rows are about to be born
        self.beginInsertRows(parent,row,row+count-1)
        for indx in range(row,row+count):
            self._wf.insert(indx,None)
        # Signal listeners that we are done inserting rows
        self.endInsertRows()

    # Shrinkable QAbstractItemModel subclass should implement
    # removeRows(row,count[,parent=QModelIndex()])
    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        # Signal listeners that rows are about to die
        self.beginRemoveRows(parent,row,row+count-1)
        for indx in range(row,row+count):
            self._wf.pop(indx)
        # Signal listeners that we are done removing rows
        self.endRemoveRows()

    # Editable QAbstractItemModel subclasses must implement
    # setData(index,value[,role])
    #def setData(self,index,value):
    #    self._img_list.insert(index,value)


