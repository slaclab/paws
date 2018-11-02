from __future__ import print_function
from collections import OrderedDict
from functools import partial
import importlib

from ..pawstools import DictTree
from .. import plugins as pgns

class PluginManager(DictTree):
    """Tree for storing, browsing, and managing PawsPlugins"""

    def __init__(self):
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

    def set_plugin_contents(self,plugin_name,**kwargs):
        for nm,val in kwargs.items():
            self.set_plugin_item(plugin_name,nm,val)

    #def set_plugin_content(self,plugin_name,item_name,val):
    #    """Set an item of plugin content to the provided value.
    #
    #    Parameters
    #    ----------
    #    plugin_name : str
    #        Name that will be used to refer to this plugin after it is added.
    #    item_name : str
    #        name of the plugin content item to be set
    #    val : object
    #        the data to be referenced to the specified item 
    #    """
    #    self.set_data(plugin_name+'.'+item_name,val)

    def set_plugin_item(self,pgn_name,item_key,item_data):
        full_key = pgn_name+'.'+item_key
        self.set_data(full_key,item_data)

    def connect(self,item_key,content_map):
        """Connect the data at `item_key` to one or more plugin content items.

        Sets up Plugin content listed in `content_map`
        to take the value at `item_key`.
        `content_map` can be a DictTree key (string) or a list thereof.
        """
        if item_key in self.connections:
            if isinstance(content_map,list):
                self.connections[item_key].extend(content_map)
            else:
                self.connections[item_key].append(content_map)
        else:
            if not isinstance(content_map,list): content_map = [content_map]
            self.connections[item_key] = content_map

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
        for item_key,content_map in self.connections.items():
            for content_key in content_map:
                if content_key.split('.')[0] == plugin_name:
                    self.set_data(content_key,self.get_data(item_key))
                    if pgn.thread_blocking:
                        pgn_item_key = content_key[content_key.find(plugin_name)+len(plugin_name)+1:]
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
            pg_dict[pg_name]['CONTENT'] = pg.content
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
        for item_key,content_map in pg_dict.pop('CONNECTIONS').items():
            self.connect(item_key,content_map)
        for pg_name in pg_dict.keys():
            self.add_plugin(pg_name,pg_dict[pg_name]['MODULE'])
            for item_name, val in pg_dict[pg_name]['CONTENT'].items():
                self.set_plugin_content(pg_name,item_name,val)

    def n_plugins(self):
        """Return number of plugins currently loaded."""
        return len(self.plugins) 


