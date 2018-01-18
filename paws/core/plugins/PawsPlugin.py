from __future__ import print_function
from collections import OrderedDict
import copy

class PawsPlugin(object):
    """Base class for building PAWS Plugins."""

    def __init__(self,inputs):
        super(PawsPlugin,self).__init__()
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.message_callback = print
        self.data_callback = None 

    def __getitem__(self,key):
        if key == 'inputs':
            return self.inputs
        elif key == 'content':
            return self.content()
        else:
            raise KeyError('[{}] PawsPlugins only recognize keys {}'
            .format(__name__,self.keys()))
    def keys(self):
        return ['inputs','content'] 

    def content(self):
        """Return a dict containing meaningful plugin content.

        This method is used to fetch Plugin content.
        It should be reimplemented for most practical PawsPlugin subclasses.
        """
        return {}

    def description(self):
        """Describe the plugin.

        PawsPlugin.description() returns a string 
        documenting the functionality of the PawsPlugin,
        the current input settings, etc.
        Reimplement this in PawsPlugin subclasses.
        """
        return str(self.setup_dict()) 

    def start(self):
        """Start the plugin.

        Assuming a plugin's inputs have been set,
        PawsPlugin.start() should prepare the plugin for use, 
        e.g. by opening connections, reading files, etc. 
        Reimplement this in PawsPlugin subclasses as needed.
        """
        pass

    def stop(self):
        """Stop the plugin.

        PawsPlugin.stop() should provide a clean end for the plugin,
        for instance closing connections used by the plugin.
        Reimplement this in PawsPlugin subclasses as needed.
        """
        pass

    def setup_dict(self):
        """Return a dict that states the plugin's module and inputs."""
        pgin_mod = self.__module__[self.__module__.find('plugins'):]
        pgin_mod = pgin_mod[pgin_mod.find('.')+1:]
        dct = OrderedDict() 
        dct['plugin_module'] = pgin_mod
        dct['inputs'] = self.inputs 
        return dct


