from __future__ import print_function
from collections import OrderedDict
import copy

from .. import pawstools

class PawsPlugin(object):
    """Base class for building PAWS Plugins."""

    def __init__(self,inputs):
        super(PawsPlugin,self).__init__()
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.input_locator = OrderedDict.fromkeys(self.inputs.keys())
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.message_callback = self.tagged_print
        self.data_callback = None 
        self.running = False
        for name in self.inputs.keys(): 
            self.input_locator[name] = pawstools.InputLocator(pawstools.basic_type,self.inputs[name])

    def __getitem__(self,key):
        if key == 'inputs':
            return self.inputs
        else:
            raise KeyError('[{}] {} not in valid plugin keys: {}'
            .format(__name__,key,self.keys()))
    def keys(self):
        return ['inputs'] 

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def get_plugin_content(self):
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
        self.running = True 

    def stop(self):
        """Stop the plugin.

        PawsPlugin.stop() should provide a clean end for the plugin,
        for instance closing connections used by the plugin.
        Reimplement this in PawsPlugin subclasses as needed.
        """
        self.running = False 

    @classmethod
    def clone(cls):
        return cls()

    def build_clone(self):
        """Clone the Plugin."""
        new_pgn = self.clone()
        for inp_nm,il in self.input_locator.items():
            if il.tp == pawstools.basic_type:
                new_pgn.inputs[inp_nm] = copy.deepcopy(self.inputs[inp_nm]) 
            elif il.tp == pawstools.plugin_item:
                # plugins are expected to be threadsafe
                new_pgn.inputs[inp_nm] = self.inputs[inp_nm]
        #new_pgn.data_callback = self.data_callback
        #new_pgn.message_callback = self.message_callback
        #if self.running:
        #    new_pgn.start()
        return new_pgn

    def setup_dict(self):
        """Return a dict that states the plugin's module and inputs."""
        pgin_mod = self.__module__[self.__module__.find('plugins'):]
        pgin_mod = pgin_mod[pgin_mod.find('.')+1:]
        dct = OrderedDict() 
        dct['plugin_module'] = pgin_mod
        inp_dct = OrderedDict() 
        for nm,il in self.input_locator.items():
            inp_dct[nm] = {'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct['inputs'] = inp_dct 
        return dct


