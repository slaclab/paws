from collections import OrderedDict
import copy
from functools import partial

from ..models.TreeModel import TreeModel
from ..operations import optools
from ..operations.Operation import Operation, Batch, Realtime

class Workflow(TreeModel):
    """
    Tree structure for a Workflow built from paws Operations.
    Keeps a reference to its Workflow Manager,
    which is specified as an initialization argument.
    """

    def __init__(self,wfman):
        super(Workflow,self).__init__()
        self.wfman = wfman

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

    # TODO: the following
    def check_wf(self):
        """
        Check the dependencies of the workflow.
        Ensure that all loaded operations have inputs that make sense.
        Return a status code and message for each of the Operations.
        """
        pass

    def execution_stack(self):
        """
        Build a stack (list) of lists of Operation uris,
        such that each list indicates a set of Operations
        whose dependencies are satisfied by the Operations above them.
        For Batch or Realtime operations, 
        the layer should be of the form[batch_name,[batch_stack]],
        where batch_name indicates the batch controller Operation,
        and batch_stack is built from self.batch_op_stack().
        """
        stk = []
        valid_wf_inputs = []
        diagnostics = {}
        continue_flag = True
        while not optools.stack_size(stk) == self.n_items() and continue_flag:
            ops_rdy = []
            ops_not_rdy = []
            for itm in self._root_item.children:
                if not optools.stack_contains(itm.tag,stk):
                    op_rdy,op_diag = self.is_op_ready(itm.tag,valid_wf_inputs)
                    diagnostics.update(op_diag)
                    if op_rdy:
                        ops_rdy.append(itm.tag)
                    else:
                        ops_not_rdy.append(itm.tag)
            # Finished building list of ops currently ready. Now filter these into stack.
            if any(ops_rdy):
                # Which of these are not Batch/Realtime ops?
                non_batch_rdy = []
                for op_tag in ops_rdy:
                    op = self.get_data_from_uri(op_tag)
                    if not isinstance(op,Batch) and not isinstance(op,Realtime):
                        non_batch_rdy.append(op_tag)
                if any(non_batch_rdy):
                    ops_rdy = non_batch_rdy
                    stk.append(ops_rdy)
                    for op_tag in ops_rdy:
                        op = self.get_data_from_uri(op_tag)
                        valid_wf_inputs += optools.get_valid_wf_inputs(op_tag,op)
                else:
                    batch_tag = ops_rdy[0]
                    ops_rdy = [batch_tag]
                    batch_op = self.get_data_from_uri(batch_tag)
                    batch_stk,batch_rdy,batch_diag = self.batch_op_stack(batch_tag,valid_wf_inputs)
                    diagnostics.update(batch_diag)
                    stk.append([batch_tag,batch_stk])
                    valid_wf_inputs += optools.get_valid_wf_inputs(batch_tag,batch_op)
            else:
                continue_flag = False
        #print optools.print_stack(stk)
        return stk,diagnostics

    def print_stack(self,stk):
        stktxt = ''
        opt_newline = '\n'
        for i,lst in zip(range(len(stk)),stk):
            if i == len(stk)-1:
                opt_newline = ''
            first_op = self.get_data_from_uri(lst[0])
            if isinstance(first_op,Batch) or isinstance(first_op,Realtime):
                substk = lst[1]
                stktxt += ('[\'{}\':\n{}\n]'+opt_newline).format(lst[0],self.print_stack(lst[1]))
            else:
                stktxt += ('{}'+opt_newline).format(lst)
        return stktxt

    def is_op_ready(self,op_tag,valid_wf_inputs,batch_routes=[]):
        op = self.get_data_from_uri(op_tag)
        if isinstance(op,Batch):
            b_stk,op_rdy,diagnostics = self.batch_op_stack(op_tag,valid_wf_inputs)
        elif isinstance(op,Realtime):
            rt_stk,op_rdy,diagnostics = self.batch_op_stack(op_tag,valid_wf_inputs)
        else:
            inputs_rdy = []
            diagnostics = {} 
            for name,il in op.input_locator.items():
                msg = ''
                if il.src == optools.wf_input and il.tp == optools.ref_type and not il.val in valid_wf_inputs:
                    inp_rdy = False
                    msg = str('Operation input {}.inputs.{} (={}) '.format(op_tag,name,il.val)
                    + 'not found in valid Workflow input list: {}'.format(valid_wf_inputs))
                elif il.src == optools.batch_input and not op_tag+'.'+optools.inputs_tag+'.'+name in batch_routes:
                    inp_rdy = False
                    msg = str('Operation input {}.inputs.{} (={}) '.format(op_tag,name,il.val)
                    + 'expects batch input but is not listed in batch routes: {}'.format(batch_routes))
                else:
                    inp_rdy = True
                inputs_rdy.append(inp_rdy)
                diagnostics[op_tag+'.'+optools.inputs_tag+'.'+name] = msg
            if all(inputs_rdy):
                op_rdy = True
            else:
                op_rdy = False
        return op_rdy,diagnostics 

    def batch_op_stack(self,batch_op_tag,valid_wf_inputs):
        """
        Use batch_op.batch_ops() and a list of valid_wf_inputs 
        to build a stack (list) of lists of operations suitable for serial execution.
        """
        batch_op = self.get_data_from_uri(batch_op_tag)
        # Batch and Realtime execution operations expect to have their inputs loaded
        # by optools.load_inputs() before calling realtime_ops() or batch_ops()
        optools.load_inputs(batch_op,self)
        op_tags = []
        if isinstance(batch_op,Realtime):
            op_tags = batch_op.realtime_ops()
        elif isinstance(batch_op,Batch):
            op_tags = batch_op.batch_ops()
        # make a copy of valid_wf_inputs
        # so that the existing valid_wf_inputs list is not mutated 
        valid_batch_inputs = copy.copy(valid_wf_inputs)
        # add the batch's own valid inputs to the list
        valid_batch_inputs += optools.get_valid_wf_inputs(batch_op_tag,batch_op)
        # build the batch substack
        b_stk = []
        layer = []
        diagnostics = {}
        for op_tag in op_tags:
            op_rdy,op_diag = self.is_op_ready(op_tag,valid_batch_inputs,batch_op.input_routes())
            diagnostics.update(op_diag)
            if op_rdy:
                layer.append(op_tag)
        while any(layer):
            b_stk.append(layer)
            for op_tag in layer:
                op = self.get_data_from_uri(op_tag)
                valid_batch_inputs += optools.get_valid_wf_inputs(op_tag,op)
            layer = []
            for op_tag in op_tags:
                op_rdy,op_diag = self.is_op_ready(op_tag,valid_batch_inputs,batch_op.input_routes())
                diagnostics.update(op_diag)
                if op_rdy and not optools.stack_contains(op_tag,b_stk):
                    layer.append(op_tag)
        b_rdy = len(op_tags) == optools.stack_size(b_stk) 
        return b_stk,b_rdy,diagnostics 

