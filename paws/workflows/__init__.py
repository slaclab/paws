from __future__ import print_function
import os
import pkgutil
import importlib

def load_workflows(path_,pkg,cat_root=''):
    cat_list = []
    cat_wf_list = []
    wf_modules = {} 
    mods = pkgutil.iter_modules(path_)
    mods = [mod for mod in mods if mod[1] not in ['__init__','Workflow','WfManager','wftools']]
    for modloader, modname, ispkg in mods:
        if ispkg:
            pkg_path = [os.path.join(path_[0],modname)]
            subcat_root = modname
            if cat_root:
                subcat_root = cat_root+'.'+modname
            pkg_cats, pkg_wfs, pkg_wf_modules = load_workflows(pkg_path,pkg+'.'+modname,subcat_root)
            pkg_wfs = [wf for wf in pkg_wfs if not wf in cat_wf_list]
            pkg_cats = [cat for cat in pkg_cats if not cat in cat_list]
            cat_wf_list = cat_wf_list + pkg_wfs
            cat_list = cat_list + pkg_cats
            wf_modules.update(pkg_wf_modules)
        else:
            # assume the module defines workflows and generates a .wfm or .wfl
            if not cat_root in cat_list:
                cat_list.append(cat_root)
            cat_wf_list.append( (cat_root,modname) )
            wf_modules[cat_root+'.'+modname] = os.path.join(path_[0],modname) 
    # don't import these modules: it will cause an import loop
    #for wf_uri,wf_path in wf_modules.items():
    #    wf_mod = importlib.import_module('.'+wf_uri,__name__)
    return cat_list, cat_wf_list, wf_modules

cat_list, cat_wf_list, wf_modules = load_workflows(__path__,__name__)

def import_workflow(wf_module_key):
    mod = importlib.import_module('.'+wf_module_key,__name__)
    return mod.__dict__[wf_module_key.split('.')[-1]]

#print(cat_list)
#print(cat_wfl_list)
#print(wfl_modules)

