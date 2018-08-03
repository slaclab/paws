from __future__ import print_function
from collections import OrderedDict
from functools import partial
import importlib

from ..models.DictTree import DictTree
from .. import plugins as pgns
from .. import pawstools
from .PawsPlugin import PawsPlugin

class PluginManager(DictTree):
    """Tree for storing, browsing, and managing PawsPlugins"""

    def __init__(self):
        #flag_dict = OrderedDict(selected=False,running=False)
        super(PluginManager,self).__init__()
        self.plugins = self._root
        self.plugins_running = OrderedDict()
        self.connections = OrderedDict()
        self.message_callback = self.tagged_print 

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def set_verbose(self,plugin_name,flag=True):
        self.plugins[plugin_name].set_verbose(flag)

    def set_log_dir(self,dir_path):
        for nm,pg in self.plugins.items():
            pg.set_log_dir(dir_path)

    def add_plugin(self,plugin_name,plugin_module):
        """Import, name, and add a plugin.

        After a plugin is added to a plugin_manager,
        it is available as plugin_manager.plugins[plugin_name].

        Parameters
        ----------
        plugin_name : str
            Name that will be used to refer to this plugin after it is added.
        plugin_module : str
            Name of the plugin module.
            Example: If class MyPlugin is in the CATEGORY.MyPlugin module,
            retrieve it with `plugin_module` = 'CATEGORY.MyPlugin'.
        """
        p = self.get_plugin(plugin_module)
        if not self.is_key_valid(plugin_name): 
            raise KeyError(self.key_error_message(plugin_name))
        #p.message_callback = self.message_callback
        p.data_callback = partial(self.set_plugin_item,plugin_name)
        self.set_data(plugin_name,p)
        self.plugins_running[plugin_name] = False 
    
    def add_plugins(self,**kwargs):
        for pgn_nm,pgn_mod in kwargs.items():
            self.add_plugin(pgn_nm,pgn_mod)

    def set_plugin_item(self,pgn_name,item_key,item_data):
        full_key = pgn_name+'.'+item_key
        self.set_data(full_key,item_data)

    def get_plugin(self,plugin_module): 
        """Import, instantiate, return a PawsPlugin from its module.

        This can also be used to test the Python environment 
        for compatibility with a plugin.

        Parameters
        ----------
        plugin_module : str
            Name of the plugin module.
            See add_plugin().

        Returns
        -------
        PawsPlugin 
            An instance of the PawsPlugin subclass defined in `plugin_module`. 
        """
        mod = importlib.import_module('.'+plugin_module,pgns.__name__)
        return mod.__dict__[plugin_module]()

    def set_inputs(self,plugin_name,**kwargs):
        for input_name,val in kwargs.items():
            self.set_input(plugin_name,input_name,val)

    def set_input(self,plugin_name,input_name,val):
        """Set a plugin input to the provided value.

        Parameters
        ----------
        plugin_name : str
            Name that will be used to refer to this plugin after it is added.
        input_name : str
            name of the input to be set
        val : object
            the data to be used as plugin input
        """
        self.set_data(plugin_name+'.inputs.'+input_name,val)

    def connect(self,item_key,input_map):
        """Connect the data at `item_key` to one or more inputs.

        Sets up Plugin inputs listed in `input_map`
        to take the value at `item_key`.
        `input_map` can be a TreeItem key (string) or a list thereof.
        """
        if item_key in self.connections:
            if isinstance(input_map,list):
                self.connections[item_key].extend(input_map)
            else:
                self.connections[item_key].append(input_map)
        else:
            if not isinstance(input_map,list): input_map = [input_map]
            self.connections[item_key] = input_map

    def start_plugins(self,plugin_name_list):
        for pn in plugin_name_list:
            self.start_plugin(pn)

    def start_plugin(self,plugin_name):
        """Start the plugin referred to by `plugin_name`."""
        self.message_callback('starting plugin {}'.format(plugin_name))
        pgn = self.prepare_plugin(plugin_name)
        self.plugins_running[plugin_name] = True 
        pgn.start()
        
    def prepare_plugin(self,plugin_name):
        pgn = self.plugins[plugin_name]
        if pgn.thread_blocking:
            pgn_clone = self.plugins[plugin_name].build_clone()
            pgn.thread_clone = pgn_clone 
            pgn.thread_clone.proxy = pgn
        for item_key,input_map in self.connections.items():
            for input_key in input_map:
                if input_key.split('.')[0] == plugin_name:
                    self.set_data(input_key,self.get_data(item_key))
                    if pgn.thread_blocking:
                        pgn_item_key = input_key[input_key.find(plugin_name)+len(plugin_name)+1:]
                        pgn_clone.set_data(pgn_item_key,self.get_data(item_key))
        return pgn

    def stop_plugin(self,plugin_name):
        self.message_callback('stopping plugin {}'.format(plugin_name))
        self.plugins[plugin_name].stop()
        self.plugins_running[plugin_name] = False 

    def setup_dict(self):
        pg_dict = OrderedDict()
        for pg_name,pg in self.plugins.items():
            pg_dict[pg_name] = OrderedDict()
            pg_dict[pg_name]['MODULE'] = pg.__module__[pg.__module__.find('plugins.')+8:] 
            pg_dict[pg_name]['INPUTS'] = pg.inputs
        pg_dict['CONNECTIONS'] = self.connections 
        return pg_dict

    def load_plugins(self,pg_dict):
        """Load plugins from a setup dict.

        Written for loading plugins from saved data.

        Parameters
        ----------
        pg_dict : dict 
            Dict specifying plugin setup
        """
        for item_key,input_map in pg_dict.pop('CONNECTIONS').items():
            self.connect(item_key,input_map)
        for pg_name in pg_dict.keys():
            self.add_plugin(pg_name,pg_dict[pg_name]['MODULE'])
            for inp_name, val in pg_dict[pg_name]['INPUTS'].items():
                self.set_input(pg_name,inp_name,val)

    def n_plugins(self):
        """Return number of plugins currently loaded."""
        return len(self.plugins) 

    #def build_tree(self,x):
    #    """Return a dict describing a tree-like structure of this object.
    #
    #    This is a reimplemention of TreeModel.build_tree() 
    #    to define this object's child tree structure.
    #    For a PluginManager, a dict is provided for each PawsPlugin,
    #    where the dict contains the results of calling
    #    self.build_tree(plugin.inputs)
    #    """
    #    if isinstance(x,PawsPlugin):
    #        d = OrderedDict()
    #        d['inputs'] = self.build_tree(x.inputs)
    #        d.update(x.get_plugin_content())
    #    else:
    #        return super(PluginManager,self).build_tree(x) 
    #    return d


