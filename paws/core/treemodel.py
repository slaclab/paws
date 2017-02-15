import string 
from collections import OrderedDict

from PySide import QtCore

from .treeitem import TreeItem

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
        # keep root items in a TreeItem list
        self.root_items = []    

    def get_item(self,idx):
        """Just a prettier face in front of idx.internalPointer()"""
        return idx.internalPointer() 

    def build_uri(self,idx):
        """
        Build a URI for the TreeItem at idx 
        by prepending its parent tags with '.' as a delimiter.
        """
        item_ref = self.get_item(idx)
        item_uri = item_ref.tag()
        while item_ref.parent.isValid():
            item_ref = self.get_item(item_ref.parent)
            item_uri = item_ref.tag()+"."+item_uri
        return item_uri

    def list_tags(self,parent):
        """Get a list of tags for TreeItems under parent."""
        if not parent.isValid():
            return [item.tag() for item in self.root_items]
        else:
            return [item.tag() for item in self.get_item(parent).children]

    def auto_tag(self,prefix):
        """
        Generate the next unique tag from prefix by appending '_x' to it, 
        where x is a minimal nonnegative integer.
        """
        indx = 0
        goodtag = False
        while not goodtag:
            testtag = prefix+'_{}'.format(indx)
            if not testtag in self.list_tags(QtCore.QModelIndex()):
                goodtag = True
            else:
                indx += 1
        return testtag
    
    # test uniqueness and good form of a tag
    def is_good_tag(self,testtag,parent=QtCore.QModelIndex()):
        """
        Checks for usable tags, returns a (bool,string) tuple
        where the bool indicates whether the tag is good, 
        and the string provides explanation if the tag is not good. 
        """
        spec_chars = string.punctuation 
        spec_chars = spec_chars.replace('_','')
        spec_chars = spec_chars.replace('-','')
        if not testtag:
            return (False, 'Tag is blank')
        elif testtag in self.list_tags(parent):
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

    def is_good_uri(self,uri):
        """Returns whether or not input uri points to an item in this tree."""
        if not uri:
            return False
        path = uri.split('.')
        p_idx = QtCore.QModelIndex()
        for itemuri in path:
            try:
                row = self.list_tags(p_idx).index(itemuri)
            except ValueError as ex:
                return False
            idx = self.index(row,0,p_idx)
            # get TreeItem from QModelIndex
            #item = self.get_item(idx)
            # set new parent in case the path continues...
            p_idx = idx
        return True

    def get_from_uri(self, uri):
        """Get from this tree the item at the given uri."""
        path = uri.split('.')
        p_idx = QtCore.QModelIndex()
        try:
            for itemuri in path:
                # get QModelIndex of item 
                row = self.list_tags(p_idx).index(itemuri)
                idx = self.index(row,0,p_idx)
                # get TreeItem from QModelIndex
                itm = self.get_item(idx)
                # set new parent in case the path continues...
                p_idx = idx
            return itm, idx
        except Exception as ex:
            msg = '-----\nbad uri: {}\n-----\n'.format(uri)
            #print msg
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
            # If parent is not a valid index, a top level item is being queried.
            if row < len(self.root_items) and row >= 0:
                # Return the index
                return self.createIndex(row,col,self.root_items[row])
            else:
                # Bad row: return invalid index
                return QtCore.QModelIndex()
        else:
            # Grab the parent from its QModelIndex...
            p_item = parent.internalPointer()
            # Return the index of the child at row
            if row < len(p_item.children) and row >= 0:
                return self.createIndex(row,col,p_item.children[row])
            else:
                # Bad row: return invalid index
                return QtCore.QModelIndex()
                
    # Subclass of QAbstractItemModel must implement parent()
    def parent(self,idx):
        """
        Returns QModelIndex of parent of item at QModelIndex index
        """
        # Grab this TreeItem from its QModelIndex
        itm = idx.internalPointer()
        if not itm.parent.isValid():
            # We have no parent, therefore a top level item
            return QtCore.QModelIndex()
        else:
            return itm.parent
        
    # Subclass of QAbstractItemModel must implement rowCount()
    def rowCount(self,parent=QtCore.QModelIndex()):
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
    def columnCount(self,parent=QtCore.QModelIndex()):
        """
        Let TreeModels by default have one column,
        to display the local TreeItem's tag.
        """
        return 1

    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,itm_idx,data_role):
        if (not itm_idx.isValid()):
            return None
        item = itm_idx.internalPointer()
        if ((data_role == QtCore.Qt.DisplayRole
        or data_role == QtCore.Qt.ToolTipRole 
        or data_role == QtCore.Qt.StatusTipRole
        or data_role == QtCore.Qt.WhatsThisRole)
        and itm_idx.column() == 0):
            return item.tag()
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
            for j in range(row,row+count)[::-1]:
                #del item.children[j]
                item.children.pop(j)
        else:
            for j in range(row,row+count)[::-1]:
                #del self.root_items[j]
                self.root_items.pop(j)
        # Signal listeners that we are done removing rows
        self.endRemoveRows()

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} item(s) open".format(self.rowCount(QtCore.QModelIndex()))
        #elif (data_role == QtCore.Qt.DisplayRole and section == 1):
        #    return "info".format(self.rowCount(QtCore.QModelIndex()))
        else:
            return None

    def iter_indexes(self,parent=QtCore.QModelIndex()):
        """Provide a list of the QModelIndexes held in the tree"""
        if parent.isValid():
            ixs = [parent]
            # Loop through children of parent
            items = self.get_item(parent).children
        else:
            ixs = []
            # Loop through root_items
            items = self.root_items
        for j in range(len(items)):
            item = items[j]
            ix = self.index(j,0,parent)
            # TODO: check for NoneType children here?
            if item.n_children > 0:
                ixs = ixs + self.iter_indexes(ix)
        return ixs

    def print_tree(self,rowprefix='',parent=QtCore.QModelIndex()):
        if parent.isValid():
            item = self.get_item(parent)
            print rowprefix+str(item.data)
            for j in range(item.n_children()):
                self.print_tree(rowprefix+'\t',self.index(j,0,parent))
        else:
            for jroot in range(len(self.root_items)):
                item = self.root_items[jroot]
                self.print_tree(rowprefix,self.index(jroot,0,parent))
            
    def tree_dataChanged(self,idx):
        self.dataChanged.emit(idx,idx)
        itm = idx.internalPointer()
        for c_row in range(itm.n_children()):
            c_idx = self.index(c_row,0,idx)
            self.tree_dataChanged(c_idx)

    def build_dict(self,x):
        """Build a dict from structured data object x"""
        if isinstance(x,dict):
            d = x 
        elif isinstance(x,list):
            d = OrderedDict(zip([str(i) for i in range(len(x))],x)) 
        else:
            d = {} 
        return d

    def tree_update(self,idx,x_new):
        """
        Call this function to store x_new in the TreeItem at idx 
        and then build/update/prune the subtree rooted at that item.
        Take measures to change as little as possible of the tree,
        since this can be a big operation and is called frequently.
        """
        itm = idx.internalPointer()
        x = itm.data
        itm.data = x_new
        # Build dict of the intended children 
        x_dict = self.build_dict(x_new)
        # Remove obsolete children
        c_kill = [] 
        for j in range(itm.n_children()):
            #if not self.index(j,0,idx).internalPointer().tag() in x_dict.keys():
            if not itm.children[j].tag() in x_dict.keys():
                c_kill.append( j )
        c_kill.sort()
        for j in c_kill[::-1]:
            self.beginRemoveRows(idx,j,j)
            itm.children.pop(j)
            self.endRemoveRows()
        # Add items for any new children 
        c_keys = [itm.children[j].tag() for j in range(itm.n_children())]
        for k in x_dict.keys():
            if not k in c_keys:
                nc = itm.n_children()
                c_itm = TreeItem(nc,0,idx)
                c_itm.set_tag(k)
                self.beginInsertRows(idx,nc,nc)
                itm.children.insert(nc,c_itm)
                self.endInsertRows()
        # Recurse to update children
        for j in range(itm.n_children()):
            c_idx = self.index(j,0,idx)
            c_tag = c_idx.internalPointer().tag()
            self.tree_update(c_idx,x_dict[c_tag])
        # Finish by informing views that dataChanged().
        self.tree_dataChanged(idx) 

    def setData(self,idx,value,data_role):
        return False


