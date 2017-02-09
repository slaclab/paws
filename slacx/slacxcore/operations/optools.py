from collections import OrderedDict

from PySide import QtCore

import slacxop

##### TODO: the following but gracefully
# definitions for operation input sources
no_input = 0
text_input = 1
fs_input = 2
wf_input = 3
plugin_input = 4
batch_input = 5 
valid_sources = [no_input,text_input,fs_input,wf_input,plugin_input,batch_input]
input_sources = ['None','Text Input','Filesystem','Workflow','Plugins','Batch'] 

# supported types for user input
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

# unsupported types for each source, keyed by source
invalid_types = {}                
invalid_types[no_input] = [str_type,int_type,float_type,bool_type,ref_type,path_type,auto_type]
invalid_types[text_input] = [ref_type,path_type,auto_type]
invalid_types[fs_input] = [str_type,int_type,float_type,bool_type,ref_type,auto_type]
invalid_types[wf_input] = [str_type,int_type,float_type,bool_type,auto_type]
invalid_types[plugin_input] = [str_type,int_type,float_type,bool_type,auto_type]
invalid_types[batch_input] = [str_type,int_type,float_type,bool_type,ref_type,path_type]

# tags for inputs and outputs TreeItems    
inputs_tag = 'inputs'
outputs_tag = 'outputs'

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

def get_uri_from_dict(uri,d):
    keys = uri.split('.')
    itm = d
    for k in keys:
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

def op_dict(op):
    dct = OrderedDict() 
    dct['type'] = type(op).__name__ 
    dct[inputs_tag] = op_inputs_dict(op)
    return dct

def op_inputs_dict(op):
    dct = OrderedDict() 
    for name in op.inputs.keys():
        il = op.input_locator[name]
        dct[name] = {'src':il.src,'type':il.tp,'val':il.val}
    return dct

def plugin_dict(pgin):
    dct = OrderedDict()
    dct['type'] = type(pgin).__name__
    dct[inputs_tag] = pgin.inputs 
    return dct

#def outputs_dict(self,op):
#    #dct = {}
#    dct = OrderedDict() 
#    for name in op.outputs.keys():
#        dct[name] = str(op.outputs[name])
#    return dct

class InputLocator(object):
    """
    Objects of this class are used as containers for inputs to an Operation,
    and should by design contain the information needed to find the relevant input data.
    After the data is loaded, it should be stored in InputLocator.data.
    """
    def __init__(self,src=no_input,tp=none_type,val=None):
        #if src not in valid_sources: 
        #    msg = 'found input source {}, should be one of {}'.format(src, valid_sources)
        self.src = src
        self.tp = tp
        self.val = val 
        self.data = None 

def parameter_doc(name,value,doc):
    #if type(value).__name__ == 'InputLocator':
    if isinstance(value, InputLocator):
        src_str = input_sources[value.src]
        tp_str = input_types[value.tp]
        d = value.data
        return "- name: {} \n- source: {} \n- type: {} \n- value: {} \n- doc: {}".format(name,src_str,tp_str,d,doc) 
    else:
        val_str = str(value)
        tp_str = type(value).__name__
        return "- name: {} \n- type: {} \n- value: {} \n- doc: {}".format(name,tp_str,val_str,doc) 

def stack_size(stk):
    sz = 0
    for lst in stk:
        if isinstance(lst[0].data,slacxop.Batch) or isinstance(lst[0].data,slacxop.Realtime):
            sz += stack_size(lst[1])+1
        else:
            sz += len(lst)
    return sz

def stack_contains(itm,stk):
    for lst in stk:
        if isinstance(lst[0].data,slacxop.Batch) or isinstance(lst[0].data,slacxop.Realtime):
            if itm == lst[0] or stack_contains(itm,lst[1]):
                return True
        else:
            if itm in lst:
                return True
    return False

def print_stack(stk):
    stktxt = ''
    for lst in stk:
        if isinstance(lst[0].data,slacxop.Batch) or isinstance(lst[0].data,slacxop.Realtime):
            substk = lst[1]
            stktxt += '[{}:\n{}]\n'.format(lst[0].tag(),print_stack(lst[1]))
            #[[itm.tag() for itm in sublst] for sublst in substk])
        else:
            stktxt += '{}\n'.format([itm.tag() for itm in lst])
    return stktxt

#def loader_extensions():
#    return str(
#    "ALL (*.*);;"
#    + "TIFF (*.tif *.tiff);;"
#    + "RAW (*.raw);;"
#    + "MAR (*.mar*)"
#    )

