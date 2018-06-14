from collections import OrderedDict
from datetime import datetime as dt
import importlib
import os
import re

import yaml

from . import operations
from . import workflows
wf_module = workflows.__name__

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

