from collections import OrderedDict

from PySide import QtCore

import slacxop

##### TODO: the following but gracefully 
# definitions for operation input sources 
no_input = 0
user_input = 1
fs_input = 2
wf_input = 3
plugin_input = 4
batch_input = 5 
valid_sources = [no_input,user_input,fs_input,wf_input,plugin_input,batch_input]
input_sources = ['None','User Input','Filesystem','Workflow','Plugins','Batch'] 

# supported types for operation inputs
none_type = 0
auto_type = 1
str_type = 2
int_type = 3
float_type = 4
bool_type = 5
list_type = 6
valid_types = [none_type,auto_type,str_type,int_type,float_type,bool_type,list_type]
input_types = ['none','auto','string','integer','float','boolean','list']

# unsupported types for each source, keyed by source
invalid_types = {}                
invalid_types[no_input] = [auto_type,str_type,int_type,float_type,bool_type,list_type]
invalid_types[user_input] = [auto_type]
invalid_types[fs_input] = [str_type,int_type,float_type,bool_type]
invalid_types[wf_input] = [str_type,int_type,float_type,bool_type]
invalid_types[plugin_input] = [str_type,int_type,float_type,bool_type]
invalid_types[batch_input] = [str_type,int_type,float_type,bool_type,list_type]

# tags and indices for inputs and outputs trees
inputs_tag = 'inputs'
outputs_tag = 'outputs'
inputs_idx = 0
outputs_idx = 1

def cast_type_val(tp,val):
    """
    Perform type casting for operation inputs.
    Note that this should not be called for inputs of auto_type.
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
        val = bool(val)
    elif tp == list_type:
        # val will be a list of things, already typecast by the list builder 
        val = list(val)
    else:
        msg = 'type selection {}, should be one of {}'.format(tp,valid_types)
        raise ValueError(msg)
    return val

def val_list(il):
    if il.tp == list_type:
        return il.val
    else:
        return [il.val]

def parse_plugin_input(plugman,il,op):
    itm, indx = plugman.get_from_uri(il.val)
    return itm.data

def parse_wf_input(wfman,il,op):
    uris = val_list(il)
    rets = []
    for uri in uris:
        uri_parts = uri.split('.')
        if len(uri_parts) >= 3:
            io_type = uri_parts[1]
            if io_type == inputs_tag:
                #print 'seeking input {}'.format(uri)
                inprouteflag = False
                if isinstance(op,slacxop.Batch) or isinstance(op,slacxop.Realtime):
                    inprouteflag = uri in op.input_routes()
                if inprouteflag:
                    # a uri used to direct a batch executor in setting data.
                    # It should be returned directly- the batch will use it as is.
                    rets.append(uri)
                else:
                    # an input uri... trusting that this input has already been loaded,
                    # grab the data from the InputLocator at that uri and return it.
                    # TODO: make sure this is coherent with wfman.upstream_stack() 
                    itm, idx = wfman.get_from_uri(uri)
                    il = itm.data 
                    rets.append(il.data)
            else:
                # an output is requested. fetch and return data.
                itm, idx = wfman.get_from_uri(uri)
                rets.append(itm.data)
        else:
            # an entire Operation or its inputs or outputs dict is requested. fetch and return data.
            itm, indx = wfman.get_from_uri(uri)
            rets.append(itm.data)
    if il.tp == list_type:
        return rets
    else:
        return rets[0]

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

#def loader_extensions():
#    return str(
#    "ALL (*.*);;"
#    + "TIFF (*.tif *.tiff);;"
#    + "RAW (*.raw);;"
#    + "MAR (*.mar*)"
#    )

