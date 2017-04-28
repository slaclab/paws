import os
from datetime import datetime as dt

import yaml

# TODO: Make scratch directory and other cfg'ables into a cfg file

p = os.path.abspath(__file__)
# p = (pawsroot)/paws/core/pawstools.py
d = os.path.dirname(p)
# d = (pawsroot)/paws/core/
d = os.path.dirname(d)
# d = (pawsroot)/paws/
sourcedir = str(d)
d = os.path.dirname(d)
# d = (pawsroot)
rootdir = str(d)
scratchdir = os.path.join(rootdir,'scratch')
if not os.path.exists(scratchdir):
    os.mkdir(scratchdir)

# Get the code version from the paws_config.py file, store as __version__
with open(os.path.join(rootdir,'paws_config.py')) as f: 
    exec(f.read())
version=__version__

class LazyCodeError(Exception):
    def __init__(self,msg):
        super(LazyCodeError,self).__init__(self,msg)

class WorkflowAborted(Exception):
    def __init__(self,msg):
        super(WorkflowAborted,self).__init__(self,msg)

def dtstr():
    """Return date and time as a string"""
    return dt.strftime(dt.now(),'%Y %m %d, %H:%M:%S')

def timestr():
    """Return time as a string"""
    return dt.strftime(dt.now(),'%H:%M:%S')

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

def save_cfg(cfg_data,cfg_file):
    cfg = open(cfg_file,'w')
    yaml.dump(cfg_data,cfg)
    cfg.close()

def load_cfg(cfg_file):
    cfg = open(cfg_file,'r')
    cfg_data = yaml.load(cfg)
    cfg.close()
    if not cfg_data:
        cfg_data = OrderedDict() 
    return cfg_data

