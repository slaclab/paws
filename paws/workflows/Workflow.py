from __future__ import print_function
from collections import OrderedDict
import copy
from functools import partial
import traceback
import os

from ..models.TreeModel import TreeModel
from ..operations.Operation import Operation

class Workflow(TreeModel):
    """Workflow built from paws Operations, with TreeModel interface.
    
    This and other paws classes are TreeModels
    mostly for convenient gui interfacing.
    """

    def __init__(self):
        flag_dict = OrderedDict(selected=False,enabled=True)
        super(Workflow,self).__init__(flag_dict)
        self.inputs = OrderedDict()
        self.outputs = OrderedDict()
        self.op_inputs = OrderedDict()
        self.op_connections = OrderedDict()
        self.plugin_connections = OrderedDict()
        self.workflow_connections = OrderedDict()
        self.op_dependencies = OrderedDict() 
        self.operations = self._root_dict
        self.message_callback = self.tagged_print
        self.data_callback = self.set_item 
        self.stop_flag = False

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def add_operation(self,op_name,op):
        """Name and add an Operation to the Workflow.

        If `op_name` is not unique, 
        the existing Operation is overwritten.

        Parameters
        ----------
        op_name : str
            name to give to the new Operation 
        """
        #op.message_callback = self.message_callback
        op.data_callback = partial(self.set_op_item,op_name)
        self.set_item(op_name,op)

    def remove_operation(self,op_name):
        """Remove an Operation by providing its name as `op_name`."""
        self.remove_item(op_name)

    def n_operations(self):
        return len(self.operations) 

    def set_op_input(self,op_name,input_name,val):
        if not op_name in self.op_inputs: self.op_inputs[op_name] = OrderedDict()
        self.op_inputs[op_name][input_name] = val
        # TODO: consider whether to do this here vs at runtime
        self.operations[op_name].set_input(input_name,val)

    def connect(self,output_uri,input_map):
        """Connect the output at `output_uri` to one or more inputs.

        Sets up Operation inputs listed in `input_map`
        to take the value at `output_uri`.
        `input_map` can be a TreeItem uri (string) or a list thereof.
        """
        if output_uri in self.op_connections:
            if isinstance(input_map,list):
                self.op_connections[output_uri].extend(input_map)
            else:
                self.op_connections[output_uri].append(input_map)
        else:
            if not isinstance(input_map,list): input_map = [input_map]
            self.op_connections[output_uri] = input_map

    def connect_plugin(self,input_uri,plugin_item_uri):
        self.plugin_connections[input_uri] = plugin_item_uri

    def connect_workflow(self,input_uri,wf_name):
        self.workflow_connections[input_uri] = wf_name 

    def connect_input(self,input_name,targets):
        self.inputs[input_name] = targets

    def connect_output(self,output_name,targets):
        self.outputs[output_name] = targets

    def break_connection(self,io_uri):
        if io_uri in self.op_connections:
            self.op_connections.pop(input_uri)
        else:
            for o_uri,i_uris in self.op_connections.items():
                if io_uri in i_uris:
                    i_uris.pop(i_uris.index(io_uri))

    def break_input(self,input_name):
        if input_name in self.inputs:
            self.inputs.pop(input_name)
    
    def break_output(self,output_name):
        if output_name in self.outputs:
            self.outputs.pop(output_name)

    def get_outputs(self):
        d = OrderedDict()
        for out_name in self.outputs.keys():
            d[out_name] = self.get_output(out_name)
        return d

    def set_input(self,input_name,val):
        """Set a value for Operation inputs.

        If `input_name` is in self.inputs,
        `val` will be set for all self.inputs[`input_name`].
        """
        r = self.inputs[input_name]
        if not isinstance(r,list):
            r = [r]
        for uri in r:
            self.set_item(uri,val)

    def get_input(self,input_name):
        return self.get_data_from_uri(self.inputs[input_name])

    def get_output(self,output_name):
        return self.get_data_from_uri(self.outputs[output_name])

    def set_dependency(self,op_name,dependency_ops):
        """Set `op_name` to depend on one or more other `dependency_ops`"""
        if not isinstance(dependency_ops,list):
            dependency_ops = [dependency_ops]
        if op_name in self.op_dependencies.keys():
            self.op_dependencies[op_name].extend(dependency_ops)
        else:
            self.op_dependencies[op_name] = dependency_ops

    def get_dependencies(self,op_name):
        """Return all Operations that are dependencies of Operation `op_name`"""
        deps = []
        if op in self.op_dependencies:
            deps.extend(self.op_dependencies[op_name])
        for output_uri,input_map in self.op_connections.items():
            for input_uri in input_map:
                if input_uri.split('.')[0] == op_name:
                    new_dep = output_uri.split('.')[0]
                    if not new_dep in deps:
                        deps.append(new_dep)
        return deps

    def execution_stack(self):
        """Determine order of execution and diagnostics for the Workflow.

        Returns
        -------
        stk : list
            List of lists of Operation names,
            where each list contains Operations
            that can be executed after the Operations in the lists above them.
        diag : dict
            Gives diagnostic information for any Operations not ready to run. 
            Keys are operation names, values are diagnostic info (strings).
        """
        stk = []
        #valid_wf_inputs = [] 
        disabled_ops = []
        diagnostics = {}
        continue_flag = True
        while not stack_size(stk)+len(disabled_ops) == self.n_operations() and continue_flag:
            ops_rdy = []
            ops_not_rdy = []
            for op_name in self.operations.keys():
                op_rdy,op_diag = False,{}
                if not self.is_enabled(op_name):
                    op_rdy = False
                    op_diag = {op_name:'Operation is disabled'}
                elif not stack_contains(op_name,stk) and not op_name in disabled_ops:
                    if op_name in self.op_dependencies.keys():
                        dep_ops = self.get_dependencies(op_name)
                        if all([stack_contains(nm,stk) for nm in dep_ops]):
                            op_rdy,op_diag = True,{}
                        else:
                            op_rdy = False
                            op_diag = {op_name:'One or more unsatisfied dependencies ({}) '.format(dep_ops)}
                    else:
                        op_rdy,op_diag = True,{}
                diagnostics.update(op_diag)
                if op_rdy:
                    ops_rdy.append(op_name)
            ops_to_run = []
            if any(ops_rdy):
                for op_name in ops_rdy:
                    if self.is_enabled(op_name):
                        ops_to_run.append(op_name)
                    elif not op_name in disabled_ops:
                        disabled_ops.append(op_name) 
            if any(ops_to_run):
                stk.append(ops_to_run)
            else:
                continue_flag = False
        return stk,diagnostics

    def run(self):
        """Execute the Workflow.

        All of the operations in the Workflow that are ready
        will be executed in the order obtained from self.execution_stack()
        """
        self.stop_flag = False
        stk,diag = self.execution_stack()
        bad_diag_keys = [k for k in diag.keys() if diag[k]]
        for k in bad_diag_keys:
            self.message_callback('WARNING- {} is not ready: {}'.format(k,diag[k]))
        self.message_callback('workflow queue:'+os.linesep+print_stack(stk))
        for lst in stk:
            if self.stop_flag:
                self.message_callback('Workflow stopped.')
                return
            for op_name in lst: 
                self.message_callback('running: {}'.format(op_name))
                op = self.prepare_operation(op_name)
                op.stop_flag = False
                op.run() 
                for outnm,outdata in op.outputs.items():
                    self.data_callback(op_name+'.outputs.'+outnm,outdata)

    def prepare_operation(self,op_name):
        """Prepare according to op_connections, return the Operation"""
        for output_uri,input_map in self.op_connections.items():
            for input_uri in input_map:
                if input_uri.split('.')[0] == op_name:
                    self.set_item(input_uri,self.get_data_from_uri(output_uri))
        return self.get_data_from_uri(op_name) 
                    
    def stop(self):
        """Stop the Workflow and all of its Operations."""
        self.stop_flag = True
        stk,diag = self.execution_stack()
        for lst in stk:
            for op_name in lst: 
                self.get_data_from_uri(op_name).stop()

    def enable_op(self,opname):
        self.set_op_enabled(opname,True)

    def disable_op(self,opname):
        self.set_op_enabled(opname,False)

    def set_op_enabled(self,opname,flag=True):
        op_item = self.get_from_uri(opname)
        op_item.flags['enabled'] = flag

    def is_enabled(self,opname):
        op_item = self.get_from_uri(opname)
        return op_item.flags['enabled']

    def op_enabled_flags(self):
        dct = OrderedDict()
        for opnm in self.operations.keys():
            dct[opnm] = self.get_from_uri(opnm).flags['enabled']
        return dct

    def build_clone(self):
        """Produce a clone of this Workflow."""
        new_wf = self.clone() 
        new_wf.inputs = copy.deepcopy(self.inputs)
        new_wf.outputs = copy.deepcopy(self.outputs)
        new_wf.op_dependencies = copy.deepcopy(self.op_dependencies)
        new_wf.op_connections = copy.deepcopy(self.op_connections)
        # TODO: consider how to handle callbacks,
        # considering threading, parallel processing
        #new_wf.message_callback = self.message_callback
        #new_wf.data_callback = self.data_callback
        for op_name,op in self.operations.items():
            new_op = op.build_clone()
            new_wf.add_operation(op_name,new_op)
            if not self.is_enabled(op_name):
                new_wf.disable_op(op_name)
        return new_wf

    @classmethod
    def clone(cls):
        return cls()

    def build_tree(self,x):
        """Return a tree-like dict referencing the Workflow data.

        This is a reimplemention of TreeModel.build_tree().
        Reimplementing this allows Workflows to use TreeItem uris as keys.

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

def stack_contains(itm,stk):
    for lst in stk:
        if itm in lst:
            return True
    return False

def stack_size(stk):
    sz = 0
    for lst in stk:
        sz += len(lst)
    return sz

def print_stack(stk):
    stktxt = ''
    opt_newline = os.linesep
    n_layers = len(stk)
    for i,lst in enumerate(stk):
        if i == n_layers-1:
            opt_newline = ''
        stktxt += ('{}'+opt_newline).format(lst)
    return stktxt


