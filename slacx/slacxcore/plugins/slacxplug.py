import abc

class SlacxPlugin(object):
    __metaclass__ = abc.ABCMeta
    """
    Abstract class for imposing slacx plugin structure via inheritance.
    """

    def __init__(self,input_names):
        super(SlacxPlugin,self).__init__()
        self.inputs = OrderedDict()
        self.input_doc = {}
        self.input_src = {}
        self.input_type = {}
        # For each of the var names, assign to None 
        for name in input_names: 
            self.input_src[name] = optools.no_input
            self.input_type[name] = optools.none_type
            self.inputs[name] = None
            self.input_doc[name] = None

    def stop(self):
        """
        SlacxPlugin.stop() should provide a clean end for the plugin,
        for instance closing all connections and files used by the plugin.
        The default implementation does nothing, 
        assumes the plugin can be cleanly terminated by dereferencing. 
        """
        pass

    def description(self):
        """
        SlacxPlugin.description() returns a string 
        documenting the functionality of the SlacxPlugin.
        The default implementation returns no description. 
        """
        return "No description available"

    def content(self):
        """
        SlacxPlugin.content() returns a data structure 
        containing the meaningful objects contained in the plugin.
        The default implementation returns the plugin itself. 
        """
        return self


