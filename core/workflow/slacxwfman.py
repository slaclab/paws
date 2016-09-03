from PySide import QtCore

from core.treemodel import TreeModel
from core.treeitem import TreeItem

class WfManager(TreeModel):
    """
    Class for managing a workflow built from slacx operations.
    """

    def __init__(self,**kwargs):
        #TODO: build a saved tree from kwargs
        #if 'wf_loader' in kwargs:
        #    with f as open(wf_loader,'r'): 
        #        self.load_from_file(f)
        self._wf = {}       # this will be a dict managed by a dask graph 
        super(WfManager,self).__init__()

    # add an Operation to the tree as a new top-level TreeItem.
    def add_op(self,new_op):
        # Count top-level rows by passing parent=QModelIndex()
        ins_row = self.rowCount(QtCore.QModelIndex())
        # Make a new TreeItem, column 0, invalid parent 
        new_treeitem = TreeItem(ins_row,0,QtCore.QModelIndex())
        new_treeitem.data.append(new_op)
        new_treeitem.set_tag('op{}'.format(ins_row))
        new_treeitem.long_tag = new_op.tag()
        self.beginInsertRows(
        QtCore.QModelIndex(),ins_row,ins_row)
        # Insertion occurs between notification methods
        self.root_items.insert(ins_row,new_treeitem)
        self.endInsertRows()
        # TODO: render Operation inputs and outputs as children

    # remove an Operation from the workflow tree
    def remove_op(self,rm_indx):
        rm_row = rm_indx.row()
        self.beginRemoveRows(
        QtCore.QModelIndex(),rm_row,rm_row)
        # Removal occurs between notification methods
        item_removed = self.root_items.pop(removal_row)
        self.endRemoveRows()

    # QAbstractItemModel subclass should implement 
    # headerData(int section,Qt.Orientation orientation[,role=Qt.DisplayRole])
    # note: section arg indicates row or column number, depending on orientation
    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole
            and section == 0):
            return "{} operation(s) loaded".format(self.rowCount(QtCore.QModelIndex()))
        else:
            return None

    def check_wf(self):
        """
        Check the dependencies of the workflow.
        Ensure that all loaded operations have inputs that make sense.
        If everything is found to be ok,
        load the self._wf dict for dask.get() functionality.
        """
        pass


