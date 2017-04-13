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
        # Flags: use these to serve as toggles for things specific to a TreeItem-based model
        self._flags = [] 

    def n_children(self):
        return len(self.children)

    def tag(self):
        if not self._tag:
            return 'untagged'
        else:
            return self._tag

    def set_tag(self,tag_in):
        self._tag = tag_in

    #def insert_child(self,new_child,row):
    #    self.children.insert(row,new_child)

    #def remove_child(self,row):
    #    self.children.pop(row)
    


