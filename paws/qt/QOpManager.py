from collections import OrderedDict

from PySide import QtCore

from ..qt.QTreeSelectionModel import QTreeSelectionModel

class QOpManager(QTreeSelectionModel):
    """
    A QTreeSelectionModel for interacting with TreeModel OpManager.
    """

    def __init__(self,opman):
        flag_dict = OrderedDict()
        flag_dict['enable'] = True
        super(QOpManager,self).__init__(flag_dict,opman)
        self.opman = opman

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operations available".format(self.opman.n_ops())
        else:
            return super(QOpManager,self).headerData(section,orientation,data_role) 

    #def idx_of_cat(self,catname,p_idx):
    #    """
    #    If cat exists under p_idx, return its index, 
    #    else return an invalid QModelIndex.
    #    """
    #    ncats = self.item_count(p_idx)
    #    p_itm = self.get_from_idx(p_idx)
    #    for j in range(ncats):
    #        idx = self.index(j,0,p_idx)
    #        cat = self.get_from_idx(idx).tag
    #        if cat == catname:
    #            return idx
    #    return QtCore.QModelIndex() 

    #def remove_ops(self,rm_idx):
    #    """
    #    Remove an Operation or category from the tree.
    #    """
    #    if not rm_idx == self.root_index() and rm_idx.isValid():
    #        p_idx = self.parent(rm_idx)
    #        rm_itm = self.get_from_idx(rm_idx)
    #        self.delete_item(rm_itm.tag,p_idx)            

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
 


