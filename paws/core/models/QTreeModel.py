from PySide import QtCore

from .TreeItem import TreeItem
from .TreeModel import TreeModel

class QTreeModel(QtCore.QAbstractItemModel):
    """
    Class for tree management with a QAbstractItemModel.
    Required virtual methods index(), parent(), rowCount(), columnCount(), and data().
    Resizeable TreeModels should implement
    insertRows(), removeRows(), insertColumns(), and removeColumns().
    To customize the header in QAbstractItemViews, implement headerData().
    """

    def __init__(self):
        super(QTreeModel,self).__init__()
        # a TreeItem with no parent is the root of the tree
        self._root_item = TreeItem(None,'ROOT')
        # the tree data is all stored in a TreeModel
        self._tree = TreeModel()
        #self._root_item.data = TreeModel() 
        #self._root_item.data = self._tree

    # Subclass of QAbstractItemModel must implement index()
    def index(self,row,col,p_idx):
        """
        Returns QModelIndex address of int row, int col, under QModelIndex p_idx.
        If a row, column, p_idx combination is invalid, return QModelIndex().
        """
        if not p_idx.isValid():
            if row == 0:
                return self.root_index()
            else:
                return QtCore.QModelIndex()
        else:
            p_itm = self.get_from_idx(p_idx)
            if row < p_itm.n_children() and row >= 0:
                return self.createIndex(row,col,p_itm.children[row])
            else:
                return QtCore.QModelIndex()

    def root_index(self):
        return self.createIndex(0,0,self._root_item)

    def get_from_idx(self,idx=QtCore.QModelIndex()):
        """
        For a valid QModelIndex, return idx.internalPointer().
        For an invalid index, return None.
        """
        if idx.isValid():
            return idx.internalPointer() 
        else:
            return None 

    def get_from_uri(self,uri):
        try:
            path = uri.split('.')
            itm = self._root_item
            for k in path[:-1]:
                child_keys = [c.tag for c in itm.children]
                itm = itm.children[child_keys.index(k)]
            k = path[-1]
            if k:
                child_keys = [c.tag for c in itm.children]
                return itm.children[child_keys.index(k)]
            elif k == '':
                return itm 
        except Exception as ex:
            msg = '\n[{}] Encountered an error while fetching uri {}\n'.format(__name__,uri)
            ex.message = msg + ex.message
            raise ex

    def get_idx_of_uri(self,uri):
        try:
            path = uri.split('.')
            idx = self.root_index()
            for k in path[:-1]:
                itm = self.get_from_idx(idx)
                child_keys = [c.tag for c in itm.children]
                idx = self.index(child_keys.index(k),0,idx)
            k = path[-1]
            if k:
                itm = self.get_from_idx(idx)
                child_keys = [c.tag for c in itm.children]
                return self.index(child_keys.index(k),0,idx)
            elif k == '':
                return idx 
        except Exception as ex:
            msg = '\n[{}] Encountered an error while indexing uri {}\n'.format(__name__,uri)
            ex.message = msg + ex.message
            raise ex

    def get_data_from_uri(self,uri):
        return self._tree.get_from_uri(uri)

    def get_data_from_idx(self,idx):
        uri = self.build_uri(idx)
        return self.get_data_from_uri(uri)

    def build_uri(self,idx):
        """
        Build a URI for the TreeItem at idx 
        by prepending its parent tags with '.' as a delimiter.
        """
        itm = self.get_from_idx(idx)
        uri = itm.tag
        while not itm == self._root_item:
            uri = itm.tag+"."+uri
            itm = itm.parent
        return uri

    def set_item(self,itm_tag,itm_data=None,parent_idx=None):
        if parent_idx is None:
            parent_idx = self.root_index()
        parent_uri = self.build_uri(parent_idx)
        itm_uri = parent_uri+'.'+itm_tag
        # store the data in the underlying TreeModel
        self._tree.set_uri(itm_uri,itm_data)
        # add TreeItems to index the new TreeModel content 
        self.tree_update(parent_idx,itm_tag,itm_data)
        child_keys = [c.tag for c in parent_itm.children]
        itm_idx = self.index(child_keys.index(itm_tag),0,parent_idx)
        self.tree_dataChanged(itm_idx) 

    def tree_update(self,parent_idx,itm_tag,itm_data):
        parent_itm = self.get_from_idx(parent_uri)
        child_keys = [c.tag for c in parent_itm.children]
        if itm_tag in child_keys:
            # Find the row of existing itm_tag under parent,
            itm_row = child_keys.index(itm_tag)
            itm = parent_itm.children[itm_row]
        else:
            # Else, put a new TreeItem at the end row
            itm_row = self.item_count(parent_idx)
            itm = TreeItem(parent_itm,itm_tag)
            self.beginInsertRows(parent_idx,itm_row,itm_row)
            parent_itm.children.insert(itm_row,itm)
            self.endInsertRows()
        # If needed, get the index of the new item and recurse 
        if isinstance(itm_data,dict):
            itm_idx = self.index(itm_row,0,parent_idx)
            for tag,val in itm_data.items():
                self.tree_update(itm_idx,tag,val)

    def remove_item(self,itm_tag,parent_idx=None):
        if parent_idx is None:
            parent_idx = self.root_index()
        parent_uri = self.build_uri(parent_idx)
        itm_uri = parent_uri+'.'+itm_tag
        # remove the data from the underlying TreeModel
        self._tree.delete_uri(itm_uri)
        # remove the corresponding subtree or TreeItem.
        parent_itm = self.get_from_idx(parent_idx)
        child_keys = [c.tag for c in parent_itm.children]
        rm_row = child_keys.index(itm_tag)
        self.beginRemoveRows(parent_idx,rm_row,rm_row)
        parent_itm.children.pop(rm_row)
        self.endRemoveRows()
        self.dataChanged.emit(rm_idx,rm_idx)

    def item_count(self,parent_idx=None):
        if parent_idx is None:
            parent_idx = self.root_index()
        return self.rowCount(parent_idx) 

    def tree_dataChanged(self,idx):
        itm = idx.internalPointer()
        self.dataChanged.emit(idx,idx)
        for c_row in range(itm.n_children())[::-1]:
            c_idx = self.index(c_row,0,idx)
            self.tree_dataChanged(c_idx)

    # Subclass of QAbstractItemModel must implement parent()
    def parent(self,idx):
        """
        Returns QModelIndex of parent of item at QModelIndex index
        """
        itm = self.get_from_idx(idx)
        if itm == self._root_item:
            return QtCore.QModelIndex()
        parent_itm = itm.parent
        if parent_itm == self._root_item:
            return self.root_index()
        parent_tag = parent_itm.tag
        grandparent_itm = parent_itm.parent
        parent_keys = [p.tag for p in grandparent_itm.children]
        parent_row = parent_keys.index(parent_tag)
        return self.createIndex(row,0,grandparent_itm.children[parent_row])
        
    # Subclass of QAbstractItemModel must implement rowCount()
    def rowCount(self,parent_idx=QtCore.QModelIndex()):
        """
        Either give the number of top-level items,
        or count the children of parent
        """
        if not parent_idx.isValid():
            # there is only 1 root item 
            return 1
        else:
            # count children of parent item
            parent_itm = self.get_from_idx(parent_idx)
            return parent_itm.n_children()
    
    # Subclass of QAbstractItemModel must implement columnCount()
    def columnCount(self,parent=QtCore.QModelIndex()):
        """
        QTreeModels by default have one column.
        More columns can be supported 
        by providing data for them in QTreeModel.data().
        """
        return 1

    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,itm_idx,data_role):
        """
        QTreeModel's implementation of data() 
        returns the tag of the TreeItem at itm_idx.
        This is only if itm_idx.column() == 0.
        Subclasses can reimplement data() 
        to provide meaningful output for other columns,
        and may consider falling back on super().data() 
        if itm_idx.column() == 0.
        """
        if (not itm_idx.isValid()):
            return None
        #if itm_idx == self.root_index():
        #    return None
        #itm = itm_idx.internalPointer()
        itm = self.get_from_idx(itm_idx)
        if ((data_role == QtCore.Qt.DisplayRole
        or data_role == QtCore.Qt.ToolTipRole 
        or data_role == QtCore.Qt.StatusTipRole
        or data_role == QtCore.Qt.WhatsThisRole)
        and itm_idx.column() == 0):
            return itm.tag
        else:
            return None

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} item(s)".format(self.item_count())
        else:
            return None

    # Expandable QAbstractItemModel subclass should implement
    # insertRows(row,count[,parent=QModelIndex()])
    #def insertRows(self,row,count,parent_idx=QtCore.QModelIndex()):
    #    if parent_idx.isValid():
    #        parent_itm = self.get_from_idx(parent_idx)
    #        parent_uri = self.build_uri(parent_idx)
    #        #self.beginInsertRows(parent_idx,row,row+count-1)
    #        for j in range(row,row+count)[::-1]:
    #            dummy_uri = self._tree.make_unique_uri(parent_uri+'.'+'dummy')
    #            dummy_tag = dummy_uri.split('.')[-1]
    #            self.add_item(dummy_tag,None,parent_idx)
    #            #new_itm = TreeItem(parent_itm,dummy_tag)
    #            #parent_itm.children.insert(j,new_itm)
    #        #self.endInsertRows()
    #        return True
    #    else:
    #        return False

    # Shrinkable QAbstractItemModel subclass should implement
    # removeRows(row,count[,parent=QModelIndex()])
    #def removeRows(self,row,count,parent_idx=QtCore.QModelIndex()):
    #    if parent_idx.isValid():
    #        parent_itm = self.get_from_idx(parent_idx) 
    #        self.beginRemoveRows(parent,row,row+count-1)
    #        for j in range(row,row+count)[::-1]:
    #            del_idx = self.index(j,0,parent)
    #            del_itm = p_itm.children.pop(j)
    #            del_itm.deleteLater()
    #        self.endRemoveRows()
    #        return True
    #    else:
    #        return False


    #def iter_indexes(self,parent=QtCore.QModelIndex()):
    #    """Provide a list of the QModelIndexes held in the tree"""
    #    if parent.isValid():
    #        idxs = [parent]
    #        itms = self.get_from_idx(parent).children
    #        for j in range(len(itms)):
    #            itm = itms[j]
    #            idx = self.index(j,0,parent)
    #            if itm.n_children > 0:
    #                idxs = idxs + self.iter_indexes(idx)
    #        return idxs

    #def tree_datachanged():
        #"""
        #Call this function to store x_new as TreeItem.data at idx 
        #and then build/update/prune the subtree rooted at that item
        #based on the result of self.build_dict(x_new).
        #x_new may be an entirely new object, an altered copy of an old object,
        #or even the same object that already exists at idx
        #(i.e. it may already be that idx.internalPointer().data == x_new),
        #in which case any updates that happened to x_new since the last tree_update
        #will be percolated down the subtree. 
        #"""
        #itm = idx.internalPointer()
        #itm.data = x_new
        #x_new_dict = self.build_dict(x_new)
        #obsolete_child_rows = [] 
        #for j in range(itm.n_children()):
        #    if not itm.children[j].tag() in x_new_dict.keys():
        #        obsolete_child_rows.append( j )
        #for j in obsolete_child_rows[::-1]:
        #    obsolete_child_idx = self.index(j,0,idx)
        #    self.remove_item(obsolete_child_idx)
        #child_tags = self.list_child_tags(idx)
        #for k in x_new_dict.keys():
        #    if not k in child_tags:
        #        c_idx = self.add_item(k,x_new_dict[k],idx)
        #        self.tree_update(c_idx,x_new_dict[k])
        #self.tree_dataChanged(idx) 

        #itm.data = itm_data
        #idx = self.index(ins_row,0,parent) 
        #self.tree_dataChanged(idx)
        #return idx       

        #parent = rm_itm.parent
        #if parent.isValid():
        #    #rm_itm = rm_idx.internalPointer()
        #    #for child_row in range(rm_itm.n_children())[::-1]:
        #    #    child_idx = self.index(child_row,0,rm_idx)
        #    #    self.remove_item(child_idx)
        #    rm_row = rm_idx.row()
        #    self.beginRemoveRows(parent,rm_row,rm_row)
        #    rm_itm = parent.internalPointer().children.pop(rm_row)
        #    self.endRemoveRows()
        #    rm_itm.deleteLater()
        #    #del rm_itm
        #    rm_itm = None
        #self.tree_dataChanged(rm_idx) 
        #self.tree_dataChanged(self.root_index()) 


