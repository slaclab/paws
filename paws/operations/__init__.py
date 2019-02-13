import os
import pkgutil

op_modules = []
def load_ops_from_path(path_,pkg,cat_root=''):
    ops = []
    cats = []
    mods = pkgutil.iter_modules(path_)
    mods = [mod for mod in mods if mod[1] not in ['__init__','Operation']]
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
            op_modules.append(cat_root+'.'+modname)
    return ops, cats

cat_op_list, cat_list = load_ops_from_path(__path__,__name__)

