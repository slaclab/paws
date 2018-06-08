from __future__ import print_function
from collections import OrderedDict
from functools import partial
import importlib

from ..models.TreeModel import TreeModel
from .. import plugins as pgns
from .. import pawstools
from .PawsPlugin import PawsPlugin

class PluginManager(TreeModel):
    """Tree for storing, browsing, and managing PawsPlugins"""

    def __init__(self):
        flag_dict = OrderedDict(selected=False,running=False)
        super(PluginManager,self).__init__(flag_dict)
        self.plugins = self._root_dict
        self.message_callback = self.tagged_print 

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

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
        if not self.is_tag_valid(plugin_name): 
            raise pawstools.PluginNameError(self.tag_error_message(plugin_name))
        #p.message_callback = self.message_callback
        p.data_callback = partial(self.set_plugin_item,plugin_name)
        self.set_item(plugin_name,p)
        self.get_from_uri(plugin_name).flags['running'] = False 

    def set_plugin_item(self,pgn_name,item_uri,item_data):
        full_uri = pgn_name+'.'+item_uri
        self.set_item(full_uri,item_data)

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

    def set_input(self,plugin_name,input_name,val,tp=None):
        """Set a plugin input to the provided value.

        Parameters
        ----------
        plugin_name : str
            Name that will be used to refer to this plugin after it is added.
        input_name : str
            name of the input to be set
        val : object
            the data to be used as plugin input
        tp : str or int, optional
            the input type determines how the PluginManager 
            interprets the input value `val`.
        """
        if not plugin_name in self.plugins.keys():
            raise KeyError('Plugin {} does not exist'.format(plugin_name))
        if not input_name in self.plugins[plugin_name].inputs.keys():
            raise KeyError('Input name {} not valid for PawsPlugin {} ({}).'
            .format(input_name,plugin_name,type(self.plugins[plugin_name]).__name__))
        if tp is not None and not tp in pawstools.valid_types and not tp in pawstools.input_types:
            # tp is neither a string or an enum
            raise ValueError('[{}] failed to parse input type: {}'.format(__name__,tp))
        il = self.plugins[plugin_name].input_locator[input_name]
        if tp is not None:
            if tp in pawstools.input_types:
                tp = pawstools.input_types.index(tp)
            il.tp = pawstools.valid_types[tp]
        if il.tp == pawstools.runtime_type:
            # set il.val as None to exclude this il.val from serialization
            il.val = None
        else:
            il.val = val
        if il.tp in [pawstools.basic_type,pawstools.runtime_type]:
            # these types may be loaded for immediate use
            self.set_item(plugin_name+'.inputs.'+input_name,val)

    def start_plugins(self,plugin_name_list):
        for pn in plugin_name_list:
            self.start_plugin(pn)

    def start_plugin(self,plugin_name):
        """Start the plugin referred to by `plugin_name`."""
        self.message_callback('starting plugin {}'.format(plugin_name))
        self.prepare_plugin(plugin_name)
        # keep track of run state with treeitem flags
        self.get_from_uri(plugin_name).flags['running'] = True 
        self.plugins[plugin_name].start()

    def prepare_plugin(self,plugin_name):
        pgn = self.plugins[plugin_name]
        for inpname,il in pgn.input_locator.items():
            full_uri = plugin_name+'.inputs.'+inpname
            if il.tp == pawstools.plugin_item:
                if isinstance(il.val,list):
                    item_data = []
                    for item_name in il.val:
                        item = self.get_data_from_uri(item_name)
                        item_data.append(item)
                else:
                    item_data = self.get_data_from_uri(il.val)
            elif il.tp == pawstools.basic_type:
                item_data = il.val
            else:
                raise ValueError('Unable to set input type {} for plugin {}'
                .format(il.tp,plugin_name))
            self.set_item(full_uri,item_data)

    def stop_plugin(self,plugin_name):
        self.message_callback('stopping plugin {}'.format(plugin_name))
        self.plugins[plugin_name].stop()
        # keep track of run state with treeitem flags
        self.get_from_uri(plugin_name).flags['running'] = False 

    def load_plugin(self,plugin_name,plugin_setup_dict):
        """Load a plugin from a dict of setup data.

        Intended to load plugins from saved data.

        Parameters
        ----------
        plugin_name : str
            Name that will be used to refer to this plugin after it is added.
        plugin_setup_dict : dict 
            Dict specifying plugin setup
        """
        plugin_mod = plugin_setup_dict['plugin_module']
        self.add_plugin(plugin_name,plugin_mod)
        p = self.plugins[plugin_name]
        # TODO: refactor, remove inputlocators from plugins
        #il_setup_dict = plugin_setup_dict['inputs']
        #for inp_name in p.inputs.keys():
        #    if inp_name in il_setup_dict.keys():
        #        tp = il_setup_dict[inp_name]['tp']
        #        val = il_setup_dict[inp_name]['val']
        #        self.set_input(plugin_name,inp_name,val,tp)

    def n_plugins(self):
        """Return number of plugins currently loaded."""
        return len(self.plugins) 

    def build_tree(self,x):
        """Return a dict describing a tree-like structure of this object.

        This is a reimplemention of TreeModel.build_tree() 
        to define this object's child tree structure.
        For a PluginManager, a dict is provided for each PawsPlugin,
        where the dict contains the results of calling
        self.build_tree(plugin.inputs)
        """
        if isinstance(x,PawsPlugin):
            d = OrderedDict()
            d['inputs'] = self.build_tree(x.inputs)
            d.update(x.get_plugin_content())
        else:
            return super(PluginManager,self).build_tree(x) 
        return d


