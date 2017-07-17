import abc
from collections import OrderedDict

from ..operations import Operation as op

class PawsPlugin(object):
    __metaclass__ = abc.ABCMeta
    """
    Abstract class for imposing paws plugin structure via inheritance.
    """

    def __init__(self,input_names):
        super(PawsPlugin,self).__init__()
        self.inputs = OrderedDict()
        self.input_doc = {}
        self.input_src = {}
        self.input_type = {}
        # For each of the var names, assign to None 
        for name in input_names: 
            self.input_src[name] = op.no_input
            self.input_type[name] = op.none_type
            self.inputs[name] = None
            self.input_doc[name] = None

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


