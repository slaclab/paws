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
import tzlocal
import datetime

from ..models.TreeModel import TreeModel
from .. import pawstools

class PawsPlugin(TreeModel):
    """Base class for building PAWS Plugins."""

    def __init__(self,inputs):
        super(PawsPlugin,self).__init__()
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.message_callback = self.tagged_print
        self.data_callback = None 
        # take the running_lock when toggling the run flag 
        self.running_lock = Condition()
        self.running = False
        self.n_events = 0
        # use command_lock to add or pop commands from the queue
        self.command_lock = Condition()
        self.commands = queue.Queue() 
        # use history lock to edit the history
        self.history_lock = Condition()
        self.history = []
        # by default, plugins are assumed to be non-blocking
        self.thread_blocking = False
        # if a plugin is blocking, it will act as a proxy,
        # while a thread_clone does the work.
        # proxy is the thread_clone's ref to this object, i.e.
        # self.thread_clone.proxy == self.
        self.thread_clone = None
        self.proxy = None
        # keep track of py version for convenience
        self.py_version = int(sys.version[0])
        tz = tzlocal.get_localzone()
        ep = datetime.datetime.fromtimestamp(0,tz)
        t0 = datetime.datetime.now(tz)
        t0_utc = int((t0-ep).total_seconds())
        self.history_file = '{}_{}.log'.format(type(self).__name__,t0_utc)
        self.history_path = os.path.join(pawstools.paws_scratch_dir,self.history_file)

    def set_log_path(self,file_path):
        dp,fn = os.path.split(file_path)
        self.history_file = fn 
        self.history_path = file_path 

    def set_log_file(self,file_name):
        dp,fn = os.path.split(self.history_path)
        self.history_file = file_name 
        self.history_path = os.path.join(dp,file_name)

    def set_log_dir(self,dir_path): 
        self.history_path = os.path.join(dir_path,self.history_file)

    def set_item(self,item_uri,val):
        uri_parts = item_uri.split('.')
        itm = self
        for p in uri_parts[:-1]:
            itm = itm[p]
        itm[uri_parts[-1]] = val

    def __getitem__(self,key):
        if key == 'inputs':
            return self.inputs
        elif key == 'history':
            return self.history
        elif key == 'running':
            return self.running
        elif key == 'commands':
            return self.commands
        else:
            raise KeyError('[{}] {} not in valid plugin keys: {}'
            .format(__name__,key,self.keys()))
    def keys(self):
        return ['inputs','history','running','commands'] 

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

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
        #self.thread_clone = self.build_clone()
        #self.thread_clone.proxy = self
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
        for inp_nm,val in self.inputs.items():
            new_pgn.inputs[inp_nm] = copy.deepcopy(val) 
        #new_pgn.data_callback = self.data_callback
        #new_pgn.message_callback = self.message_callback
        return new_pgn

    def add_to_history(self,t,msg):
        """Add a timestamp and a message to the plugin's history."""
        self.history.append((t,msg))
        self.n_events += 1
        if np.mod(self.n_events,1000) == 0:
            self.dump_history(900)
            # always keep the past 100 points?
            self.history = self.history[-100:]

    def dump_history(self,n_events=None):
        dump_file = open(self.history_path,'a')
        h = self.history
        if n_events is not None: h = self.history[:n_events]
        for t,msg in h:
            dump_file.write('{}: {}'.format(t,msg)+os.linesep)
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

    def get_plugin_content(self):
        return {}

