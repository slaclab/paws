from collections import OrderedDict

from PySide import QtCore

from ..core.operations import Operation as op
from .QTreeSelectionModel import QTreeSelectionModel

class QWorkflow(QTreeSelectionModel):
    """
    A QTreeSelectionModel for interacting with TreeModel Workflow.
    """

    def __init__(self,wf):
        flag_dict = OrderedDict()
        flag_dict['select'] = False
        flag_dict['enable'] = False
        super(QWorkflow,self).__init__(flag_dict,wf)
        #self._tree references wf after QTreeModel.__init__()
        #self.wf = wf

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.root_item().n_children())
        else:
            return super(QWorkflow,self).headerData(section,orientation,data_role)    

    wf_updated = QtCore.Signal()

    def remove_op(self,op_tag):
        """
        Remove an Operation from the workflow tree.
        """
        self.remove_item(op_tag)
        self.wf_updated.emit() 

    def set_op(self,op_tag,new_op):
        """
        Set workflow tree data at op_tag to new_op.
        """
        self.set_item(op_tag,new_op)
        self.wf_updated.emit() 

    def set_op_input_at_uri(self,uri,val):
        """
        Set an op input at uri to provided value val.
        The uri must be a valid uri in the QTreeModel,
        of the form opname.inputs.inpname.
        """
        path = uri.split('.')
        opname = path[0]
        if not path[1] == op.inputs_tag:
            msg = '[{}] uri {} does not point to an input'.format(__name__,uri)
            raise ValueError(msg)
        inpname = path[2]
        #inp_uri = opname+'.'+op.inputs_tag+'.'+inpname
        op = self._tree.get_data_from_uri(opname)
        op.input_locator[inpname].data = val
        self.set_item_at_uri(uri,val)

        # Additionally, set the op.input_locator[name].data to val.
        #opname = uri[:uri.find('.')]
        #inputname = uri[uri.rfind('.')+1:]
        #op = self._tree.get_data_from_uri(opname)
        #op.input_locator[inputname].data = val
        #self.wf_updated.emit() 

    #def update_op(self,op_tag,new_op):
    #    """Update given uri op_tag to Operation new_op."""
    #    self.set_item(op_tag,new_op)

    #    #p_idx = self.parent(rm_idx)
    #    #if not p_idx == self.root_index():
    #    #    msg = '[{}] Called remove_op on non-Operation at QModelIndex {}. \n'.format(__name__,rm_idx)
    #    #    raise ValueError(msg)
    #    #rm_itm = self.get_from_idx(rm_idx)
    #    #self.remove_item(rm_itm.tag,p_idx)


    #def tree_update(self,parent_itm,itm_tag,itm_data):
    #    if isinstance(itm_data,Operation):
    #        super(Workflow,self).tree_update(parent_itm,itm_tag,self.build_tree(itm_data))
    #    else:
    #        super(Workflow,self).tree_update(parent_itm,itm_tag,itm_data)



