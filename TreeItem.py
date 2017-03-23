class TreeItem(object):
    """
    Container for packing objects into a TreeModel.

    This is a container to facilitate data storage in a TreeModel. 
    A TreeItem keeps references to a parent QModelIndex,
    and to its row and column within the QAbstractItemModel structure.
    The objective content of the TreeItem is stored at TreeItem.data. 
    Every TreeItem must have a tag() for display and uri creation.
    """

    def __init__(self,row,column,parent):
        # TODO: Consider whether TreeItem.parent is a good idea...
        self.parent = parent
        self.row = row
        self.column = column
        self.data = None        # TreeItem contains a single object as its data 
        self.children = []      # list of other TreeItems
        #self._long_tag = None 
        self._tag = None
        self._checked = False


    #def n_data(self):
    #    return len(self.data)

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

    #def long_tag(self):
    #    if not self._long_tag:
    #        return self._tag
    #    else:
    #        return self._long_tag

    def set_tag(self,tag_in):
        self._tag = tag_in

    def is_checked(self):
        return self._checked
    
    def children_checked(self):
        if self.n_children > 0:
            return any([c_itm.children_checked() for c_itm in self.children])
        else:
            return self._checked

    def set_checked(self,val):
        self._checked = bool(val)

    #def set_long_tag(self,tag_in):
    #    self._long_tag = tag_in

    #def data_str(self):
    #    """Build a string representing self.data"""
    #    #for i in range(len(self.data)):
    #    datstr = str(self.data)
    #    return 'data:\n' + datstr[:min((len(datstr),60))]


