from __future__ import print_function
from collections import OrderedDict
import copy
from functools import partial

from ..pawstools import DictTree 

class Workflow(DictTree):
    """Workflow built from paws Operations, with DictTree interface."""

    def __init__(self,inputs,outputs):
        super(Workflow,self).__init__()
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.outputs = OrderedDict(copy.deepcopy(outputs))
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.output_doc = OrderedDict.fromkeys(self.outputs.keys()) 
        self._module_path = __name__

        # TODO: debug, ensure _module_path agrees with WfManager.load_workflow()
        #self.tagged_print(self._module_path)


        #self.input_map = OrderedDict()
        #self.output_map = OrderedDict()
        #self.op_inputs = OrderedDict()
        #self.op_connections = OrderedDict()
        #self.plugin_connections = OrderedDict()
        #self.workflow_connections = OrderedDict()
        #self.op_dependencies = OrderedDict() 
        self.operations = self._root
        self.ops_enabled = OrderedDict() 
        self.message_callback = self.tagged_print
        self.data_callback = self.set_data
        self.stop_flag = False

    def add_operations(self,**kwargs):
        for op_name, op in kwargs.items():
            self.add_operation(op_name,op)

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
        self.ops_enabled[op_name] = True
        self.set_data(op_name,op)

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def set_op_inputs(self,op_name,**kwargs):
        for input_name,val in kwargs.items():
            self.set_op_input(op_name,input_name,val)

    def set_op_input(self,op_name,input_name,val):
        #if not op_name in self.operations:
        #    raise KeyError('operation name {} does not exist'.format(op_name))
        #if not input_name in self.operations[op_name].inputs:
        #    raise KeyError('input name {} does not exist for operation {}'
        #    .format(input_name,op_name))
        itm_key = op_name+'.inputs.'+input_name 
        self.verify_keys([itm_key])
        self.set_data(itm_key,val)

    def set_op_item(self,op_name,item_key,item_data):
        """Subroutine for use with functools.partial for callbacks"""
        full_key = op_name+'.'+item_key
        self.set_data(full_key,item_data)

    def verify_keys(self,keys):
        for k in keys:
            kparts = k.split('.')
            # check only the first three parts of the key:
            # things should be documented to that depth
            if len(kparts) > 3: kparts = kparts[:3]
            k_check = kparts.pop(0)
            for subk in kparts:
                k_check += '.' + subk
            if not k_check in self.keys():
                raise KeyError('Workflow item key {} does not exist'.format(k_check))

    def set_inputs(self,**kwargs):
        for input_name,val in kwargs.items():
            self.inputs[input_name] = val

    #def set_input(self,input_name,val):
    #    """Set a value for Workflow items in self.input_map[`input_name`]"""
    #    r = self.input_map[input_name]
    #    for k in r:
    #        self.set_data(k,val)
    #        # Update the wf_item map so the value is loaded at runtime 
    #        #self.set_wf_item(k,val)

    #def get_output(self,output_name):
    #    out_map = self.outputs[output_name]
    #    if len(out_map) == 1:
    #        return self.get_data(out_map[0])
    #    else:
    #        return [self.get_data(k) for k in out_map]

    #def set_wf_item(self,wf_item_key,val):
    #    self.verify_keys([wf_item_key])
    #    self.op_inputs[wf_item_key] = val

    def run_with(self,**kwargs):
        """Run the Workflow with keyword arguments substituted for the inputs.

        Any keyword arguments that match the Workflow.inputs keys
        are loaded into the Workflow.inputs before calling Workflow.run().
        All relevant results are stored in Workflow.outputs.
        """
        self.inputs.update(kwargs)
        return self.run() 

    def run(self):
        """Run the Workflow."""
        pass
        #self.stop_flag = False
        #stk,diag = self.execution_stack()
        #for itm_key,val in self.op_inputs.items():
        #    self.set_data(itm_key,val)
        #bad_diag_keys = [k for k in diag.keys() if diag[k] and self.is_enabled(k)]
        #for k in bad_diag_keys:
        #    self.message_callback('WARNING- {} is not ready: {}'.format(k,diag[k]))
        #self.message_callback('workflow order:'+os.linesep+print_stack(stk))
        #for lst in stk:
        #    if self.stop_flag:
        #        self.message_callback('Workflow stopped.')
        #        return
        #    for op_name in lst: 
        #        self.message_callback('running: {}'.format(op_name))
        #        op = self.prepare_operation(op_name)
        #        op.stop_flag = False
        #        op.run() 
        #        for outnm,outdata in op.outputs.items():
        #            self.data_callback(op_name+'.outputs.'+outnm,outdata)

    def stop(self):
        """Stop the Workflow and all of its Operations."""
        with self.stop_lock:
            self.stop_flag = True
        #for op_name,op in self.operations.items():
        #    op.stop()
        #stk,diag = self.execution_stack()
        #for lst in stk:
        #    for op_name in lst: 
        #        self.get_data(op_name).stop()

    def build_clone(self):
        """Produce a clone of this Workflow."""
        new_wf = self.clone() 
        new_wf.inputs = copy.deepcopy(self.inputs)
        new_wf.outputs = copy.deepcopy(self.outputs)
        # TODO: consider how to handle callbacks; mind threading 
        new_wf.message_callback = self.message_callback
        new_wf.data_callback = self.data_callback
        return new_wf
        #new_wf.op_inputs = copy.deepcopy(self.op_inputs)
        #new_wf.op_dependencies = copy.deepcopy(self.op_dependencies)
        #new_wf.op_connections = copy.deepcopy(self.op_connections)
        #new_wf.plugin_connections = copy.deepcopy(self.plugin_connections)
        #new_wf.workflow_connections = copy.deepcopy(self.workflow_connections)
        #for op_name,op in self.operations.items():
        #    new_op = op.build_clone()
        #    new_wf.add_operation(op_name,new_op)
        #    #if not self.is_enabled(op_name):
        #    #    new_wf.disable_op(op_name)

    def setup_dict(self):
        """Return a dict that describes the Workflow setup.""" 
        wf_dict = OrderedDict()
        wf_dict['WF_MODULE'] = self._module_path 
        wf_dict['INPUTS'] = copy.deepcopy(self.inputs)
    #    wf_dict['OUTPUTS'] = copy.deepcopy(self.outputs)
        return wf_dict

    @classmethod
    def clone(cls):
        return cls()

    def enable_ops(self,*args):
        for op_name in args:
            self.enable_op(op_name)

    def disable_ops(self,*args):
        for op_name in args:
            self.disable_op(op_name)

    def enable_op(self,op_name):
        self.set_op_enabled(op_name,True)

    def disable_op(self,op_name):
        self.set_op_enabled(op_name,False)

    def set_op_enabled(self,op_name,flag=True):
        self.ops_enabled[op_name] = flag 

    #def is_enabled(self,op_name):
    #    return self.ops_enabled[op_name] 

    #def op_enabled_flags(self):
    #    dct = OrderedDict()
    #    for opnm in self.operations.keys():
    #        dct[opnm] = self.ops_enabled[opnm]
    #    return dct

    #def prepare_operation(self,op_name):
    #    """Prepare according to op_connections, return the Operation"""
    #    for output_key,input_map in self.op_connections.items():
    #        for input_key in input_map:
    #            if input_key.split('.')[0] == op_name:
    #                self.set_data(input_key,self.get_data(output_key))
    #    for itm_key,val in self.op_inputs.items():
    #        if itm_key.split('.')[0] == op_name:
    #            self.set_data(itm_key,val)
    #    return self.get_data(op_name) 
                    
    #def set_dependency(self,op_name,dependency_ops):
    #    """Set `op_name` to depend on one or more other `dependency_ops`"""
    #    if not isinstance(dependency_ops,list):
    #        dependency_ops = [dependency_ops]
    #    if op_name in self.op_dependencies.keys():
    #        self.op_dependencies[op_name].extend(dependency_ops)
    #    else:
    #        self.op_dependencies[op_name] = dependency_ops

    #def get_dependencies(self,op_name):
    #    """Return all Operations that are dependencies of Operation `op_name`"""
    #    deps = []
    #    if op_name in self.op_dependencies:
    #        deps.extend(self.op_dependencies[op_name])
    #    for output_key,input_map in self.op_connections.items():
    #        for input_key in input_map:
    #            if input_key.split('.')[0] == op_name:
    #                new_dep = output_key.split('.')[0]
    #                if not new_dep in deps:
    #                    deps.append(new_dep)
    #    return deps

    #def execution_stack(self):
    #    """Determine order of execution and diagnostics for the Workflow.

    #    Returns
    #    -------
    #    stk : list
    #        List of lists of Operation names,
    #        where each list contains Operations
    #        that can be executed after the Operations in the lists above them.
    #    diag : dict
    #        Gives diagnostic information for any Operations not ready to run. 
    #        Keys are operation names, values are diagnostic info (strings).
    #    """
    #    stk = []
    #    #valid_wf_inputs = [] 
    #    disabled_ops = []
    #    for op_name in self.operations.keys():
    #        if not self.is_enabled(op_name):
    #            disabled_ops.append(op_name) 
    #    diagnostics = {}
    #    continue_flag = True
    #    while not stack_size(stk)+len(disabled_ops) == self.n_operations() and continue_flag:
    #        ops_rdy = []
    #        ops_not_rdy = []
    #        for op_name in self.operations.keys():
    #            op_rdy,op_diag = False,{op_name:''}
    #            if not self.is_enabled(op_name):
    #                op_rdy = False
    #                op_diag = {op_name:'disabled'}
    #            elif not stack_contains(op_name,stk) and not op_name in disabled_ops:
    #                #if op_name in self.op_dependencies.keys():
    #                dep_ops = self.get_dependencies(op_name)
    #                if all([stack_contains(nm,stk) or nm in disabled_ops for nm in dep_ops]):
    #                    # TODO: consider if disabled ops should be dependencies 
    #                    op_rdy,op_diag = True,{op_name:''}
    #                else:
    #                    op_rdy = False
    #                    op_diag = {op_name:'One or more unsatisfied dependencies ({}) '.format(dep_ops)}
    #                #else:
    #                #    op_rdy,op_diag = True,{}
    #            diagnostics.update(op_diag)
    #            if op_rdy:
    #                ops_rdy.append(op_name)
    #        ops_to_run = []
    #        if any(ops_rdy):
    #            for op_name in ops_rdy:
    #                if self.is_enabled(op_name):
    #                    ops_to_run.append(op_name)
    #        if any(ops_to_run):
    #            stk.append(ops_to_run)
    #        else:
    #            continue_flag = False
    #    return stk,diagnostics

    # TODO: consider moving these connection methods to WfManager
    # so that they can be checked against the available plugins/workflows
    #
    #def connect_plugin(self,plugin_item_key,input_map):
    #    if not isinstance(input_map,list): input_map = [input_map]
    #    self.verify_keys(input_map)
    #    if plugin_item_key in self.plugin_connections:
    #        self.plugin_connections[plugin_item_key].extend(input_map)
    #    else:
    #        self.plugin_connections[plugin_item_key] = input_map 
    #
    #def connect_workflow(self,wf_name,input_map):
    #    if not isinstance(input_map,list): input_map = [input_map]
    #    self.verify_keys(input_map)
    #    if wf_name in self.workflow_connections:
    #        self.workflow_connections[wf_name].extend(input_map)
    #    else:
    #        self.workflow_connections[wf_name] = input_map

    #def remove_operation(self,op_name):
    #    """Remove Operation `op_name`."""
    #    self.remove_data(op_name)

    #def n_operations(self):
    #    return len(self.operations) 

    #def connect(self,item_key,input_map):
    #    """Connect `item_key` data to one or more inputs.
    #
    #    Sets up Workflow keys listed in `input_map`
    #    to take the value from `item_key`.
    #    `input_map` can be a key (string) or a list thereof.
    #    """
    #    if not isinstance(input_map,list): input_map = [input_map]
    #    self.verify_keys([item_key])
    #    self.verify_keys(input_map)
    #    if item_key in self.op_connections:
    #        self.op_connections[item_key].extend(input_map)
    #    else:
    #        self.op_connections[item_key] = input_map

    #def connect_input(self,input_name,targets):
    #    if not isinstance(targets,list): targets = [targets]
    #    self.verify_keys(targets)
    #    if not input_name in self.inputs:
    #        self.inputs[input_name] = []
    #    for tgt in targets:
    #        if not tgt in self.inputs[input_name]:
    #            self.inputs[input_name].append(tgt)

    #def connect_output(self,output_name,targets):
    #    if not isinstance(targets,list): targets = [targets]
    #    self.verify_keys(targets)
    #    if not output_name in self.outputs:
    #        self.outputs[output_name] = [] 
    #    for tgt in targets:
    #        if not tgt in self.outputs[output_name]:
    #            self.outputs[output_name].append(tgt)

    #def break_connection(self,io_key):
    #    if io_key in self.op_connections:
    #        self.op_connections.pop(input_key)
    #    else:
    #        for o_key,i_keys in self.op_connections.items():
    #            if io_key in i_keys:
    #                i_keys.pop(i_keys.index(io_key))

    #def break_input(self,input_name):
    #    if input_name in self.input_map:
    #        self.input_map.pop(input_name)
    
    #def break_output(self,output_name):
    #    if output_name in self.output_map:
    #        self.output_map.pop(output_name)

    #def get_outputs(self):
    #    d = OrderedDict()
    #    for out_name in self.outputs.keys():
    #        d[out_name] = self.get_output(out_name)
    #    return d


