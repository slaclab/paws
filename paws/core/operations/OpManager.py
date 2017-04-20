from PySide import QtCore

from .. import operations as ops
from ..models.QTreeSelectionModel import QTreeSelectionModel

class OpManager(QTreeSelectionModel):
    """
    Tree structure for categorized storage and retrieval of Operations.
    """

    def __init__(self,**kwargs):
        super(OpManager,self).__init__({'select':False,'enable':False})
        self._module_list = []
        self.logmethod = None

    def load_cats(self,cat_list):
        for cat in cat_list:
            p_idx = self.root_index()
            self._module_list.append(cat)
            for subcat in cat.split('.'):
                #print 'add cat {} under {}'.format(subcat,parent.internalPointer().tag())
                self.add_cat(subcat,p_idx)
                p_idx = self.idx_of_cat(subcat,p_idx)

    def add_cat(self,new_cat,p_idx):
        """
        Add a category to the tree under parent,
        if not already there. Return its index.
        """
        cat_idx = self.idx_of_cat(new_cat,p_idx)
        if not cat_idx.isValid():
            self.set_item(new_cat,None,p_idx)

    def idx_of_cat(self,catname,p_idx):
        """
        If cat exists under p_idx, return its index, 
        else return an invalid QModelIndex.
        """
        ncats = self.item_count(p_idx)
        p_itm = self.get_from_idx(p_idx)
        for j in range(ncats):
            idx = self.index(j,0,p_idx)
            cat = self.get_from_idx(idx).tag
            if cat == catname:
                return idx
        return QtCore.QModelIndex() 

    def load_ops(self,cat_op_list):
        """
        Load OpManager tree from input cat_op_list.
        Format of cat_op_list is [(category1,op1),(category2,op2),...].
        i.e. each operation in cat_op_list is specified by a tuple,
        where the first element is a category,
        and the second element is the Operation itself.
        load_cats() MUST be called before load_ops()
        and MUST ensure that all cats in cat_op_list exist in the tree.
        """
        #### BUILD OPERATIONS TREE
        # Tree will consist of nodes indicating categories,
        # with subcategories or Operations as children.
        for cat_op in cat_op_list:
            self._module_list.append(cat_op[0]+'.'+cat_op[1].__name__)
            idx = self.root_index()
            for subcat in cat_op[0].split('.'):
                idx = self.idx_of_cat(subcat,idx)
            self.add_op(cat_op[1],idx)

    def add_op(self,op,p_idx):
        """
        Add op to the tree, 
        as a child of the TreeItem at QModelIndex p_idx.
        """
        self.set_item(op.__name__,op,p_idx)

    def remove_ops(self,rm_idx):
        """
        Remove an Operation or category from the tree.
        """
        if not rm_idx == self.root_index() and rm_idx.isValid():
            p_idx = self.parent(rm_idx)
            rm_itm = self.get_from_idx(rm_idx)
            self.delete_item(rm_itm.tag,p_idx)            

    # get an Operation by its cat.[subcat.(...).]opname uri
    #def get_op_from_uri(self,op_uri):
        #return self.get_data_from_uri(op_uri)
        #for op in self._op_list:
        #    if op.__name__ == op_name:
        #        return op
        #return None

    # get an Operation from the list by its TreeItem's QModelIndex
    #def get_op(self,indx):
        #treeitem = self.get_item(indx)
        #return treeitem.data
 
    # Reimplemented headerData() for OpManager 
    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operations available".format(len(self._op_list))
        else:
            return super(OpManager,self).headerData(section,orientation,data_role) 

