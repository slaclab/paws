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
    """Workflow built from paws Operations, with TreeModel interface.
    
    This and other paws classes are TreeModels
    mostly for graphical considerations,
    where these (pure python) TreeModels can interface 
    with gui-based tree views by adding a relatively thin adapter,
    such as paws.qt.QTreeModel.QTreeModel.
    """

    def __init__(self):
        flag_dict = OrderedDict()
        flag_dict['select'] = False
        flag_dict['enable'] = True
        super(Workflow,self).__init__(flag_dict)
        self.inputs = OrderedDict()
        self.outputs = OrderedDict()
        self.operations = self._root_dict
        self.message_callback = print
        self.data_callback = None
        self.stop_flag = False

    def add_operation(self,op_name,op):
        """Name and add an Operation to the Workflow.

        If `op_name` is not unique, 
        this existing Operation is overwritten.

        Parameters
        ----------
        op_name : str
            name to give to the new Operation 
        """
        op.message_callback = self.message_callback
        op.data_callback = partial(self.set_op_item,op_name)
        self.set_item(op_name,op)

    def load_operation(self,op_name,op_setup_dict,op_manager):
        """Load an Operation from a dict that specifies its parameters.

        If `op_name` is not unique, the Operation is overwritten.

        Parameters
        ----------
        op_name : str
            name to be given to the new Operation 
        op_setup_dict : dict
            dict specifying Operation setup
        """
        op_uri = op_setup_dict['op_module']
        if not op_manager.is_op_activated(op_uri):
            op_manager.activate_op(op_uri)
        op = op_manager.get_data_from_uri(op_uri)()
        self.add_operation(op_name,op)
        il_setup_dict = op_setup_dict['inputs']
        for inp_name in op.inputs.keys():
            if inp_name in il_setup_dict.keys():
                tp = il_setup_dict[inp_name]['tp']
                val = il_setup_dict[inp_name]['val']
                self.set_op_input(op_name,inp_name,val,tp)

    def remove_operation(self,op_name):
        """Remove an Operation by providing its name as `op_name`."""
        self.remove_item(op_name)

    def n_operations(self):
        return len(self.operations) 

    def set_op_input(self,op_name,input_name,val,tp=None):
        """Set up the Operation input at `op_input_uri`.

        This changes op.input_locator indicated by `op_input_uri`
        to refer to the new value `val` and type `tp`.
        For basic and runtime input types,
        the value is also loaded directly into op.inputs.
        For runtime inputs, the value is not stored in the input_locator,
        and this is on purpose, to prevent serializing those objects later.

        Parameters
        ----------
        op_name : str
            name of the Operation 
        input_name : str
            name of the input
        val : object
            any object to set as the Operation input value
        tp : str or int, optional
            the input type determines how the Workflow 
            interprets the input value.
            For example, 
            the input can be set to another Operation output,
            to be found at 'process.outputs.out1',
            or simply be set to the string 'process.outputs.out1',
            depending on the specified type.
            Valid types are any string in paws.core.operations.Operation.input_types,
            or any integer in paws.core.operations.Operation.valid_types.
            If not provided, the type is left at its previous setting.
        """
        if not op_name in self.operations.keys():
            msg = 'Operation {} not found in workflow'\
            .format(op_name)
            raise KeyError(msg)
        if not input_name in self.operations[op_name].inputs.keys():
            msg = str('Input name {} not valid for Operation {} ({}).'
            .format(input_name,op_name,type(self.operations[op_name]).__name__))
            raise KeyError(msg)
        if tp is not None and not tp in opmod.valid_types and not tp in opmod.input_types:
            # tp is neither a string or an enum
            msg = '[{}] failed to parse input type: {}'.format(
            __name__,tp)
            raise ValueError(msg)
        il = self.operations[op_name].input_locator[input_name]
        if tp is not None:
            if tp in opmod.input_types:
                tp = opmod.input_types.index(tp)
            il.tp = opmod.valid_types[tp]
        if not il.tp == opmod.runtime_type:
            il.val = val
        else:
            # set inputlocator.val to None, 
            # so that this object will NOT attempt
            # to be serialized when save_to_wfl() is called.
            il.val = None
        if il.tp in [opmod.basic_type,opmod.runtime_type]:
            # these types should be loaded for immediate use
            self.set_item(op_name+'.inputs.'+input_name,val)

    def connect_input(self,wf_input_name,op_input_uris):
        self.inputs[wf_input_name] = op_input_uris

    def connect_output(self,wf_output_name,op_output_uris):
        self.outputs[wf_output_name] = op_output_uris

    def break_input(self,wf_input_name):
        self.inputs.pop(wf_input_name)
    
    def break_output(self,wf_output_name):
        self.outputs.pop(wf_output_name)

    def workflow_outputs(self):
        d = OrderedDict()
        for wf_out_name in self.outputs.keys():
            d[wf_out_name] = self.get_wf_output(wf_out_name)
        return d

    def set_wf_input(self,wf_input_name,val,tp=None):
        """Set a value for all inputs in self.inputs[`wf_input_name`]."""
        urilist = self.inputs[wf_input_name]
        if not isinstance(urilist,list):
            urilist = [urilist]
        for uri in urilist:
            p = uri.split('.')
            if len(p) > 2 and p[1] == 'inputs':
                self.set_op_input(p[0],p[2],val,tp)
            else:
                self.set_item(uri,val)

    def get_wf_input_value(self,wf_input_name):
        uri = self.inputs[wf_input_name]
        if isinstance(uri,list):
            uri = uri[0]
        p = uri.split('.')
        il = self.get_data_from_uri(p[0]).input_locator[p[2]]
        return il.val  

    def get_wf_output(self,wf_output_name):
        """Get all outputs in self.outputs[`wf_output_name`]."""
        r = self.outputs[wf_output_name]
        if isinstance(r,list):
            dl = []
            for rr in r:
                if self.contains_uri(rr):
                    dl.append(self.get_data_from_uri(rr))
                else:
                    dl.append(None)
            return dl
        else:
            if self.contains_uri(r):
                return self.get_data_from_uri(r)
            else:
                return None

    def execution_stack(self):
        """Determine order of execution and diagnostics for the Workflow.

        Returns a tuple (list,dict). 
        For any Operation that is not ready to execute,
        the dict gives information as to why it is not ready. 
       
        Returns
        -------
        stk : list
            List of lists of Operation names,
            where each list contains Operations
            whose dependencies are satisfied by the Operations above them.
        diag : dict
            Gives diagnostic information for any Operations not ready to run. 
            Keys are operation names, values are diagnostic info (strings).
        """
        stk = []
        valid_wf_inputs = [] 
        diagnostics = {}
        continue_flag = True
        while not self.stack_size(stk) == self.n_operations() and continue_flag:
            ops_rdy = []
            ops_not_rdy = []
            for op_name in self.operations.keys():
                if not self.is_op_enabled(op_name):
                    op_rdy = False
                    op_diag = {op_name:'Operation is disabled'}
                elif not self.stack_contains(op_name,stk):
                    op = self.get_data_from_uri(op_name)
                    op_rdy,op_diag = self.is_op_ready(op_name,valid_wf_inputs)
                    diagnostics.update(op_diag)
                    if op_rdy:
                        ops_rdy.append(op_name)
            if any(ops_rdy):
                stk.append(ops_rdy)
                for op_name in ops_rdy:
                    op = self.get_data_from_uri(op_name)
                    valid_wf_inputs += self.get_valid_wf_inputs(op_name,op)
            else:
                continue_flag = False
        return stk,diagnostics

    def is_op_ready(self,op_name,valid_wf_inputs):
        """self.execution_stack() uses this to check if an Operation is ready"""
        op = self.get_data_from_uri(op_name)
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
            diagnostics[op_name+'.inputs.'+name] = msg
        if all(inputs_rdy):
            op_rdy = True
        else:
            op_rdy = False
        return op_rdy,diagnostics 

    def execute(self):
        """Execute the Workflow.

        All of the operations in the Workflow that are ready
        will be executed in the order obtained from self.execution_stack()
        """
        self.stop_flag = False
        stk,diag = self.execution_stack()
        bad_diag_keys = [k for k in diag.keys() if diag[k]]
        for k in bad_diag_keys:
            self.message_callback('WARNING- {} is not ready: {}'.format(k,diag[k]))
        self.message_callback('workflow queue:'+os.linesep+self.print_stack(stk))
        for lst in stk:
            if self.stop_flag:
                self.message_callback('Workflow stopped.')
                return
            self.message_callback('running: {}'.format(lst))
            for op_name in lst: 
                op = self.get_data_from_uri(op_name) 
                for inpnm,il in op.input_locator.items():
                    if il.tp == opmod.workflow_item:
                        self.set_op_item(op_name,'inputs.'+inpnm,self.locate_input(il))
                op.stop_flag = False
                op.run() 
                for outnm,outdata in op.outputs.items():
                    self.set_op_item(op_name,'outputs.'+outnm,outdata)

    def stop(self):
        """Stop the Workflow.

        If any long-running Operations in the Workflow
        are written to examine their _stop_flag periodically,
        all execution should exit relatively soon.
        """
        self.stop_flag = True
        stk,diag = self.execution_stack()
        for lst in stk:
            for op_name in lst: 
                op = self.get_data_from_uri(op_name) 
                op.stop()

    def enable_op(self,opname):
        self.set_op_enabled(opname,True)

    def disable_op(self,opname):
        self.set_op_enabled(opname,False)

    def set_op_enabled(self,opname,flag=True):
        op_item = self.get_from_uri(opname)
        op_item.flags['enable'] = flag

    def is_op_enabled(self,opname):
        op_item = self.get_from_uri(opname)
        return op_item.flags['enable']

    def op_enable_flags(self):
        dct = OrderedDict()
        for opnm in self.operations.keys():
            dct[opnm] = self.get_from_uri(opnm).flags['enable']
        return dct

    def setup_dict(self):
        """Return a dict that describes the Workflow setup.""" 
        wf_dict = OrderedDict() 
        for op_name,op in self.operations.items():
            wf_dict[op_name] = op.setup_dict()
        wf_dict['WORKFLOW_INPUTS'] = self.inputs
        wf_dict['WORKFLOW_OUTPUTS'] = self.outputs
        wf_dict['OP_ENABLE_FLAGS'] = self.op_enable_flags()
        return wf_dict

    def clone_wf(self):
        """Produce a clone of this Workflow."""
        new_wf = self.clone() 
        new_wf.inputs = copy.deepcopy(self.inputs)
        new_wf.outputs = copy.deepcopy(self.outputs)
        # NOTE 1: cloned workflows will dump messages to self.message_callback 
        new_wf.message_callback = self.message_callback
        # NOTE 2: they will also dump their data to self.data_callback.
        # In cases where this is undesirable,
        # e.g. when running multiple clones in parallel, 
        # this data_callback should be disconnected after cloning.
        # This default setting is mostly intended for the use case
        # of cloning the workflow to run it in a separate thread.
        new_wf.data_callback = self.data_callback
        for op_name,op in self.operations.items():
            new_wf.add_operation(op_name,op.clone_op())
            if not self.is_op_enabled(op_name):
                new_wf.disable_op(op_name)
        return new_wf

    @classmethod
    def clone(cls):
        return cls()

    def build_tree(self,x):
        """Return a dict describing a tree-like structure of this object.

        This is a reimplemention of TreeModel.build_tree() 
        to define this object's child tree structure.
        For a Workflow, a dict is provided for each Operation,
        where the operation dict contains the results of calling
        self.build_tree(op.inputs) and self.build_tree(op.outputs). 
        """
        if isinstance(x,Operation):
            d = OrderedDict()
            d['inputs'] = self.build_tree(x.inputs)
            d['outputs'] = self.build_tree(x.outputs)
            return d
        else:
            return super(Workflow,self).build_tree(x) 


    def set_op_item(self,op_name,item_uri,item_data):
        """Subroutine for use with functools.partial for callbacks"""
        full_uri = op_name+'.'+item_uri
        self.set_item(full_uri,item_data)

    def locate_input(self,il):
        if isinstance(il.val,list):
            return [self.get_data_from_uri(v) for v in il.val]
        else:
            return self.get_data_from_uri(il.val)

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
    def get_valid_wf_inputs(op_name,op):
        """Get all valid uris referring to Operation data.

        Returns the TreeModel uris of the Operation,
        its inputs and outputs dicts,
        and each of the data items in the inputs and outputs dicts.
        """
        # valid_wf_inputs should be the operation, its input and output dicts, and their respective entries
        valid_wf_inputs = [op_name,op_name+'.inputs',op_name+'.outputs']
        valid_wf_inputs += [op_name+'.outputs.'+k for k in op.outputs.keys()]
        valid_wf_inputs += [op_name+'.inputs.'+k for k in op.inputs.keys()]
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



