from PySide import QtCore

class TreeModel(QtCore.QAbstractItemModel):
    """
    Class for tree management with a QAbstractItemModel.
    Implements required virtual methods index(), parent(), rowCount().
    Other required virtual methods are columnCount() and data():
    these should be implemented by subclassing of TreeModel.
    Resizeable TreeModels must implement: 
    insertRows(), removeRows(), insertColumns(), removeColumns()
    If nicely labeled headers are desired, one should implement
    headerData().
    """

    def __init__(self):
        super(TreeModel,self).__init__()
        # keep root items in a TreeItem list
        self.root_items = []    

    # Subclass of QAbstractItemModel must implement index()
    def index(self,row,col,parent):
        """
        Returns QModelIndex address of int row, int col, under QModelIndex parent.
        """
        if not parent.isValid():
            # If parent is not a valid index, a top level item is being queried.
            return self.createIndex(row,col,self.root_items[row])
        else:
            # We need to grab the parent from its QModelIndex...
            p_item = parent.internalPointer()
            # and return the index of the child at row
            return self.createIndex(row,col,p_item.children[row])

    # Subclass of QAbstractItemModel must implement parent()
    def parent(self,index):
        """
        Returns QModelIndex of parent of item at QModelIndex index
        """
        # Grab this TreeItem from its QModelIndex
        item = index.internalPointer()
        if not item.parent.isValid():
            # We have no parent, therefore a top level item
            return QtCore.QModelIndex()
        else:
            return item.parent
        
    # Subclass of QAbstractItemModel must implement rowCount()
    def rowCount(self,parent):
        """
        Either give the number of top-level items,
        or count the children of parent
        """
        if not parent.isValid():
            # top level parent: count root items
            #print 'number of rows in root_items: {}'.format(len(self.root_items))
            return len(self.root_items)
        else:
            # count children of parent item
            parent_item = parent.internalPointer()
            return parent_item.n_children()
    
    # Subclass of QAbstractItemModel must implement columnCount()
    def columnCount(self,parent):
        """
        In current implementation, all TreeItems only have one column"""
        #if not parent.isValid():
        #    if len(self.root_items) > 1:
        #        return self.root_items[0].n_data() 
        #    else:
        #        return 1
        return 1

    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,item_indx,data_role):
        if (not item_indx.isValid()):
            return None
        item = item_indx.internalPointer()
        if data_role == QtCore.Qt.DisplayRole:
            return item.tag()
        #elif (data_role == QtCore.Qt.ToolTipRole) and len(item.data) > 0:
        #    return type(item.data[0]).__name__ 
        elif (data_role == QtCore.Qt.ToolTipRole 
            or data_role == QtCore.Qt.StatusTipRole
            or data_role == QtCore.Qt.WhatsThisRole):
            return item.long_tag + '\n\n' + item.data_str()
        else:
            return None

    # Expandable QAbstractItemModel subclass should implement
    # insertRows(row,count[,parent=QModelIndex()])
    def insertRows(self,row,count,parent=QtCore.QModelIndex()):
        # Signal listeners that rows are about to be born
        self.beginInsertRows(parent,row,row+count-1)
        if parent.isValid():
            # Get the TreeItem referred to by QModelIndex parent:
            item = parent.internalPointer()
            for j in range(row,row+count):
                item.children.insert(j,None)
        else:
            # Insert rows into self.root_items:
            for j in range(row,row+count):
                self.root_items.insert(j,None)
        # Signal listeners that we are done inserting rows
        self.endInsertRows()

    # Shrinkable QAbstractItemModel subclass should implement
    # removeRows(row,count[,parent=QModelIndex()])
    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        # Signal listeners that rows are about to die
        self.beginRemoveRows(parent,row,row+count-1)
        if parent.isValid():
            # Get the TreeItem referred to by QModelIndex parent:
            item = parent.internalPointer()
            for j in range(row,row+count):
                item.children.pop(j)
        else:
            for j in range(row,row+count):
                self.root_items.pop(j)
        # Signal listeners that we are done removing rows
        self.endRemoveRows()

    # get a TreeItem from the tree by its QModelIndex
    def get_item(self,indx):
        return indx.internalPointer() 

    