class TreeSelectionModel(TreeModel):

    def __init__(self):
        super(TreeSelectionModel,self).__init__()

    def columnCount(self,parent):
        """
        Let TreeSelectionModel have two columns:
        one for the TreeItem tag, one for selection status.
        """
        return 2

    def headerData(self,section,orientation,data_role):
        # note: section indicates row or column number, depending on orientation
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return super(TreeSelectionModel,self).data(section,orientation,data_role) 
        elif (data_role == QtCore.Qt.DisplayRole and section == 1):
            return "selection"

    # QAbstractItemModel subclass must implement 
    # data(QModelIndex[,role=Qt.DisplayRole])
    def data(self,itm_idx,data_role):
        if (not itm_idx.isValid()):
            return None
        itm = itm_idx.internalPointer()
        if ((data_role == QtCore.Qt.DisplayRole
        or data_role == QtCore.Qt.ToolTipRole 
        or data_role == QtCore.Qt.StatusTipRole
        or data_role == QtCore.Qt.WhatsThisRole)
        and itm_idx.column() == 0):
            return itm.tag()
        elif data_role == QtCore.Qt.CheckStateRole and itm_idx.column() == 1:
            if itm.is_checked():
                return QtCore.Qt.Checked
            elif itm.children_checked():
                return QtCore.Qt.PartiallyChecked
            else:
                return QtCore.Qt.Unchecked
        else:
            return None

    # Need flags to reflect checkability
    def flags(self, idx):
        if not idx.isValid():
            return None
        elif idx.column() == 1:
            return super(TreeSelectionModel,self).flags(idx) | QtCore.Qt.ItemIsUserCheckable
        else:
            return super(TreeModel, self).flags(idx)

    # Ui-editable QAbstractItemModel subclasses must implement setData(index,value[,role])
    def setData(self,idx,value,data_role):
        if idx.column() == 1:
            #if role == Qt.EditRole:
            #    return False
            if data_role == QtCore.Qt.CheckStateRole:
                itm = self.get_item(idx)
                itm.set_checked(value)
                self.dataChanged.emit(idx, idx)
                return True
            else:
                return super(TreeModel, self).setData(index, value, data_role)
        else:
            return super(TreeModel, self).setData(index, value, data_role)

    def set_all_unselected(self,idx=QtCore.QModelIndex()):
        if idx.isValid():
            itm = self.get_item(idx)
            itm.set_checked(False)
            for c_row in range(itm.n_children()):
                c_idx = self.index(c_row,0,idx)
                self.set_all_unselected(c_idx)
        else:
            for r_row in range(self.rowCount()):
                r_idx = self.index(r_row,0,idx)
                self.set_all_unselected(r_idx)
            
    def get_all_selected(self,idx=QtCore.QModelIndex()):
        sel_idxs = []
        if idx.isValid():
            itm = self.get_item(idx)
            if itm.is_checked():
                sel_idxs.append(idx)
            for c_row in range(itm.n_children()):
                c_idx = self.index(c_row,0,idx)
                sel_idxs = sel_idxs + self.get_all_selected(c_idx)
        else:
            for r_row in range(self.rowCount()):
                r_idx = self.index(r_row,0,idx)
                sel_idxs = sel_idxs + self.get_all_selected(r_idx)
        return sel_idxs



