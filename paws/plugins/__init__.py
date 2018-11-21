import pkgutil
import os

def load_plugins(pkg_path):
    p_names = []
    # pkgutil.iter_modules returns module_loader, module_name, ispkg forall modules in path
    mods = pkgutil.iter_modules(pkg_path)
    mods = [mod for mod in mods if mod[1] not in ['__init__','PawsPlugin','PluginManager']]
    for modloader, modname, ispkg in mods:
        p_names.append(modname)
    return p_names

plugin_name_list = load_plugins(__path__)
    
