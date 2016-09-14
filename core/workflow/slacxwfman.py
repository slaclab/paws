from PySide import QtCore

from core.treemodel import TreeModel
from core.treeitem import TreeItem

class WfManager(TreeModel):
    """
    Class for managing a workflow built from slacx operations.
    """

    def __init__(self,**kwargs):
        self._n_loaded = 0 
        #TODO: build a saved tree from kwargs
        #if 'wf_loader' in kwargs:
        #    with f as open(wf_loader,'r'): 
        #        self.load_from_file(f)
        self._wf = {}       # this will be a dict managed by a dask graph 
        super(WfManager,self).__init__()

    def add_op(self,new_op):
        """Add an Operation to the tree as a new top-level TreeItem."""
        # Count top-level rows by passing parent=QModelIndex()
        ins_row = self.rowCount(QtCore.QModelIndex())
        # Make a new TreeItem, column 0, invalid parent 
        new_treeitem = TreeItem(ins_row,0,QtCore.QModelIndex())
        new_treeitem.data.append(new_op)
        new_treeitem.set_tag( 'op{}'.format(self._n_loaded) )
        new_treeitem.long_tag = new_op.__doc__
        self.beginInsertRows(
        QtCore.QModelIndex(),ins_row,ins_row)
        # Insertion occurs between notification methods
        self.root_items.insert(ins_row,new_treeitem)
        self.endInsertRows()
        # Render Operation inputs and outputs as children
        indx = self.index(ins_row,0,QtCore.QModelIndex())
        self.io_subtree(new_op,indx)
        self._n_loaded += 1

    def update_op(self,indx,new_op):
        """Replace Operation at indx with new_op"""
        # Get the treeitem for indx
        item = self.get_item(indx)
        # Put the data in the treeitem
        item.data[0] = new_op
        item.long_tag = new_op.__doc__
        # Wipe out the children
        #for child in item.children:
        #    del child
        # Update the op subtree
        self.build_io_subtrees(new_op,indx)
        # TODO: update gui arg frames

    def io_subtree(self,op,parent):
        """Add inputs and outputs subtrees as children of an Operation TreeItem"""
        # Get a reference to the parent item
        p_item = parent.internalPointer()
        # TreeItems as placeholders for inputs, outputs lists
        inputs_treeitem = TreeItem(0,0,parent)
        inputs_treeitem.set_tag('Inputs')
        outputs_treeitem = TreeItem(1,0,parent)
        outputs_treeitem.set_tag('Outputs')
        # Insert the new TreeItems
        self.beginInsertRows(parent,0,1)
        p_item.children.insert(0,inputs_treeitem)
        p_item.children.insert(1,outputs_treeitem)
        self.endInsertRows()
        # Populate the new TreeItems with op.inputs and op.outputs
        self.build_io_subtrees(op,parent)

    def build_io_subtrees(self,op,parent):
        # Get a reference to the parent item
        p_item = parent.internalPointer()
        # assume operation object is parent.data[0]
        #op = p_item.data[0]
        # Get references to the inputs and outputs subtrees
        inputs_treeitem = p_item.children[0]
        outputs_treeitem = p_item.children[1]
        # Get the QModelIndexes of the subtrees 
        inputs_indx = self.index(0,0,parent)
        outputs_indx = self.index(1,0,parent)
        # Eliminate their children
        nc_i = inputs_treeitem.n_children()
        nc_o = outputs_treeitem.n_children()
        self.removeRows(0,nc_i,inputs_indx)
        self.removeRows(0,nc_o,outputs_indx)
        #self.beginRemoveRows(inputs_indx,0,nc_i-1)
        #for i in range(nc_i-1):
        #    #del self.get_item(inputs_indx).children[i]
        #    self.get_item(inputs_indx).children.pop(i)
        #self.endRemoveRows()
        #self.beginRemoveRows(outputs_indx,0,nc_o-1)
        #for i in range(nc_o-1):
        #    #del self.get_item(outputs_indx).children[i]
        #    self.get_item(outputs_indx).children.pop(i)
        #self.endRemoveRows()
        # Populate new inputs and outputs
        for name,val in op.inputs.items():
            ins_row = self.rowCount(inputs_indx)
            inp_treeitem = TreeItem(ins_row,0,inputs_indx)
            inp_treeitem.set_tag(name)
            # generate long tag from Operation.parameter_doc(name,val,doc)
            inp_treeitem.long_tag = p_item.data[0].parameter_doc(name,val,op.input_doc[name])
            inp_treeitem.data.append(val)
            self.beginInsertRows(inputs_indx,ins_row,ins_row)
            inputs_treeitem.children.insert(ins_row,inp_treeitem)
            self.endInsertRows()
        for name,val in op.outputs.items():
            ins_row = self.rowCount(outputs_indx)
            out_treeitem = TreeItem(ins_row,0,outputs_indx)
            out_treeitem.set_tag(name)
            out_treeitem.long_tag = p_item.data[0].parameter_doc(name,val,op.output_doc[name])
            out_treeitem.data.append(val)
            self.beginInsertRows(outputs_indx,ins_row,ins_row)
            outputs_treeitem.children.insert(ins_row,out_treeitem)
            self.endInsertRows()

    def remove_op(self,rm_indx):
        """Remove an Operation from the workflow tree"""
        rm_row = rm_indx.row()
        self.beginRemoveRows(
        QtCore.QModelIndex(),rm_row,rm_row)
        # Removal occurs between notification methods
        item_removed = self.root_items.pop(rm_row)
        self.endRemoveRows()

    # QAbstractItemModel subclass should implement 
    # headerData(int section,Qt.Orientation orientation[,role=Qt.DisplayRole])
    # note: section arg indicates row or column number, depending on orientation
    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.rowCount(QtCore.QModelIndex()))
        elif (data_role == QtCore.Qt.DisplayRole and section == 1):
            return "info".format(self.rowCount(QtCore.QModelIndex()))
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


