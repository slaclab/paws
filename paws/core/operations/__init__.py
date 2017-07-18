from __future__ import print_function
import os
import pkgutil
import importlib
from collections import OrderedDict

import yaml

from .. import pawstools

# check for an ops.cfg (yaml) file
cfg_file = os.path.join(pawstools.paws_cfg_dir,'ops.cfg')
if os.path.exists(cfg_file):
    load_flags = pawstools.load_cfg(cfg_file)
else:
    load_flags = OrderedDict() 
    
def save_config():
    """
    Call save_config() before closing 
    to save the state of which ops are enabled/disabled.
    """
    # Order the load flags using load_keys...
    od_load_flags = OrderedDict()
    for k in load_keys:
        od_load_flags[k] = load_flags[k]
    pawstools.save_cfg(od_load_flags,cfg_file)

# Keep track of keys that get loaded in this run.
# These keys are used to remove load_flags automatically
# in case Operations or categories have been renamed or removed.
load_keys = []

def update_load_flags():
    for k in load_flags.keys():
        if not k in load_keys:
            load_flags.pop(k)

def load_ops_from_path(path_,pkg,cat_root=''):
    ops = []
    cats = []
    # pkgutil.iter_modules returns module_loader, module_name, ispkg forall modules in path
    mods = pkgutil.iter_modules(path_)
    mods = [mod for mod in mods if mod[1] not in ['__init__','Operation','OpManager','optools','DMZ']]
    for modloader, modname, ispkg in mods:
        if cat_root == '':
            mod_root = modname 
        else:
            mod_root = cat_root+'.'+modname
        load_keys.append(mod_root)
        if mod_root in load_flags.keys():
            load_mod = bool(load_flags[mod_root])
        else:
            # NOTE: This line determines whether or not 
            # newly arrived modules should be loaded by default.
            load_mod = False
        #
        #load_mod = True
        #
        load_flags[mod_root] = load_mod
        # if it is a package, recurse
        if ispkg:
            pkg_path = [os.path.join(path_[0],modname)]
            pkg_ops, pkg_cats = load_ops_from_path(pkg_path,pkg+'.'+modname,mod_root)
            pkg_ops = [op for op in pkg_ops if not op in ops]
            pkg_cats = [cat for cat in pkg_cats if not cat in cats]
            ops = ops + pkg_ops
            cats = cats + pkg_cats
        else:
            # assume that there is an Operation in this module
            # whose class name is the same as the module name.
            ops.append( (cat_root,modname) )
            if not cat_root in cats:
                cats.append(cat_root)
    return ops, cats
        #if load_mod:
        #    # Assume Operation name is same as module name.
        #    # Get the operation from the module.
        #    # TODO: Handle any ImportErrors or AttributeErrors.
        #    mod = importlib.import_module('.'+modname,pkg)
        #    op = getattr(mod,modname)
            #try:
            #    ops.append( (cat_root,op) )
            #    if not cat_root in cats:
            #        cats.append(cat_root)
            #except AttributeError as ex:
            #    pass
            #    msg = str('Failed to load Operation subclass {} '.format(modname)
            #    + 'from module of the same name. Error message: '+ ex.message
            #    + '\nTo load an Operation, '
            #    + 'ensure the Operation subclass '
            #    + 'has the same name as its .py module file')
            #    print(msg)

def disable_ops(disable_root):
    # get all keys that contain disable_root
    disable_keys = [k for k in load_flags.keys() if disable_root in k]
    for k in disable_keys:
        load_flags[k] = False 

#print(load_flags)

cat_op_list, cat_list = load_ops_from_path(__path__,__name__)

update_load_flags()

#op = load_op_from_module(mod,cat_root)
#mod_ops, mod_cats = load_ops_from_module(mod,cat_root)
#mod_ops = [op for op in mod_ops if not op in ops]
#mod_cats = [cat for cat in mod_cats if not cat in cats]
#ops = ops + mod_ops
#cats = cats + mod_cats

#def load_op_from_module(mod,cat_root):
    # Get the operation from the module:
    # assume Operation name is same as module name
    #op = getattr(mod,mod)
    #ops = []
    #cats = []
    #for nm, itm in mod.__dict__.items():
    #    try:
    #        # is it a class?
    #        if isinstance(itm,type):
    #            # is it a non-abstract subclass of Operation?
    #            if issubclass(itm,Operation) and not nm in ['Operation','Realtime','Batch']:
    #                op = getattr(mod,nm)
    #                ops.append( (cat_root,op) )
    #                if not cat_root in cats:
    #                    cats.append(cat_root)
    #                    #load_flags[cat_root] = True
    #                    #load_keys.append(cat_root)
    #                #cat = cat_root
    #                parent_cats_done = False
    #                while not parent_cats_done:
    #                    if not cat.rfind('.') == -1:
    #                        parcat = cat[:cat.rfind('.')]
    #                        if not parcat in cats:
    #                            cats.append(parcat)
    #                            load_keys.append(parcat)
    #                        cat = parcat
    #                    else:
    #                        parent_cats_done = True
    #                load_flags[nm] = True
    #                load_keys.append(nm)
    #    except ImportError as ex:
    #        print '[{}] had trouble dealing with {}: {}'.format(__name__,name,item)
    #        print 'Error text: {}'.format(ex.message)
    #        pass 
    #return ops, cats



