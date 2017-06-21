"""
Operations config and processing routines
"""

import glob
import copy
from collections import Iterator
from collections import OrderedDict

# tags for inputs and outputs TreeItems    
inputs_tag = 'inputs'
outputs_tag = 'outputs'

# Declarations of valid sources and types for workflow and plugin inputs
##### TODO: the following but gracefully
no_input = 0
text_input = 1
fs_input = 2
wf_input = 3
plugin_input = 4
batch_input = 5 
valid_sources = [no_input,text_input,fs_input,wf_input,plugin_input,batch_input]
input_sources = ['none','text','filesystem','workflow','plugins','batch'] 

none_type = 0
str_type = 1
int_type = 2
float_type = 3
bool_type = 4
ref_type = 5
path_type = 6
auto_type = 7
valid_types = [none_type,str_type,int_type,float_type,bool_type,ref_type,path_type,auto_type]
input_types = ['none','string','integer','float','boolean','reference','path','auto']

invalid_types = {}                
invalid_types[no_input] = [str_type,int_type,float_type,bool_type,ref_type,path_type,auto_type]
invalid_types[text_input] = [ref_type,path_type,auto_type]
invalid_types[fs_input] = [str_type,int_type,float_type,bool_type,ref_type,auto_type]
invalid_types[wf_input] = [str_type,int_type,float_type,bool_type,auto_type]
invalid_types[plugin_input] = [str_type,int_type,float_type,bool_type,auto_type]
invalid_types[batch_input] = [str_type,int_type,float_type,bool_type,ref_type,path_type]

class InputLocator(object):
    """
    Objects of this class are used as containers for inputs to an Operation,
    and should by design contain the information needed to find the relevant input data.
    After the data is loaded, it should be stored in InputLocator.data.
    """
    def __init__(self,src=no_input,tp=none_type,val=None):
        self.src = src
        self.tp = tp
        self.val = val 
        self.data = None 

class FileSystemIterator(Iterator):

    def __init__(self,dirpath,regex):
        self.paths_done = []
        self.dirpath = dirpath
        self.rx = regex
        super(FileSystemIterator,self).__init__()

    def next(self):
        batch_list = glob.glob(self.dirpath+'/'+self.rx)
        for path in batch_list:
            if not path in self.paths_done:
                self.paths_done.append(path)
                return [path]
        return [None]

class ExecutionError(Exception):
    def __init__(self,msg):
        super(ExecutionError,self).__init__(self,msg)

def parameter_doc(name,value,doc):
    if isinstance(value, InputLocator):
        src_str = input_sources[value.src]
        tp_str = input_types[value.tp]
        v_str = str(value.val)
        return "- name: {} \n- source: {} \n- type: {} \n- value: {} \n- doc: {}".format(name,src_str,tp_str,v_str,doc) 
    else:
        tp_str = type(value).__name__
        return "- name: {} \n- type: {} \n- doc: {}".format(name,tp_str,doc) 

def get_uri_from_dict(uri,d):
    keys = uri.split('.')
    itm = d
    for k in keys:
        if not isinstance(itm,dict):
            msg = 'something in {} is not a dict'.format(uri)
            raise KeyError(msg)
        if not k in itm.keys():
            msg = 'did not find uri {} in dict'.format(uri)
            raise KeyError(msg)
        else:
            itm = itm[k]
    return itm

def dict_contains_uri(uri,d):
    keys = uri.split('.')
    itm = d
    for k in keys:
        if not k in itm.keys():
            return False
        else:
            itm = itm[k]
    return True


####### functions for fetching inputs and loading them into operations #######

def cast_type_val(tp,val):
    """
    Perform type casting for operation inputs.
    This should be called only for source = text_input.
    """
    if tp == none_type:
        val = None 
    elif tp == int_type:
        val = int(val)
    elif tp == float_type:
        val = float(val)
    elif tp == str_type:
        val = str(val)
    elif tp == bool_type:
        val = bool(eval(str(val)))
    else:
        msg = 'type selection {}, should be one of {}'.format(tp,valid_types)
        raise ValueError(msg)
    return val

