from __future__ import print_function
from collections import OrderedDict
import sys
import os
import copy
from threading import Thread, Condition
if int(sys.version[0]) == 2:
    import Queue as queue
else:
    import queue 

import numpy as np

from .. import pawstools

class PawsPlugin(object):
    """Base class for building PAWS Plugins."""

    def __init__(self,inputs):
        super(PawsPlugin,self).__init__()
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.input_locator = OrderedDict.fromkeys(self.inputs.keys())
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        for name in self.inputs.keys(): 
            self.input_locator[name] = pawstools.InputLocator(pawstools.basic_type,self.inputs[name])
        self.message_callback = self.tagged_print
        self.data_callback = None 
        self.running_lock = Condition()
        self.running = False
        self.n_events = 0
        self.command_lock = Condition()
        self.commands = queue.Queue() 
        self.history_lock = Condition()
        self.history = []
        self.thread_clone = None
        self.proxy = None
        self.py_version = int(sys.version[0])

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
        with self.history_lock:
            h = copy.deepcopy(self.history)
        return {'history':h}

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

    def run_clone(self):
        with self.running_lock:
            self.running = True
        self.thread_clone = self.build_clone()
        self.thread_clone.proxy = self
        th = Thread(target=self.thread_clone.run)
        th.start()

    def run_notify(self):
        with self.running_lock:
            if int(self.py_version) == 2:
                self.running_lock.notifyAll()
            else:
                self.running_lock.notify_all()

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

    def add_to_history(self,t,cmd,resp):
        self.history.append(OrderedDict(t=t,command=cmd,response=resp))
        self.n_events += 1
        if np.mod(self.n_events,1000) == 0:
            self.dump_history(900)
            # always keep the past 100 points?
            self.history = self.history[-100:]

    def dump_history(self,n_events=None):
        dump_path = os.path.join(pawstools.paws_scratch_dir,'{}.log'.format(self))
        dump_file = open(dump_path,'a')
        h = self.history
        if n_events is not None: h = self.history[:n_events]
        for ev in h:
            dump_file.write('{} :: {} :: {}\n'.format(ev['t'],ev['command'],ev['response']))
        dump_file.close()

    def notify_locks(self,locks):
        if not isinstance(locks,list):
            locks = [locks]
        for l in locks:
            with l:
                if int(self.py_version) == 2:
                    l.notifyAll()
                else:
                    l.notify_all()

