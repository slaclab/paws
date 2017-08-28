class TreeItem(object):
    """
    A structured container for indexing a TreeModel.
    A TreeItem keeps references to a parent TreeItem
    and a list of child TreeItems.
    It is labeled by a tag (TreeItem.tag)
    which must be unique across its sibling TreeItems.
    A root TreeItem should have None as its parent item.
    """

    def __init__(self,parent_itm,tag):
        super(TreeItem,self).__init__()
        self.parent = parent_itm 
        self.children = []      # list of child TreeItems
        self.flags = {}         # dict for any added functionality (e.g. toggles, etc) 
        self.tag = tag          # string tag for indexing and display
        #self.data = None       # TreeItem contains a single object as its data 

    def n_children(self):
        return len(self.children)

    def build_uri(self):
        """
        Return the TreeModel uri of this TreeItem
        by following its parents up to a root item. 
        """
        if self.parent is None:
            return ''
        else:
            uri = self.tag 
            itm = self.parent
            while itm.parent is not None:
                uri = itm.tag+'.'+uri
                itm = itm.parent
        return uri