def locate_input(il,wf=None,plugin_manager=None):
    """
    Return the data pointed to by a given InputLocator object.
    A Workflow and a PluginManager can be provided 
    as optional arguments,
    in which case they are used to fetch data.
    """
    if il.src == no_input or il.tp == none_type:
        return None
    elif il.src == batch_input:
        # Expect this input to have been set by Workflow Manager.
        return il.data 
    elif il.src == text_input: 
        if isinstance(il.val,list):
            return [cast_type_val(il.tp,v) for v in il.val]
        else:
            return cast_type_val(il.tp,il.val)
    elif il.src == wf_input:
        if il.tp == ref_type:

            # Note, this will return whatever data is stored in the TreeItem at uri.
            # If il.val is the uri of an input that has not yet been loaded,
            # this means it will get the InputLocator that currently inhabits that uri.

            # Note, this problem has now been fixed by changing Workflow.build_dict()
            # to not substitute InputLocators for inputs that had not been loaded.

            if isinstance(il.val,list):
                return [wf.get_data_from_uri(v) for v in il.val]
            else:
                return wf.get_data_from_uri(il.val)
        elif il.tp == path_type: 
            if isinstance(il.val,list):
                return [str(v) for v in il.val]
            else:
                return str(il.val)
    elif il.src == plugin_input:
        if il.tp == ref_type:
            if isinstance(il.val,list):
                return [plugin_manager.get_data_from_uri(v) for v in il.val]
            elif il.val is not None:
                return plugin_manager.get_data_from_uri(il.val)
            else:
                return None
        elif il.tp == path_type:
            if isinstance(il.val,list):
                return [str(v) for v in il.val]
            else:
                return str(il.val)
    elif il.src == fs_input:
        if isinstance(il.val,list):
            return [str(v) for v in il.val]
        else:
            return str(il.val)
    else: 
        msg = 'found input source {}, should be one of {}'.format(
        il.src, valid_sources)
        raise ValueError(msg)

def load_inputs(op,wf=None,plugin_manager=None):
    """
    Loads input data for an Operation from its input_locators.
    A Workflow and a PluginManager can be provided 
    as optional arguments,
    in which case they are used to fetch data.
    """
    for name,il in op.input_locator.items():
        if isinstance(il,InputLocator):
            il.data = locate_input(il,wf,plugin_manager)
            op.inputs[name] = il.data
        else:
            msg = '[{}] Found broken Operation.input_locator for {}: {}'.format(
            __name__, name, il)
            raise ValueError(msg)

####### functions having to do with workflow execution #######
# TODO: consider creating a wftools module instead

def get_valid_wf_inputs(op_tag,op):
    """
    Return the TreeModel uris of the op and its inputs/outputs 
    that are eligible as downstream inputs in the workflow.
    """
    # valid_wf_inputs should be the operation, its input and output dicts, and their respective entries
    valid_wf_inputs = [op_tag,op_tag+'.'+inputs_tag,op_tag+'.'+outputs_tag]
    valid_wf_inputs += [op_tag+'.'+outputs_tag+'.'+k for k in op.outputs.keys()]
    valid_wf_inputs += [op_tag+'.'+inputs_tag+'.'+k for k in op.inputs.keys()]
    return valid_wf_inputs
    
def stack_size(stk):
    sz = 0
    for lst in stk:
        for lst_itm in lst:
            if isinstance(lst_itm,list):
                sz += stack_size(lst_itm)
            else:
                sz += 1
    return sz

def stack_contains(itm,stk):
    for lst in stk:
        if itm in lst:
            return True
        for lst_itm in lst:
            if isinstance(lst_itm,list):
                if stack_contains(itm,lst_itm):
                    return True
    return False

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

def is_op_ready(wf,op_tag,valid_wf_inputs,batch_routes=[]):
    op = wf.get_data_from_uri(op_tag)
    if op._batch_flag: 
        b_stk,op_rdy,diagnostics = batch_op_stack(wf,op_tag,valid_wf_inputs)
    elif op._realtime_flag: 
        rt_stk,op_rdy,diagnostics = batch_op_stack(wf,op_tag,valid_wf_inputs)
    else:
        inputs_rdy = []
        diagnostics = {} 
        for name,il in op.input_locator.items():
            msg = ''
            if (il.src == wf_input and il.tp == ref_type 
            and not il.val in valid_wf_inputs):
                inp_rdy = False
                msg = str('Operation input {}.inputs.{} (={}) '.format(op_tag,name,il.val)
                + 'not found in valid Workflow input list: {}'.format(valid_wf_inputs))
            elif (il.src == batch_input 
            and not op_tag+'.'+inputs_tag+'.'+name in batch_routes):
                inp_rdy = False
                msg = str('Operation input {}.inputs.{} (={}) '.format(op_tag,name,il.val)
                + 'expects batch input but is not listed in batch routes: {}'.format(batch_routes))
            else:
                inp_rdy = True
            inputs_rdy.append(inp_rdy)
            diagnostics[op_tag+'.'+inputs_tag+'.'+name] = msg
        if all(inputs_rdy):
            op_rdy = True
        else:
            op_rdy = False
    return op_rdy,diagnostics 

