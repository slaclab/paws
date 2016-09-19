from PySide import QtCore

from core.treemodel import TreeModel
from core.treeitem import TreeItem
from core.operations import optools

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

    def add_op(self,new_op,tag):
        """Add an Operation to the tree as a new top-level TreeItem."""
        # Count top-level rows by passing parent=QModelIndex()
        ins_row = self.rowCount(QtCore.QModelIndex())
        # Make a new TreeItem, column 0, invalid parent 
        new_treeitem = TreeItem(ins_row,0,QtCore.QModelIndex())
        new_treeitem.data.append(new_op)
        new_treeitem.set_tag( tag )
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
        # Populate new inputs and outputs
        n_inputs = len(op.inputs)
        input_items = op.inputs.items()
        n_outputs = len(op.outputs)
        output_items = op.outputs.items()
        self.beginInsertRows(inputs_indx,0,n_inputs-1)
        for i in range(n_inputs):
            name,val = input_items[i]
            inp_treeitem = TreeItem(i,0,inputs_indx)
            inp_treeitem.set_tag(name)
            # generate long tag from optools.parameter_doc(name,val,doc)
            inp_treeitem.long_tag = optools.parameter_doc(name,val,op.input_doc[name])
            inp_treeitem.data.append(val)
            inputs_treeitem.children.insert(i,inp_treeitem)
        self.endInsertRows()
        self.beginInsertRows(outputs_indx,0,n_outputs-1)
        for i in range(n_outputs):
            name,val = output_items[i]
            out_treeitem = TreeItem(i,0,outputs_indx)
            out_treeitem.set_tag(name)
            out_treeitem.long_tag = optools.parameter_doc(name,val,op.output_doc[name])
            out_treeitem.data.append(val)
            outputs_treeitem.children.insert(i,out_treeitem)
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
        """
        pass

    def load_wf_dict(self):
        """
        Build a dask-compatible dictionary from the Operations in the workflow tree
        """
        pass

    def locate_input(self,inplocator):
        """Return the data pointed to by a given InputLocator object"""
        src = inplocator.src
        uri = inplocator.uri
        if src in optools.valid_sources:
            if src == optools.text_input_selection: 
                # uri will be unicode rep of numerical input
                # leave type casting to the Operation itself
                return uri 
            elif src == optools.image_input_selection: 
                # follow uri in image tree
                tag = uri.split('.')[0]
                indx = self.imgman.list_tags().index(tag)
                item = self.imgman.root_items[indx]
            elif src == optools.op_input_selection: 
                # follow uri in workflow tree
                tag = uri.split('.')[0]
                indx = self.imgman.list_tags().index(tag)
                item = self.imgman.root_items[indx]
        else: 
            msg = 'found input source {}, should be one of {}'.format(
            src, valid_sources)
            raise ValueError(msg)


