import pkgutil

def load_plugins(path_,pkg):
    p_names = []
    # pkgutil.iter_modules returns module_loader, module_name, ispkg forall modules in path
    mods = pkgutil.iter_modules(path_)
    mods = [mod for mod in mods if mod[1] not in ['__init__','plugin','plugin_manager']]
    for modloader, modname, ispkg in mods:
        p_names.append(modname)
    return p_names 

plugin_name_list = load_plugins(__path__,__name__)
    
