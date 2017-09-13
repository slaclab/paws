"""
Various tools for working with Workflows and Operations
"""

import glob
import copy
from collections import Iterator
from collections import OrderedDict

from . import Operation as opmod 

class FileSystemIterator(Iterator):

    def __init__(self,dirpath,regex,include_existing_files=True):
        self.dirpath = dirpath
        self.rx = regex
        self.paths_done = []
        if not include_existing_files:
            self.paths_done = glob.glob(self.dirpath+'/'+self.rx)
        super(FileSystemIterator,self).__init__()

    def next(self):
        batch_list = glob.glob(self.dirpath+'/'+self.rx)
        for path in batch_list:
            if not path in self.paths_done:
                self.paths_done.append(path)
                return path
        return None

class ExecutionError(Exception):
    def __init__(self,msg):
        super(ExecutionError,self).__init__(self,msg)

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

def locate_input(il,wf=None,wf_manager=None,plugin_manager=None):
    """
    Return the data pointed to by a given InputLocator object.
    A WfManager and/or a PluginManager can be provided 
    as optional arguments,
    in which case they are used to fetch data.
    """
    if il.tp == opmod.no_input or il.val is None:
        return None
    elif il.tp == opmod.workflow_item:
        if isinstance(il.val,list):
            return [wf.get_data_from_uri(v) for v in il.val]
        else:
            return wf.get_data_from_uri(il.val)
    elif il.tp == opmod.entire_workflow:
        return wf_manager.workflows[il.val]
    elif il.tp == opmod.plugin_item:
        if isinstance(il.val,list):
            return [plugin_manager.get_data_from_uri(v) for v in il.val]
        else:
            return plugin_manager.get_data_from_uri(il.val)
    elif il.tp == opmod.auto_type:
        return il.val
    else:
        msg = '[{}] failed to parse InputLocator (type: {}, val: {})'.format(
        __name__,il.tp,il.val)
        raise ValueError(msg)
    #elif il.tp == opmod.integer_type:
    #    if isinstance(il.val,list):
    #        return [int(v) for v in il.val]
    #    else:
    #        return int(il.val)
    #elif il.tp == opmod.float_type:
    #    if isinstance(il.val,list):
    #        return [float(v) for v in il.val]
    #    else:
    #        return float(il.val)
    #elif il.tp == opmod.bool_type:
    #    if isinstance(il.val,list):
    #        return [bool(eval(str(v))) for v in il.val]
    #    else:
    #        return bool(eval(str(il.val)))
    #elif (il.tp == opmod.filesystem_path
    #    or il.tp == opmod.workflow_path
    #    or il.tp == opmod.string_type):
    #    if isinstance(il.val,list):
    #        return [str(v) for v in il.val]
    #    else:
    #        return str(il.val)

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

# TODO: the following
def check_wf(wf):
    """
    Check the dependencies of the workflow.
    Ensure that all loaded operations have inputs that make sense.
    Return a status code and message for each of the Operations.
    """
    pass

