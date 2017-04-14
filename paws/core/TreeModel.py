import string 
from collections import OrderedDict

from PySide import QtCore

from .TreeItem import TreeItem

class TreeModel(QtCore.QAbstractItemModel):
    """
    Class for tree management with a QAbstractItemModel.
    Implements required virtual methods index(), parent(), rowCount().
    Other required virtual methods are columnCount() and data():
    these should be implemented by subclassing of TreeModel.
    Resizeable TreeModels must implement: 
    insertRows(), removeRows(), insertColumns(), removeColumns().
    If nicely labeled headers are desired, one should implement headerData().
    """

    def __init__(self):
        super(TreeModel,self).__init__()
        # keep a TreeItem with no data as the root of the tree
        self._root_item = TreeItem(0,0,QtCore.QModelIndex())
        self._root_item.set_tag('ROOT')
        self._root_item.data = OrderedDict() 

    def root_index(self):
        return self.createIndex(0,0,self._root_item)

    def root_item(self):
        return self._root_item

    def get_item(self,idx=QtCore.QModelIndex()):
        """
        For a valid QModelIndex, return idx.internalPointer().
        For an invalid index, return self._root_item.
        """
        if idx.isValid():
            return idx.internalPointer() 
        else:
            return self._root_item

    def item_count(self,parent=None):
        if parent is None:
            parent = self.root_index()
        return self.rowCount(parent) 

    def add_item(self,itm_tag,itm_data=None,parent=None):
        if parent is None:
            parent = self.root_index()
        ins_row = self.item_count(parent)
        itm = TreeItem(ins_row,0,parent)
        #itm.setParent(self)
        itm.set_tag(itm_tag)
        itm.data = itm_data
        self.beginInsertRows(parent,ins_row,ins_row)
        self.get_item(parent).children.insert(ins_row,itm)
        self.endInsertRows()
        idx = self.index(ins_row,0,parent) 
        self.tree_dataChanged(idx)
        return idx       

    def remove_item(self,rm_idx):
        rm_itm = self.get_item(rm_idx)
        parent = rm_itm.parent
        if parent.isValid():
            #rm_itm = rm_idx.internalPointer()
            #for child_row in range(rm_itm.n_children()):
            #    child_idx = self.index(child_row,0,rm_idx)
            #    self.remove_item(child_idx)
            rm_row = rm_idx.row()
            self.beginRemoveRows(parent,rm_row,rm_row)
            rm_itm = parent.internalPointer().children.pop(rm_row)
            self.endRemoveRows()
            rm_itm.deleteLater()
            #del rm_itm
            rm_itm = None
        self.dataChanged.emit(rm_idx,rm_idx)
        #self.tree_dataChanged(rm_idx) 

    def tree_update(self,idx,x_new):
        """
        Call this function to store x_new as TreeItem.data at idx 
        and then build/update/prune the subtree rooted at that item
        based on the result of self.build_dict(x_new).
        x_new may be an entirely new object, an altered copy of an old object,
        or even the same object that already exists at idx
        (i.e. it may already be that idx.internalPointer().data == x_new),
        in which case any updates that happened to x_new since the last tree_update
        will be percolated down the subtree. 
        """
        itm = idx.internalPointer()
        itm.data = x_new
        x_new_dict = self.build_dict(x_new)
        obsolete_child_rows = [] 
        for j in range(itm.n_children()):
            if not itm.children[j].tag() in x_new_dict.keys():
                obsolete_child_rows.append( j )
        for j in obsolete_child_rows[::-1]:
            obsolete_child_idx = self.index(j,0,idx)
            self.remove_item(obsolete_child_idx)
        child_tags = self.list_child_tags(idx)
        for k in x_new_dict.keys():
            if not k in child_tags:
                c_idx = self.add_item(k,x_new_dict[k],idx)
                self.tree_update(c_idx,x_new_dict[k])
        self.tree_dataChanged(idx) 

    def build_dict(self,x):
        """Build a dict from structured data object x"""
        if isinstance(x,dict):
            d = x 
        elif isinstance(x,list):
            d = OrderedDict(zip([str(i) for i in range(len(x))],x)) 
        else:
            d = {} 
        return d

    def build_uri(self,idx):
        """
        Build a URI for the TreeItem at idx 
        by prepending its parent tags with '.' as a delimiter.
        """
        item_ref = self.get_item(idx)
        item_uri = item_ref.tag()
        #while item_ref.parent.isValid():
        while not item_ref == self._root_item:
            item_uri = item_ref.tag()+"."+item_uri
            item_ref = self.get_item(item_ref.parent)
        return item_uri

    def tree_dataChanged(self,idx):
        self.dataChanged.emit(idx,idx)
        itm = idx.internalPointer()
        for c_row in range(itm.n_children()):
            c_idx = self.index(c_row,0,idx)
            self.tree_dataChanged(c_idx)

    def list_child_tags(self,parent=None):
        """Get a list of tags for TreeItems under parent."""
        #if not parent.isValid():
        #    return [item.tag() for item in self.root_items]
        #else:
        if parent is None:
            parent = self.root_index()
        return [itm.tag() for itm in self.get_item(parent).children]

    def auto_tag(self,prefix):
        """
        Generate the next unique tag from prefix by appending '_x' to it, 
        where x is a minimal nonnegative integer.
        """
        suffix = 0
        goodtag = False
        while not goodtag:
            testtag = prefix+'_{}'.format(suffix)
            if not testtag in self.list_child_tags(self.root_index()): 
                goodtag = True
            else:
                suffix += 1
        return testtag
    
    # test uniqueness and good form of a tag
    def is_tag_free(self,testtag,parent=None):
        """
        Checks for uniqueness and good form of a tag, returns a (bool,string) tuple
        where the bool indicates whether the tag is good, 
        and the string provides explanation if the tag is not good. 
        """
        if parent is None:
            parent = self.root_index()
        spec_chars = string.punctuation 
        spec_chars = spec_chars.replace('_','')
        spec_chars = spec_chars.replace('-','')
        if not testtag:
            return (False, 'Tag is blank')
        elif testtag in self.list_child_tags(parent):
            return (False, 'Tag not unique')
        elif any(map(lambda s: s in testtag,[' ','\t','\n'])):
            return (False, 'Tag contains whitespace')
        elif any(map(lambda s: s in testtag,spec_chars)):
            return (False, 'Tag contains special characters')
        else:
            return (True, '')    

    @staticmethod
    def tag_error(tag,err_msg):
        """Provide a human-readable error message for bad tags."""
        return str('Tag error for {}: \n{} \n\n'.format(tag,err_msg)
                + 'Enter a unique alphanumeric tag, '
                + 'using only letters, numbers, -, and _. (no periods). ')

    def tree_contains_uri(self,uri):
        """Returns whether or not input uri points to an item in this tree."""
        if not uri:
            return False
        path = uri.split('.')
        p_idx = QtCore.QModelIndex()
        for itemuri in path:
            try:
                row = self.list_child_tags(p_idx).index(itemuri)
            except ValueError as ex:
                return False
            idx = self.index(row,0,p_idx)
            p_idx = idx
        return True

    def get_from_uri(self,uri):
        """Get from this tree the item at the given uri."""
        try:
            path = uri.split('.')
            p_idx = self.root_index()
            for itemuri in path:
                row = self.list_child_tags(p_idx).index(itemuri)
                idx = self.index(row,0,p_idx)
                itm = self.get_item(idx)
                p_idx = idx
            return itm, idx
        except Exception as ex:
            msg = '\n[{}] bad uri: {}\n'.format(__name__,uri)
            ex.message = msg + ex.message
            raise ex

    # Subclass of QAbstractItemModel must implement index()
    def index(self,row,col,parent):
        """
        Returns QModelIndex address of int row, int col, under QModelIndex parent.
        If a row, column, parent combination points to an invalid index, 
        returns invalid QModelIndex().
        """
        if not parent.isValid():
            # If parent is not a valid index, assume the root_index is desirable. 
            return self.root_index()
        else:
            p_itm = self.get_item(parent)
            if row < p_itm.n_children() and row >= 0:
                return self.createIndex(row,col,p_itm.children[row])
            else:
                return QtCore.QModelIndex()
                
    # Subclass of QAbstractItemModel must implement parent()
    def parent(self,idx):
        """
        Returns QModelIndex of parent of item at QModelIndex index
        """
        itm = idx.internalPointer()
        return itm.parent
        
    # Subclass of QAbstractItemModel must implement rowCount()
    def rowCount(self,parent=QtCore.QModelIndex()):
        """
        Either give the number of top-level items,
        or count the children of parent
        """
        if not parent.isValid():
            # there is only 1 root item 
            return 1
        else:
            # count children of parent item
            parent_item = parent.internalPointer()
            return parent_item.n_children()
    
    # Subclass of QAbstractItemModel must implement columnCount()
    def columnCount(self,parent=QtCore.QModelIndex()):
        """
        Let TreeModels by default have one column,
        to display the local TreeItem's tag.
        """
        return 1

    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,itm_idx,data_role):
        """
        TreeModel's implementation of data() returns the tag() of the TreeItem at itm_idx.
        This is only if itm_idx.column() == 0.
        Subclasses should reimplement data() to provide meaningful output for other columns,
        and may consider falling back on super().data() if itm_idx.column() == 0.
        """
        if (not itm_idx.isValid()):
            return None
        if itm_idx == self.root_index():
            return None
        itm = itm_idx.internalPointer()
        if ((data_role == QtCore.Qt.DisplayRole
        or data_role == QtCore.Qt.ToolTipRole 
        or data_role == QtCore.Qt.StatusTipRole
        or data_role == QtCore.Qt.WhatsThisRole)
        and itm_idx.column() == 0):
            return itm.tag()
        else:
            return None

    # Expandable QAbstractItemModel subclass should implement
    # insertRows(row,count[,parent=QModelIndex()])
    def insertRows(self,row,count,parent=QtCore.QModelIndex()):
        if parent.isValid():
            # Get the TreeItem referred to by QModelIndex parent:
            itm = parent.internalPointer()
            self.beginInsertRows(parent,row,row+count-1)
            for j in range(row,row+count):
                itm.children.insert(TreeItem(j,0,parent))
            self.endInsertRows()
            return True
        else:
            return False

    # Shrinkable QAbstractItemModel subclass should implement
    # removeRows(row,count[,parent=QModelIndex()])
    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent.isValid():
            p_itm = parent.internalPointer()
            self.beginRemoveRows(parent,row,row+count-1)
            for j in range(row,row+count)[::-1]:
                del_idx = self.index(j,0,parent)
                del_itm = p_itm.children.pop(j)
                del_itm.deleteLater()
            self.endRemoveRows()
            return True
        else:
            return False

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} item(s)".format(self.rowCount(QtCore.QModelIndex()))
        else:
            return None

    #def iter_indexes(self,parent=QtCore.QModelIndex()):
    #    """Provide a list of the QModelIndexes held in the tree"""
    #    if parent.isValid():
    #        idxs = [parent]
    #        itms = self.get_item(parent).children
    #        for j in range(len(itms)):
    #            itm = itms[j]
    #            idx = self.index(j,0,parent)
    #            if itm.n_children > 0:
    #                idxs = idxs + self.iter_indexes(idx)
    #        return idxs

    def print_tree(self,rowprefix='',parent=QtCore.QModelIndex()):
        tree_string = ''
        if parent.isValid():
            itm = self.get_item(parent)
            tree_string = tree_string+rowprefix+str(itm.data)+'\n'
            for j in range(itm.n_children()):
                tree_string = tree_string + self.print_tree(rowprefix+'\t',self.index(j,0,parent))
        return tree_string
            
