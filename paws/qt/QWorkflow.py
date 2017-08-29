from collections import OrderedDict

from PySide import QtCore

from ..core.workflow.Workflow import Workflow
from ..core.operations import Operation as opmod
from .QTreeSelectionModel import QTreeSelectionModel

class QWorkflow(Workflow,QTreeSelectionModel):
    """
    A QTreeSelectionModel for interacting with TreeModel Workflow.
    """

    def __init__(self,wfman):
        super(QWorkflow,self).__init__(wfman)

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.root_item().n_children())
        else:
            return super(QWorkflow,self).headerData(section,orientation,data_role)    

    opChanged = QtCore.Signal(str)

    opFinished = QtCore.Signal(str)

    def execute_op(self,op_tag):
        op = self.get_data_from_uri(op_tag) 
        self.load_inputs(op,self.wf_manager,self.wf_manager.plugin_manager)
        self.opChanged.emit(op_tag)
        op.run() 
        self.set_item(op_tag,op)
        self.opChanged.emit(op_tag)
        self.opFinished.emit(op_tag)

    #def set_op_input_at_uri(self,uri,val):
    #    """
    #    Set an op input at uri to provided value val.
    #    The uri must be a valid uri in the QTreeModel,
    #    of the form opname.inputs.inpname.
    #    """
    #    path = uri.split('.')
    #    opname = path[0]
    #    if not path[1] == opmod.inputs_tag:
    #        msg = '[{}] uri {} does not point to an input'.format(__name__,uri)
    #        raise ValueError(msg)
    #    inpname = path[2]
    #    #inp_uri = opmodname+'.'+opmod.inputs_tag+'.'+inpname
    #    op = self._tree.get_data_from_uri(opname)
    #    op.input_locator[inpname].data = val
    #    self.set_item_at_uri(uri,val)

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



