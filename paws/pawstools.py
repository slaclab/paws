from datetime import datetime as dt
import importlib
import os
import re
import string 
from collections import OrderedDict

import yaml

from . import operations
from . import workflows
        
bad_chars = string.punctuation 
bad_chars = bad_chars.replace('_','')
bad_chars = bad_chars.replace('-','')
bad_chars = bad_chars.replace('.','')
space_chars = [' ','\t','\n',os.linesep]

p = os.path.abspath(__file__)
# p = (pawsroot)/paws/pawstools.py

d = os.path.dirname(p)
# d = (pawsroot)/paws/
sourcedir = str(d)

d = os.path.dirname(d)
# d = (pawsroot)/
rootdir = str(d)

# Get the code version from the config.py file.
# Reference version string as pawstools.__version__
with open(os.path.join(sourcedir,'config.py')) as f: 
    exec(f.read())

# TODO: ensure this is valid cross-platform
user_homedir = os.path.expanduser("~")

paws_scratch_dir = os.path.join(user_homedir,'.paws_scratch')
paws_cfg_dir = os.path.join(user_homedir,'.paws_cfg')
if not os.path.exists(paws_cfg_dir):
    os.mkdir(paws_cfg_dir)
if not os.path.exists(paws_scratch_dir):
    os.mkdir(paws_scratch_dir)

def primitives(v):
    if isinstance(v,dict):
        rd = {}
        for kk,vv in v.items():
            rd[kk] = primitives(vv)
        return rd
    elif isinstance(v,list):
        return [primitives(vv) for vv in v]
    elif isinstance(v,str):
        return str(v)
    elif isinstance(v,int):
        return int(v)
    elif isinstance(v,float):
        return float(v)
    else:
        return v

class WorkflowAborted(Exception):
    pass

class OperationDisabledError(Exception):
    pass

class WfNameError(Exception):
    pass

class PluginNameError(Exception):
    pass

class PluginLoadError(Exception):
    pass

class OperationLoadError(Exception):
    pass

def dtstr():
    """Return date and time as a string"""
    return dt.strftime(dt.now(),'%Y %m %d, %H:%M:%S')

def timestr():
    """Return time as a string"""
    return dt.strftime(dt.now(),'%H:%M:%S')

def save_file(filename,d):
    """
    Create or replace file indicated by filename,
    as a yaml serialization of dict d.
    """
    f = open(filename, 'w')
    yaml.dump(d, f)
    f.close()
    
def update_file(filename,d):
    """
    Save the items in dict d into filename,
    without removing members not included in d.
    """
    if os.path.exists(filename):
        f_old = open(filename,'r')
        d_old = yaml.load(f_old)
        f_old.close()
        d_old.update(d)
        d = d_old
    f = open(filename, 'w')
    yaml.dump(d, f)
    f.close()

class DictTree(object):
    """A data structure for tree-like storage.

    A DictTree has a root (an ordered dictionary), 
    which is extended by embedding other objects 
    that are amenable to tree storage.
    Fetches items by keys (strings),
    which are sequences 
    of parent item keys(), connected by '.'s.

    Child items (end nodes of the tree)
    can be anything.
    Parent items, in order to index their children,
    must be either lists, dicts, or objects implementing
    keys(), __getitem__(key) and __setitem__(key,value).

    This data structure was originally developed
    to interface with a TreeView in a Qt GUI.
    It is no longer used in PAWS;
    it is here because it's kind of neat.
    """

    def __init__(self,data={}):
        super(DictTree,self).__init__()
        self._root = OrderedDict()
        if isinstance(data,dict):
            self._root = OrderedDict(data)

    def __getitem__(self,key):
        return self.get_data(key)

    def __setitem__(self,key,val):
        self.set_data(key,val)

    def root_keys(self):
        return self._root.keys()

    def keys(self):
        return self.subkeys()

    def subkeys(self,root_key=''):
        if not root_key:
            itm = self._root
        else:
            itm = self.get_data(root_key)
        itm_keys = []
        try:
            itm_keys = itm.keys()
        except:
            if isinstance(itm,list): 
                itm_keys = [str(i) for i in range(len(itm))] 
            else:
                # no itm_keys
                pass
        prefix = root_key
        if root_key: prefix += '.'
        sk = [prefix+s for s in itm_keys]
        for k in itm_keys:
            next_keys = self.subkeys(prefix+k) 
            if any(next_keys):
                sk.extend(next_keys)
        return sk

    @ staticmethod
    def parent_key(key):
        # TODO: handle the possibility of subkeys containing periods
        if '.' in key:
            return key[:key.rfind('.')]
        else:
            return ''

    def delete_data(self,key=''):
        """Attempts to de-reference the given key"""
        parent_itm = self._root
        if '.' in key:
            parent_itm = self.get_data(self.parent_key(key))
        itm_key = key.split('.')[-1]
        if itm_key:
            try: 
                # parent implements __getitem__()?
                parent_itm.pop(itm_key)
            except:
                # parent item is list? 
                parent_itm.pop(int(itm_key))

    def set_data(self,key='',val=None):
        """Sets the data at the given key."""
        parent_itm = self._root
        if '.' in key:
            parent_itm = self.get_data(self.parent_key(key))
        itm_key = key.split('.')[-1]
        if itm_key:
            try: 
                parent_itm[itm_key] = val
            except:
                try: 
                    parent_itm[int(itm_key)] = val # list case
                except:
                    parent_itm.append(val) # append to list case

    def get_data(self,key=''):
        """Returns the data at the given key."""
        path = key.split('.')
        itm = self._root 
        for ik,k in enumerate(path):
            child_found = False
            try: 
                itm = itm[k]
                child_found = True
            except:
                try: 
                    itm = itm[int(k)]
                    child_found = True
                except:
                    longer_key = k
                    for kk in path[ik+1:]:
                        longer_key += '.'
                        try: 
                            itm = itm[longer_key]
                            child_found = True
                        except: 
                            pass
                        longer_key += kk
                        try: 
                            itm = itm[longer_key]
                            child_found = True
                        except: 
                            pass
            if not child_found:
                raise KeyError(key)
        return itm

    def is_key_valid(self,key):
        """Check key validity.

        Keys may contain upper case letters, lower case letters, 
        numbers, dashes (-), and underscores (_) and period (.) marks. 
        Any whitespace or any character in the string.punctuation library
        (other than -, _, or .) results in an invalid key.
        """
        if not key or any(map(lambda s: s in key,space_chars))\
            or any(map(lambda s: s in key,bad_chars)):
            return False 
        return True 

    def key_error_message(self,key):
        """Provide a human-readable error message for bad keys."""
        if not key:
            return 'key is blank.'
        elif any(map(lambda s: s in key,space_chars)):
            return '"{}" contains whitespace.'.format(key)
        elif any(map(lambda s: s in key,bad_chars)):
            return '"{}" contains special characters.'.format(key)

    def print_tree(self,root_key='',offset=''):
        """Print the tree content."""
        itm = self._root
        if root_key:
            itm = self.get_data(root_key)
        tstr = os.linesep 
        try:    #if isinstance(itm,dict):
            for k in itm.keys():
                x_str = self.print_tree(root_key+'.'+k,offset+'    ')
                tstr = tstr+offset+'{}: {}'.format(k,x_str)+os.linesep
        except:
            try:    #elif isinstance(itm,list):
                for i,x in enumerate(itm):
                    x_str = self.print_tree(root_key+'.'+str(i),offset+'    ')
                    tstr = tstr+offset+'{}: {}'.format(i,x_str)+os.linesep
            except:
                return '{}'.format(itm)
        return tstr


