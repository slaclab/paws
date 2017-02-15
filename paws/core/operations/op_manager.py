from PySide import QtCore

from .. import operations as ops
from ..treemodel import TreeModel, TreeSelectionModel
from ..treeitem import TreeItem

class OpManager(TreeSelectionModel):
    """
    Tree structure for categorized storage and retrieval of Operations.
    """

    # TODO: Add methods to enable and disable Operations
    # TODO: Write a UI for enabling and disabling Operations
    # TODO: Ensure that the cfg file of enabled/disabled ops is saved before closing

    def __init__(self,**kwargs):
        super(OpManager,self).__init__()
        self._cat_list = ops.cat_list 
        self._op_list = [cat_op[1] for cat_op in ops.cat_op_list]
        self.load_cats(ops.cat_list) 
        self.load_ops(ops.cat_op_list)
        self.logmethod = None

    def save_config(self):
        for k in self._cat_list + self.list_op_names():
            ops.op_load_flags[k] = True 
        ops.save_cfg(ops.op_load_flags,ops.cfg_file)

    def load_cats(self,cat_list):
        for cat in cat_list:
            parent = QtCore.QModelIndex()
            for subcat in cat.split('.'):
                parent = self.add_cat(subcat,parent)

    def add_cat(self,new_cat,parent):
        """
        Add a category to the tree under parent if not already there. Return its index.
        """
        cat_idx = self.idx_of_cat(new_cat,parent)
        if not cat_idx.isValid():
            ins_row = self.rowCount(parent)
            new_treeitem = TreeItem(ins_row,0,parent)
            new_treeitem.data = new_cat
            new_treeitem.set_tag( new_cat )
            new_treeitem.long_tag = new_cat 
            self.beginInsertRows(parent,ins_row,ins_row)
            if parent.isValid():
                self.get_item(parent).children.insert(ins_row,new_treeitem)
            else:
                self.root_items.insert(ins_row,new_treeitem)
            self.endInsertRows()
            return self.index(ins_row,0,parent)
        else:
            return cat_idx

    def idx_of_cat(self,catname,parent):
        """If cat exists under parent, return its index, else return an invalid QModelIndex"""
        ncats = self.rowCount(parent)
        for j in range(ncats):
            idx = self.index(j,0,parent)
            cat = self.get_item(idx).data
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
            parent = QtCore.QModelIndex()
            for subcat in cat_op[0].split('.'):
                # get index of subcat
                idx = self.idx_of_cat(subcat,parent)
                parent = idx
            self.add_op(cat_op[1],idx)

    def add_op(self,op,parent):
        """add op to the tree under QModelIndex parent"""
        ins_row = self.rowCount(parent)
        op_treeitem = TreeItem(ins_row,0,parent)
        op_treeitem.data = op
        op_treeitem.set_tag( op.__name__ )
        op_treeitem.long_tag = op.__doc__
        self.beginInsertRows(parent,ins_row,ins_row)
        # Insertion occurs between notification methods
        self.get_item(parent).children.insert(ins_row,op_treeitem)
        self.endInsertRows()

    # remove an Operation from the tree
    def remove_op(self,removal_indx):
        # check if need to clear out any empty cats
        # remove op from self._op_list
        # set ops.op_load_flags so this op remains disabled at next startup 
        pass

    def list_op_names(self):
        return [op.__name__ for op in self._op_list]

    # get an Operation by its name 
    def get_op_byname(self,op_name):
        for op in self._op_list:
            if op.__name__ == op_name:
                return op
        return None

    # get index of an operation by its name
    #def get_index_byname(self,op_name):
    #    for i in range(len(self._op_list)):
    #        op = self._op_list[i]
    #        if op.__name__ == op_name:
    #            return i 
    #    return None

    # get an Operation from the list by its TreeItem's QModelIndex
    def get_op(self,indx):
        treeitem = self.get_item(indx)
        return treeitem.data
 
    # Overloaded headerData() for OpManager 
    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "Operations: {} available".format(len(self._op_list))
        else:
            return None

    # Overloaded data() for OpManager
    def data(self,item_indx,data_role):
        if (not item_indx.isValid()):
            return None
        item = item_indx.internalPointer()
        if item_indx.column() == 1:
            if item.data:
                if item.data in ops.cat_list:
                    # Should be a category
                    return ' ' 
                else:
                    # Should be an operation
                    if item.data.__doc__:
                        # Note: commas are used as delimiters when loading strings to Qt views,
                        # so they should be removed to avoid warning messages.
                        # This will munge the description a bit.
                        # TODO: A more elegant solution would be welcome.
                        return item.data.__doc__.replace(',',' ')
                    else:
                        return 'no description'
            else:
                return ' '
        else:
            if data_role == QtCore.Qt.DisplayRole:
                return item.tag()
            elif (data_role == QtCore.Qt.ToolTipRole 
                or data_role == QtCore.Qt.StatusTipRole
                or data_role == QtCore.Qt.WhatsThisRole):
                if item.data in ops.cat_list:
                    # Should be a category
                    return 'Operation category {}'.format(item.data)
                else:
                    # Should be an operation
                    return item.long_tag 
            else:
                return None
    



