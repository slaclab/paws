from collections import OrderedDict
import copy
from functools import partial
import traceback

from ..models.TreeModel import TreeModel
from ..operations import Operation as opmod
from ..operations.Operation import Operation#, Batch, Realtime
from ..operations import optools

class Workflow(TreeModel):
    """
    Tree structure for a Workflow built from paws Operations.
    """

    def __init__(self,wfman):
        flag_dict = OrderedDict()
        flag_dict['select'] = False
        flag_dict['enable'] = True
        super(Workflow,self).__init__(flag_dict)
        self.wf_manager = wfman
        self.inputs = OrderedDict()
        self.outputs = OrderedDict()
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

    def write_log(self,msg):
        self.wf_manager.write_log(msg)

    def build_tree(self,x):
        """
        Reimplemented TreeModel.build_tree() 
        so that TreeItems are built from Operations.
        """
        if isinstance(x,Operation):
            d = OrderedDict()
            d[opmod.inputs_tag] = self.build_tree(x.inputs)
            d[opmod.outputs_tag] = self.build_tree(x.outputs)
            return d
        else:
            return super(Workflow,self).build_tree(x) 

    def execute(self):
        stk,diag = self.execution_stack()
        for lst in stk:
            self.write_log('running: {}...'.format(lst))
            for op_tag in lst: 
                op = self.get_data_from_uri(op_tag) 
                self.load_inputs(op,self.wf_manager,self.wf_manager.plugin_manager)
                try:
                    op.run() 
                except Exception as ex:
                    tb = traceback.format_exc()
                    self.write_log(str('Operation {} threw an error. '
                    + '\nMessage: {} \nTrace: {}').format(op_tag,ex.message,tb)) 
                self.set_item(op_tag,op)
            #self.workflows[wfname].execute(op_list)
            self.write_log('... finished'.format(lst))

    def load_inputs(self,op,wf_manager=None,plugin_manager=None):
        """
        Loads input data for an Operation from its input_locators.
        A WfManager and a PluginManager can be provided 
        as optional arguments,
        in which case they are used to fetch data.
        """
        for name,il in op.input_locator.items():
            il.data = optools.locate_input(il,self,wf_manager,plugin_manager)
            op.inputs[name] = il.data

    def op_dict(self):
        optags = self.list_op_tags() 
        op_dict = OrderedDict(zip(optags,[self.get_data_from_uri(nm) for nm in optags]))
        return op_dict

    def list_op_tags(self):
        return self.root_tags()

    def n_ops(self):
        return self.n_children()

    def break_wf_input(self,wf_input_name):
        self.inputs.pop(wf_input_name)
    
    def connect_wf_input(self,wf_input_name,op_input_uri):
        self.inputs[wf_input_name] = op_input_uri

    def connect_wf_output(self,wf_output_name,op_output_uri):
        self.outputs[wf_output_name] = op_output_uri

    def wf_outputs_dict(self):
        d = OrderedDict()
        for wfoutnm in self.outputs.keys():
            d[wfoutnm] = self.get_data_from_uri(self.outputs[wfoutnm])
        return d

    def get_wf_output(wf_output_name):
        return self.get_data_from_uri(self.outputs[wf_output_name])

    def set_wf_input(self,wf_input_name,val):
        self.set_op_input_at_uri(self.inputs[wf_input_name],val)

    def set_op_input_at_uri(self,uri,val):
        """
        Set an op input at uri to provided value val.
        The uri must be a valid uri in the TreeModel,
        of the form opname.inputs.inpname.
        """
        path = uri.split('.')
        opname = path[0]
        if not path[1] == opmod.inputs_tag:
            msg = '[{}] uri {} does not point to an input'.format(__name__,uri)
            raise ValueError(msg)
        inpname = path[2]
        uri = opname+'.'+opmod.inputs_tag+'.'+inpname
        op = self.get_data_from_uri(opname)
        op.input_locator[inpname].val = val
        #op.input_locator[inpname].data = val
        #op.inputs[inpname] = val
        self.set_item(uri,val)

    def set_op_enabled(self,opname,flag=True):
        op_item = self.get_from_uri(opname)
        op_item.flags['enable'] = flag

    def is_op_enabled(self,opname):
        op_item = self.get_from_uri(opname)
        return op_item.flags['enable']

    def execution_stack(self):
        """
        Build a stack (list) of lists of Operation uris,
        such that each list indicates a set of Operations
        whose dependencies are satisfied by the Operations above them.
        """
        stk = []
        valid_wf_inputs = [] 
        diagnostics = {}
        continue_flag = True
        while not self.stack_size(stk) == self.n_ops() and continue_flag:
            ops_rdy = []
            ops_not_rdy = []
            #print 'continue: {}, stacksize: {}, n_ops: {}'.format(continue_flag,self.stack_size(stk),self.n_ops())
            for op_tag in self.list_op_tags():
                if not self.is_op_enabled(op_tag):
                    op_rdy = False
                    op_diag = 'Operation is disabled' 
                elif not self.stack_contains(op_tag,stk):
                    op_rdy,op_diag = self.is_op_ready(op_tag,valid_wf_inputs)
                diagnostics.update(op_diag)
                if op_rdy:
                    ops_rdy.append(op_tag)
                else:
                    ops_not_rdy.append(op_tag)
            if any(ops_rdy):
                stk.append(ops_rdy)
                for op_tag in ops_rdy:
                    op = self.get_data_from_uri(op_tag)
                    valid_wf_inputs += self.get_valid_wf_inputs(op_tag,op)
            else:
                continue_flag = False
        return stk,diagnostics
        # Finished building list of ops currently ready. Now filter these into stack.
        #if any(ops_rdy):
        #     Which of these are not Batch/Realtime ops?
        #    non_batch_rdy = []
        #    for op_tag in ops_rdy:
        #        op = wf.get_data_from_uri(op_tag)
        #        if not any([op._batch_flag,op._realtime_flag]):
        #            non_batch_rdy.append(op_tag)
        #    if any(non_batch_rdy):
        #        ops_rdy = non_batch_rdy
        #        stk.append(ops_rdy)
        #        for op_tag in ops_rdy:
        #            op = wf.get_data_from_uri(op_tag)
        #            valid_wf_inputs += get_valid_wf_inputs(op_tag,op)
        #    else:
        #        batch_tag = ops_rdy[0]
        #        ops_rdy = [batch_tag]
        #        batch_op = wf.get_data_from_uri(batch_tag)
        #        batch_stk,batch_rdy,batch_diag = batch_op_stack(
        #        wf,batch_tag,valid_wf_inputs)
        #        diagnostics.update(batch_diag)
        #        stk.append([batch_tag,batch_stk])
        #        valid_wf_inputs += get_valid_wf_inputs(batch_tag,batch_op)
        #else:
        #    continue_flag = False

    @staticmethod
    def stack_contains(itm,stk):
        for lst in stk:
            if itm in lst:
                return True
            for lst_itm in lst:
                if isinstance(lst_itm,list):
                    if stack_contains(itm,lst_itm):
                        return True
        return False

    @staticmethod
    def stack_size(stk):
        sz = 0
        for lst in stk:
            for lst_itm in lst:
                if isinstance(lst_itm,list):
                    sz += stack_size(lst_itm)
                else:
                    sz += 1
        return sz

    def is_op_ready(self,op_tag,valid_wf_inputs,batch_routes=[]):
        op = self.get_data_from_uri(op_tag)
        inputs_rdy = []
        diagnostics = {} 
        for name,il in op.input_locator.items():
            msg = ''
            if (il.tp == opmod.workflow_item 
            and not il.val in valid_wf_inputs): 
                inp_rdy = False
                msg = str('Operation input {}.inputs.{} (={}) '.format(op_tag,name,il.val)
                + 'not found in valid Workflow input list: {}'.format(valid_wf_inputs)
                + 'or in workflows: {}'.format(self.wf_manager.workflows.keys()))
            else:
                inp_rdy = True
            inputs_rdy.append(inp_rdy)
            diagnostics[op_tag+'.'+opmod.inputs_tag+'.'+name] = msg
        if all(inputs_rdy):
            op_rdy = True
        else:
            op_rdy = False
        return op_rdy,diagnostics 

    @staticmethod
    def get_valid_wf_inputs(op_tag,op):
        """
        Return the TreeModel uris of the op and its inputs/outputs 
        that are eligible as downstream inputs in the workflow.
        """
        # valid_wf_inputs should be the operation, its input and output dicts, and their respective entries
        valid_wf_inputs = [op_tag,op_tag+'.'+opmod.inputs_tag,op_tag+'.'+opmod.outputs_tag]
        valid_wf_inputs += [op_tag+'.'+opmod.outputs_tag+'.'+k for k in op.outputs.keys()]
        valid_wf_inputs += [op_tag+'.'+opmod.inputs_tag+'.'+k for k in op.inputs.keys()]
        return valid_wf_inputs
    