def batch_op_stack(wf,batch_op_tag,valid_wf_inputs):
    """
    Use batch_op.batch_ops() and a list of valid_wf_inputs 
    to build a stack (list) of lists of operations suitable for serial execution.
    """
    batch_op = wf.get_data_from_uri(batch_op_tag)
    # Batch and Realtime execution operations 
    # expect to have two inputs loaded by internal methods 
    # before calling batch_op.batch_ops() and batch_op.input_routes()
    batch_op.set_batch_ops(wf)
    batch_op.set_input_routes(wf)
    op_tags = batch_op.batch_ops()
    #load_inputs(batch_op,wf,plugin_manager)
    #op_tags = []
    #if batch_op._realtime_flag: 
    #    op_tags = batch_op.realtime_ops()
    #elif batch_op._batch_flag: 
    #    op_tags = batch_op.batch_ops()
    # make a copy of valid_wf_inputs
    # so that the existing valid_wf_inputs list is not mutated 
    valid_batch_inputs = copy.copy(valid_wf_inputs)
    # add the batch's own valid inputs to the list
    valid_batch_inputs += get_valid_wf_inputs(batch_op_tag,batch_op)
    # build the batch substack
    b_stk = []
    layer = []
    diagnostics = {}
    for op_tag in op_tags:
        op_rdy,op_diag = is_op_ready(wf,op_tag,valid_batch_inputs,batch_op.input_routes())
        diagnostics.update(op_diag)
        if op_rdy:
            layer.append(op_tag)
    while any(layer):
        b_stk.append(layer)
        for op_tag in layer:
            op = wf.get_data_from_uri(op_tag)
            valid_batch_inputs += get_valid_wf_inputs(op_tag,op)
        layer = []
        for op_tag in op_tags:
            op_rdy,op_diag = is_op_ready(wf,op_tag,valid_batch_inputs,batch_op.input_routes())
            diagnostics.update(op_diag)
            if op_rdy and not stack_contains(op_tag,b_stk):
                layer.append(op_tag)
    b_rdy = len(op_tags) == stack_size(b_stk) 
    return b_stk,b_rdy,diagnostics 

# TODO: the following
def check_wf(wf):
    """
    Check the dependencies of the workflow.
    Ensure that all loaded operations have inputs that make sense.
    Return a status code and message for each of the Operations.
    """
    pass

def execution_stack(wf):
    """
    Build a stack (list) of lists of Operation uris,
    such that each list indicates a set of Operations
    whose dependencies are satisfied by the Operations above them.
    For Batch or Realtime operations, 
    the layer should be of the form[batch_name,[batch_stack]],
    where batch_name indicates the batch controller Operation,
    and batch_stack is built from batch_op_stack().
    """
    stk = []
    valid_wf_inputs = []
    diagnostics = {}
    continue_flag = True
    while not stack_size(stk) == wf.n_ops() and continue_flag:
        ops_rdy = []
        ops_not_rdy = []
        for itm in wf._root_item.children:
            if not stack_contains(itm.tag,stk):
                op_rdy,op_diag = is_op_ready(wf,itm.tag,valid_wf_inputs)
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
                op = wf.get_data_from_uri(op_tag)
                if not any([op._batch_flag,op._realtime_flag]):
                    non_batch_rdy.append(op_tag)
            if any(non_batch_rdy):
                ops_rdy = non_batch_rdy
                stk.append(ops_rdy)
                for op_tag in ops_rdy:
                    op = wf.get_data_from_uri(op_tag)
                    valid_wf_inputs += get_valid_wf_inputs(op_tag,op)
            else:
                batch_tag = ops_rdy[0]
                ops_rdy = [batch_tag]
                batch_op = wf.get_data_from_uri(batch_tag)
                batch_stk,batch_rdy,batch_diag = batch_op_stack(
                wf,batch_tag,valid_wf_inputs)
                diagnostics.update(batch_diag)
                stk.append([batch_tag,batch_stk])
                valid_wf_inputs += get_valid_wf_inputs(batch_tag,batch_op)
        else:
            continue_flag = False
    return stk,diagnostics


