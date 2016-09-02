import pkgutil
import importlib

from core.operations.slacxop import Operation

# pkgutil.iter_modules returns module_loader, module_name, ispkg forall modules in path
mods = pkgutil.iter_modules(__path__)
# leave out the __init__ module, any modules that load core.operations, and the abc module slacxop 
mods = [mod for mod in mods if mod[1] not in ['__init__','slacxop','slacxopman']]
op_list = []

for modloader, modname, ispkg in mods:
    try:
        #print '[{}] importing module {}...'.format(__name__,modname)
        # import the module
        mod = importlib.import_module('.'+modname,'core.operations')
        # iterate through the module's __dict__, find Operations 
        for name, item in mod.__dict__.items():
            # is it a class?
            if isinstance(item,type):
                # is it a non-abstract subclass of Operation?
                if issubclass(item,Operation) and name is not 'Operation':
                    op_list.append(getattr(mod,name))
    except ImportError as ex:
        print '[{}] had trouble dealing with module item {}: {}'.format(__name__,name,item)
        raise ex



