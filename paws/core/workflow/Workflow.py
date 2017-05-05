from collections import OrderedDict
import copy
from functools import partial

from ..models.TreeModel import TreeModel
from ..operations import optools
from ..operations.Operation import Operation, Batch, Realtime

class Workflow(TreeModel):
    """
    Tree structure for a Workflow built from paws Operations.
    """
    #Keeps a reference to its Workflow Manager,
    #which is specified as an initialization argument.

    def __init__(self):
        super(Workflow,self).__init__()
        #self.wfman = wfman

    def build_tree(self,x):
        """
        Reimplemented TreeModel.build_tree() 
        so that TreeItems are built from Operations.
        """
        if isinstance(x,Operation):
            d = OrderedDict()
            d[optools.inputs_tag] = self.build_tree(x.inputs)
            d[optools.outputs_tag] = self.build_tree(x.outputs)
            return d
        else:
            return super(Workflow,self).build_tree(x) 

    def op_dict(self):
        op_names = self.list_child_tags() 
        op_dict = OrderedDict(zip(op_names,[self.get_data_from_uri(nm) for nm in op_names]))
        return op_dict

    def set_op_input(self,opname,inputname,val):
        """
        Set an op input to provided value val.
        The uri built from op_name.inputs.input_name
        must be a valid uri in the TreeModel.
        """
        #op = self.get_data_from_uri(opname)
        #op.inputs[inputname] = val
        #op.input_locator[inputname].data = val
        uri = opname+'.'+optools.inputs_tag+'.'+inputname
        self.set_item(uri,val)

