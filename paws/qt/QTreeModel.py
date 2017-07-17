from PySide import QtCore

from ..core.models.TreeModel import TreeModel

class QTreeModel(QtCore.QAbstractItemModel):
    """
    A Qt Model-View interface for a TreeModel.
    Required virtual methods: index(), parent(), rowCount(), columnCount(), and data().
    Resizeable TreeModels should implement
    insertRows(), removeRows(), insertColumns(), and removeColumns().
    To customize the header in QAbstractItemViews, implement headerData().
    """

    def __init__(self,trmod=TreeModel()):
        super(QTreeModel,self).__init__()
        self._tree=TreeModel()
        if isinstance(trmod,TreeModel):
            for c_tag in trmod.root_tags():
                self.set_item(c_tag,trmod[c_tag])
            self._tree=trmod

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
            p_itm = self.get_from_index(p_idx)
            if row < p_itm.n_children() and row >= 0:
                return self.createIndex(row,col,p_itm.children[row])
            else:
                return QtCore.QModelIndex()

    def root_index(self):
        return self.createIndex(0,0,self._tree._root_item)

    def root_item(self):
        return self._tree._root_item

    def get_from_index(self,idx=QtCore.QModelIndex()):
        """
        For a valid QModelIndex, return idx.internalPointer().
        For an invalid index, return None.
        """
        if idx.isValid():
            return idx.internalPointer() 
        else:
            return None 

    def get_data_from_index(self,idx=QtCore.QModelIndex()):
        uri = self.get_uri_of_index(idx)
        return self._tree.get_data_from_uri(uri)

    def get_uri_of_index(self,idx):
        itm = self.get_from_index(idx)
        return self._tree.build_uri(itm)

    def get_index_of_uri(self,uri):
        path = uri.split('.')
        idx = self.root_index()
        for k in path[:-1]:
            itm = self.get_from_index(idx)
            child_keys = [c.tag for c in itm.children]
            idx = self.index(child_keys.index(k),0,idx)
        k = path[-1]
        if k:
            itm = self.get_from_index(idx)
            child_keys = [c.tag for c in itm.children]
            return self.index(child_keys.index(k),0,idx)
        elif k == '':
            return idx 

    def n_children(self,parent_idx=None):
        if parent_idx is None:
            parent_idx = self.root_index()
        return self.rowCount(parent_idx)

    def set_item_at_uri(self,itm_uri,itm_data):
        if '.' in itm_uri:
            parent_uri = itm_uri[:itm_uri.rfind('.')]
            #if self._tree.contains_uri(parent_uri):
            parent_idx = self.get_index_of_uri(parent_uri)
            #else:
            #    parent_idx = self.build_to_uri(parent_uri)
            #parent_idx = self.get_index_of_uri(parent_uri)
            itm_tag = itm_uri[itm_uri.rfind('.')+1:]
        else:
            parent_idx = self.root_index()
            itm_tag = itm_uri
        self.set_item(itm_tag,itm_data,parent_idx)        

    #def build_to_uri(self,uri=''):
    #    idx = self.root_index()
    #    if '.' in uri:
    #        parent_uri = uri[:uri.rfind('.')]
    #        if self._tree.contains_uri(parent_uri):
    #            idx = self.get_index_of_uri(parent_uri)
    #        else:
    #            idx = self.build_to_uri(parent_uri)
    #        k = uri.split('.')[-1]
    #        if k == '':
    #            return idx 
    #        elif k is not None:
    #            self.set_item(k,None,idx)
    #            return self.get_index_of_uri(uri) 

    def set_item(self,itm_tag,itm_data=None,parent_idx=None):
        if parent_idx is None:
            parent_idx = self.root_index()
        parent_itm = self.get_from_index(parent_idx)
        parent_uri = self.get_uri_of_index(parent_idx)
        if parent_uri:
            itm_uri = parent_uri+'.'+itm_tag
        else:
            itm_uri = itm_tag
        # add TreeItems to index the new model content:
        # have to implement this differently than TreeModel
        # to inject calls to beginInsertRows and endInsertRows.        
        treedata = self._tree.build_tree(itm_data)
        self.tree_update(parent_idx,itm_tag,treedata)
        # store the data:
        # self._tree.tree_update() will be called with no effect. 
        self._tree.set_item(itm_uri,itm_data)
        #if isinstance(treedata,dict):
        #    itm_idx = self.get_index_of_uri(itm_uri)
        #    # also store any children
        #    for k,val in treedata.items():
        #        child_uri = itm_uri+'.'+k
        #        if not self._tree.contains_uri(child_uri):
        #            if isinstance(itm_data,list):
        #                self.set_item(k,itm_data[int(k)],itm_idx)
        #            else:
        #                # Note- parent item data needs to implement __getitem__
        #                self.set_item(k,itm_data[k],itm_idx) 
        # signal dataChanged down the tree
        child_keys = [c.tag for c in parent_itm.children]
        itm_idx = self.index(child_keys.index(itm_tag),0,parent_idx)
        self.tree_dataChanged(itm_idx) 

    def tree_update_at_uri(self,itm_uri,itm_data):
        if '.' in itm_uri:
            parent_uri = itm_uri[:itm_uri.rfind('.')]
            parent_idx = self.get_index_of_uri(parent_uri)
            itm_tag = itm_uri[itm_uri.rfind('.')+1:]
        else:
            parent_idx = self.root_index()
            itm_tag = itm_uri
        self.tree_update(parent_idx,itm_tag,self._tree.build_tree(itm_data))        

    def tree_update(self,parent_idx,itm_tag,itm_tree):
        parent_itm = self.get_from_index(parent_idx)
        child_keys = [c.tag for c in parent_itm.children]
        if itm_tag in child_keys:
            # Find existing itm under parent.
            itm_row = child_keys.index(itm_tag)
            itm = parent_itm.children[itm_row]
            idx = self.index(itm_row,0,parent_idx)
            # Remove any children that do not represent the new itm_tree data
            new_keys = []
            if isinstance(itm_tree,dict):
                new_keys = itm_tree.keys()
            for gc_row in range(itm.n_children())[::-1]:
                gc_itm = itm.children[gc_row]
                if not gc_itm.tag in new_keys:
                    #rm_row = [gc.tag for gc in itm.children].index(grandchild_itm.tag)
                    self.beginRemoveRows(idx,gc_row,gc_row)
                    itm.children.pop(gc_row) 
                    self.endRemoveRows()
        else:
            # Else, put a new TreeItem at the end row
            itm_row = self.n_children(parent_idx)
            itm = self._tree.create_tree_item(parent_itm,itm_tag)
            self.beginInsertRows(parent_idx,itm_row,itm_row)
            parent_itm.children.insert(itm_row,itm)
            self.endInsertRows()
        # If needed, get the index of the new item and recurse 
        if isinstance(itm_tree,dict):
            itm_idx = self.index(itm_row,0,parent_idx)
            for tag,val in itm_tree.items():
                #self.tree_update(itm_idx,tag,self._tree.build_tree(val))
                self.tree_update(itm_idx,tag,val)

    def remove_item(self,itm_tag,parent_idx=None):
        if parent_idx is None:
            parent_idx = self.root_index()
        parent_itm = self.get_from_index(parent_idx)
        child_keys = [c.tag for c in parent_itm.children]
        rm_row = child_keys.index(itm_tag)
        rm_idx = self.index(rm_row,0,parent_idx)
        rm_itm = self.get_from_index(rm_idx) 
        rm_uri = self._tree.build_uri(rm_itm)
        self.beginRemoveRows(parent_idx,rm_row,rm_row)
        self._tree.remove_item(rm_uri)
        #parent_itm.children.pop(rm_row)
        self.endRemoveRows()
        #self.dataChanged.emit(rm_idx,rm_idx)
        self.tree_dataChanged(parent_idx)

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
        itm = self.get_from_index(idx)
        if itm == self._tree._root_item:
            return QtCore.QModelIndex()
        parent_itm = itm.parent
        if parent_itm == self._tree._root_item:
            return self.root_index()
        parent_tag = parent_itm.tag
        grandparent_itm = parent_itm.parent
        parent_keys = [p.tag for p in grandparent_itm.children]
        parent_row = parent_keys.index(parent_tag)
        return self.createIndex(parent_row,0,grandparent_itm.children[parent_row])
        
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
            parent_itm = self.get_from_index(parent_idx)
            return parent_itm.n_children()
    
    # Subclass of QAbstractItemModel must implement columnCount()
    def columnCount(self,parent=QtCore.QModelIndex()):
        """
        TreeModels by default have one column.
        More columns can be added by reimplementing columnCount()
        and then providing for them in TreeModel.data().
        """
        return 1

    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,itm_idx,data_role):
        """
        TreeModel's implementation of data() 
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
        if ((data_role == QtCore.Qt.DisplayRole
        or data_role == QtCore.Qt.ToolTipRole 
        or data_role == QtCore.Qt.StatusTipRole
        or data_role == QtCore.Qt.WhatsThisRole)
        and itm_idx.column() == 0):
            itm = self.get_from_index(itm_idx)
            return itm.tag
        else:
            return None

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} item(s)".format(self.n_children())
        else:
            return None

