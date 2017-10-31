from __future__ import print_function
import os
import pkgutil
import importlib
from collections import OrderedDict

import yaml

from .. import pawstools

op_keys = []
def load_ops_from_path(path_,pkg,cat_root=''):
    ops = []
    cats = []
    # pkgutil.iter_modules returns module_loader, module_name, ispkg forall modules in path
    mods = pkgutil.iter_modules(path_)
    mods = [mod for mod in mods if mod[1] not in ['__init__','Operation','OpManager','optools','DMZ']]
    for modloader, modname, ispkg in mods:
        if ispkg:
            pkg_path = [os.path.join(path_[0],modname)]
            subcat_root = modname
            if cat_root:
                subcat_root = cat_root+'.'+modname
            pkg_ops, pkg_cats = load_ops_from_path(pkg_path,pkg+'.'+modname,subcat_root)
            pkg_ops = [op for op in pkg_ops if not op in ops]
            pkg_cats = [cat for cat in pkg_cats if not cat in cats]
            ops = ops + pkg_ops
            cats = cats + pkg_cats
        else:
            # assume that there is an Operation in this module
            # whose class name is the same as the module name.
            if not cat_root in cats:
                cats.append(cat_root)
            ops.append( (cat_root,modname) )
            op_keys.append(cat_root+'.'+modname)
    return ops, cats

cat_op_list, cat_list = load_ops_from_path(__path__,__name__)

# check for an ops.cfg (yaml) file
#cfg_file = os.path.join(pawstools.paws_cfg_dir,'ops.cfg')
#if os.path.exists(cfg_file):
#    load_flags = pawstools.load_cfg(cfg_file)

# Keep track of keys that get loaded in this run.
# These keys are used to remove load_flags automatically
# in case Operations or categories have been renamed or removed.
    
#def save_config():
#    """
#    Call save_config() before closing 
#    to save the state of which ops are enabled/disabled.
#    """
#    # Order the load flags using op_keys...
#    od_load_flags = OrderedDict()
#    for k in op_keys:
#        od_load_flags[k] = load_flags[k]
#    pawstools.save_cfg(od_load_flags,cfg_file)

#def disable_ops(disable_root):
#    # get all keys that contain disable_root
#    disable_keys = [k for k in load_flags.keys() if disable_root in k]
#    for k in disable_keys:
#        load_flags[k] = False 

#load_flags = OrderedDict() 
#load_flags = {k:load_flags[k] for k in load_flags.keys() if k in op_keys}


