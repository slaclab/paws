from __future__ import print_function
from collections import OrderedDict
import copy

from ..operations import Operation as opmod

class PawsPlugin(object):
    """Class template for implementing PAWS Plugins"""

    def __init__(self,inputs):
        super(PawsPlugin,self).__init__()
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.message_callback = print
        self.data_callback = None 

    def __getitem__(self,key):
        d = self.content()
        if key in d.keys():
            return d[key]
        else:
            raise KeyError('[{}] {}.__getitem__ only recognizes keys {}'
            .format(__name__,type(self).__name__,d.keys()))
    def __setitem__(self,key,data):
        d = self.content()
        if key in d.keys():
            d[key] = data
        else:
            raise KeyError('[{}] {}.__setitem__ only recognizes keys {}'
            .format(__name__,type(self).__name__,d.keys()))
    def keys(self):
        return self.content().keys() 

    def start(self):
        """
        PawsPlugin.start() should perform any setup required by the plugin,
        for instance setting up connections and reading files used by the plugin.
        The default implementation does nothing.
        """
        pass

    def stop(self):
        """
        PawsPlugin.stop() should provide a clean end for the plugin,
        for instance closing all connections and files used by the plugin.
        The default implementation does nothing, 
        assumes the plugin can be cleanly terminated by dereferencing. 
        """
        pass

    def description(self):
        """
        PawsPlugin.description() returns a string 
        documenting the functionality of the PawsPlugin.
        The default implementation returns no description. 
        """
        return "No description available"

    def content(self):
        """
        PawsPlugin.content() returns a dict
        containing the meaningful objects contained in the plugin.
        The default implementation returns an empty dict. 
        """
        return {}


