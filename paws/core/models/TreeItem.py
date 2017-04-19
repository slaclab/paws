class TreeItem(object):
    """
    A TreeItem is a structured container 
    for building a QTreeModel on top of a TreeModel. 
    A TreeItem keeps references to a parent TreeItem
    and a list of child TreeItems.
    It is labeled by a tag (TreeItem._tag or TreeItem.tag())
    which must be unique across its sibling TreeItems.
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


