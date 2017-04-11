from PySide import QtCore

class TreeItem(QtCore.QObject):
    """
    TreeItem is a container for data stored in a TreeModel. 
    A TreeItem keeps references to a parent QModelIndex,
    and to its row and column within the QAbstractItemModel structure.
    The objective content of the TreeItem is stored at TreeItem.data. 
    Every TreeItem must have a tag() for display and uri creation.
    """

    def __init__(self,row,column,parent_idx):
        super(TreeItem,self).__init__()
        self.parent = parent_idx    
        self.row = row
        self.column = column
        self.data = None        # TreeItem contains a single object as its data 
        self.children = []      # list of other TreeItems
        self._tag = None
        # Flags: one for being selected, one for being enabled
        self._flags = [False,False] 

    def n_children(self):
        return len(self.children)

    def insert_child(self,new_child,row):
        self.children.insert(row,new_child)

    def remove_child(self,row):
        child_removed = self.children.pop(row)
    
    def tag(self):
        if not self._tag:
            return 'untagged'
        else:
            return self._tag

    def set_tag(self,tag_in):
        self._tag = tag_in

    def is_checked(self):
        return self._flags[0]
    
    def children_checked(self):
        if self.n_children > 0:
            return any([c_itm.children_checked() for c_itm in self.children])
        else:
            return self._flags[0]

    def set_checked(self,val):
        self._flags[0] = bool(val)


