from collections import OrderedDict
import copy
from functools import partial

from ..models.TreeModel import TreeModel
from ..operations import Operation as op
from ..operations.Operation import Operation, Batch, Realtime

class Workflow(TreeModel):
    """
    Tree structure for a Workflow built from paws Operations.
    """

    def __init__(self):
        super(Workflow,self).__init__()
        #self.wfman = wfman

    def __getitem__(self,key):
        optags = self.keys()
        if key in optags:
            return self.get_data_from_uri(key) 
        else:
            raise KeyError('[{}] {}.__getitem__ only recognizes keys {}'
            .format(__name__,type(self).__name__,optags))
    def __setitem__(self,key,data):
        optags = self.keys() 
        # TODO: ensure that data is an Operation?
        if key in optags:
            self.set_item(key,data)
        else:
            raise KeyError('[{}] {}.__setitem__ only recognizes keys {}'
            .format(__name__,type(self).__name__,optags))
    def keys(self):
        return self.list_op_tags() 

    def build_tree(self,x):
        """
        Reimplemented TreeModel.build_tree() 
        so that TreeItems are built from Operations.
        """
        if isinstance(x,Operation):
            d = OrderedDict()
            d[op.inputs_tag] = self.build_tree(x.inputs)
            d[op.outputs_tag] = self.build_tree(x.outputs)
            return d
        else:
            return super(Workflow,self).build_tree(x) 

    def op_dict(self):
        optags = self.list_op_tags() 
        op_dict = OrderedDict(zip(optags,[self.get_data_from_uri(nm) for nm in optags]))
        return op_dict

    def list_op_tags(self):
        return self.root_tags()

    def n_ops(self):
        return self.n_children()

    def set_op_input_at_uri(self,uri,val):
        """
        Set an op input at uri to provided value val.
        The uri must be a valid uri in the TreeModel,
        of the form opname.inputs.inpname.
        """
        path = uri.split('.')
        opname = path[0]
        if not path[1] == op.inputs_tag:
            msg = '[{}] uri {} does not point to an input'.format(__name__,uri)
            raise ValueError(msg)
        inpname = path[2]
        uri = opname+'.'+op.inputs_tag+'.'+inpname
        op = self.get_data_from_uri(opname)
        op.input_locator[inpname].data = val
        self.set_item(uri,val)


