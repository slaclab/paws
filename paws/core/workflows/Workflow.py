from __future__ import print_function
from collections import OrderedDict
import copy
from functools import partial
import traceback
import os

from ..models.TreeModel import TreeModel
from ..operations import Operation as opmod
from ..operations.Operation import Operation
from ..operations import optools

class Workflow(TreeModel):
    """
    Tree structure for a Workflow built from paws Operations.
    """

    def __init__(self):
        flag_dict = OrderedDict()
        flag_dict['select'] = False
        flag_dict['enable'] = True
        super(Workflow,self).__init__(flag_dict)
        self.inputs = OrderedDict()
        self.outputs = OrderedDict()
        self.message_callback = print
        self.data_callback = None

    #def __getitem__(self,key):
    #    optags = self.keys()
    #    if key in optags:
    #        return self.get_data_from_uri(key) 
    #    else:
    #        raise KeyError('[{}] {}.__getitem__ only recognizes keys {}'
    #        .format(__name__,type(self).__name__,optags))
    #def __setitem__(self,key,data):
    #    optags = self.keys() 
    #    # TODO: ensure that data is an Operation?
    #    if key in optags:
    #        self.set_item(key,data)
    #    else:
    #        raise KeyError('[{}] {}.__setitem__ only recognizes keys {}'
    #        .format(__name__,type(self).__name__,optags))
    #def keys(self):
    #    return self.list_op_tags() 

    def set_op_item(self,op_tag,item_uri,item_data):
        full_uri = op_tag+'.'+item_uri
        self.set_item(full_uri,item_data)

    def clone_wf(self):
        """
        Produce a Workflow that is a copy of this Workflow.
        """
        new_wf = self.clone() 
        #new_wf = copy.copy(self)
        new_wf.inputs = copy.deepcopy(self.inputs)
        new_wf.outputs = copy.deepcopy(self.outputs)
        # NOTE: is it ok if I don't copy.copy the callbacks? 
        new_wf.message_callback = self.message_callback
        new_wf.data_callback = self.data_callback
        for op_tag in self.list_op_tags():
            op = self.get_data_from_uri(op_tag)
            new_wf.add_op(op_tag,op.clone_op())
        return new_wf

    @classmethod
    def clone(cls):
        return cls()

    def add_op(self,op_tag,op):
        op.message_callback = self.message_callback
        op.data_callback = partial( self.set_op_item,op_tag )
        self.set_item(op_tag,op)

    def build_tree(self,x):
        """
        Reimplemented TreeModel.build_tree() 
        so that TreeItems are built from Operations.
        """
        if isinstance(x,Operation):
            d = OrderedDict()
            d['inputs'] = self.build_tree(x.inputs)
            d['outputs'] = self.build_tree(x.outputs)
            return d
        else:
            return super(Workflow,self).build_tree(x) 

    def op_dict(self):
        optags = self.list_op_tags() 
        return OrderedDict(zip(optags,[self.get_data_from_uri(nm) for nm in optags]))

    def list_op_tags(self):
        return self.root_tags()

    def n_ops(self):
        return self.n_children()

    def connect_wf_input(self,wf_input_name,op_input_uris):
        self.inputs[wf_input_name] = op_input_uris

    def connect_wf_output(self,wf_output_name,op_output_uris):
        self.outputs[wf_output_name] = op_output_uris

    def break_wf_input(self,wf_input_name):
        self.inputs.pop(wf_input_name)
    
    def break_wf_output(self,wf_output_name):
        self.outputs.pop(wf_output_name)

    def wf_outputs_dict(self):
        d = OrderedDict()
        for wfoutnm in self.outputs.keys():
            # if the uri referred to by this output exists, save it
            if self.contains_uri(self.outputs[wfoutnm]):
                d[wfoutnm] = self.get_data_from_uri(self.outputs[wfoutnm])
        return d

    def get_wf_output(self,wf_output_name):
        """
        Fetch and return the Operation output(s)
        indicated by self.outputs[wf_output_name].
        """
        r = self.outputs[wf_output_name]
        if isinstance(r,list):
            return [self.get_data_from_uri(q) for q in r]
        else:
            return self.get_data_from_uri(r)

    def set_wf_input(self,wf_input_name,val):
        """
        Take the Operation input(s) 
        indicated by self.inputs[wf_input_name],
        and set them to the input value val. 
        """
        urilist = self.inputs[wf_input_name]
        if not isinstance(urilist,list):
            urilist = [urilist]
        for uri in urilist:
            p = uri.split('.')
            il = self.get_data_from_uri(p[0]).input_locator[p[2]]
            il.val = val
            if il.tp in [opmod.basic_type,opmod.runtime_type]:
                # these two types should be loaded for immediate use
                self.set_item(uri,val)

    def execute(self):
        stk,diag = self.execution_stack()
        bad_diag_keys = [k for k in diag.keys() if diag[k]]
        for k in bad_diag_keys:
            self.message_callback('WARNING- {} is not ready: {}'.format(k,diag[k]))
        self.message_callback('workflow queue:'+os.linesep+self.print_stack(stk))
        for lst in stk:
            self.message_callback('running: {}'.format(lst))
            for op_tag in lst: 
                op = self.get_data_from_uri(op_tag) 
                for inpnm,il in op.input_locator.items():
                    if il.tp == opmod.workflow_item:
                        self.set_op_item(op_tag,'inputs.'+inpnm,self.locate_input(il))
                op.run() 
                for outnm,outdata in op.outputs.items():
                    self.set_op_item(op_tag,'outputs.'+outnm,outdata)

    def locate_input(self,il):
        if isinstance(il.val,list):
            return [self.get_data_from_uri(v) for v in il.val]
        else:
            return self.get_data_from_uri(il.val)

    def set_op_enabled(self,opname,flag=True):
        op_item = self.get_from_uri(opname)
        op_item.flags['enable'] = flag

    def is_op_enabled(self,opname):
        op_item = self.get_from_uri(opname)
        return op_item.flags['enable']

    def op_enable_flags(self):
        dct = OrderedDict()
        for opnm in self.list_op_tags():
            dct[opnm] = self.get_from_uri(opnm).flags['enable']
        return dct

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
            for op_tag in self.list_op_tags():
                if not self.is_op_enabled(op_tag):
                    op_rdy = False
                    op_diag = {op_tag:'Operation is disabled'}
                elif not self.stack_contains(op_tag,stk):
                    op = self.get_data_from_uri(op_tag)
                    op_rdy,op_diag = self.is_op_ready(op_tag,self,valid_wf_inputs)
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

    def wf_setup_dict(self):
        wf_dict = OrderedDict() 
        for opname in self.list_op_tags():
            op = self.get_data_from_uri(opname)
            wf_dict[opname] = op.setup_dict()
        wf_dict['WORKFLOW_INPUTS'] = self.inputs
        wf_dict['WORKFLOW_OUTPUTS'] = self.outputs
        wf_dict['OP_ENABLE_FLAGS'] = self.op_enable_flags()
        return wf_dict

    def build_op_from_dict(self,op_setup,op_manager):
        op_uri = op_setup['op_module']
        op_manager.set_op_enabled(op_uri)
        op = op_manager.get_data_from_uri(op_uri)()
        op.load_defaults()
        il_setup_dict = op_setup['inputs']
        for nm in op.inputs.keys():
            if nm in il_setup_dict.keys():
                tp = il_setup_dict[nm]['tp']
                val = il_setup_dict[nm]['val']
                op.input_locator[nm] = opmod.InputLocator(tp,val) 
        return op

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

    @staticmethod
    def is_op_ready(op_tag,wf,valid_wf_inputs):
        op = wf.get_data_from_uri(op_tag)
        inputs_rdy = []
        diagnostics = {} 
        for name,il in op.input_locator.items():
            msg = ''
            if il.tp == opmod.workflow_item:
                inp_rdy = False
                if isinstance(il.val,list):
                    if all([v in valid_wf_inputs for v in il.val]):
                        inp_rdy = True 
                else:
                    if il.val in valid_wf_inputs: 
                        inp_rdy = True 
                if not inp_rdy:
                    msg = str('Operation input {} (={}) '.format(name,il.val)
                    + 'not satisfied by valid inputs list: {}'.format(valid_wf_inputs))
            else:
                inp_rdy = True
            inputs_rdy.append(inp_rdy)
            diagnostics[op_tag+'.inputs.'+name] = msg
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
        valid_wf_inputs = [op_tag,op_tag+'.inputs',op_tag+'.outputs']
        valid_wf_inputs += [op_tag+'.outputs.'+k for k in op.outputs.keys()]
        valid_wf_inputs += [op_tag+'.inputs.'+k for k in op.inputs.keys()]
        return valid_wf_inputs

    @staticmethod
    def print_stack(stk):
        stktxt = ''
        opt_newline = '\n'
        for i,lst in zip(range(len(stk)),stk):
            if i == len(stk)-1:
                opt_newline = ''
            if len(lst) > 1:
                if isinstance(lst[1],list):
                    substk = lst[1]
                    stktxt += ('[\'{}\':\n{}\n]'+opt_newline).format(lst[0],print_stack(lst[1]))
                else:
                    stktxt += ('{}'+opt_newline).format(lst)
            else:
                stktxt += ('{}'+opt_newline).format(lst)
        return stktxt


