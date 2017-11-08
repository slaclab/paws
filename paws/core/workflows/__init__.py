import os
import pkgutil

wfl_modules = {} 
def load_wfls_from_path(path_,pkg,cat_root=''):
    wfls = []
    cats = []
    mods = pkgutil.iter_modules(path_)
    mods = [mod for mod in mods if mod[1] not in ['__init__','Workflow','WfManager','wftools']]
    for modloader, modname, ispkg in mods:
        if ispkg:
            pkg_path = [os.path.join(path_[0],modname)]
            subcat_root = modname
            if cat_root:
                subcat_root = cat_root+'.'+modname
            pkg_wfls, pkg_cats = load_wfls_from_path(pkg_path,pkg+'.'+modname,subcat_root)
            pkg_wfls = [wfl for wfl in pkg_wfls if not wfl in wfls]
            pkg_cats = [cat for cat in pkg_cats if not cat in cats]
            wfls = wfls + pkg_wfls
            cats = cats + pkg_cats
        else:
            if not cat_root in cats:
                cats.append(cat_root)
            wfls.append( (cat_root,modname) )
            wfl_modules[cat_root+'.'+modname] = os.path.join(path_[0],modname) 
    return wfls, cats

cat_wfl_list, cat_list = load_wfls_from_path(__path__,__name__)

