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

from .. import pawstools

class PawsPlugin(object):
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
        history_file = '{}_{}.log'.format(type(self).__name__,t0_utc)
        self.history_path = None
        self.set_history_path(os.path.join(pawstools.paws_scratch_dir,history_file))
        self.verbose = False

    def set_history_path(self,file_path):
        if file_path == self.history_path:
            return
        suffix = 1
        fp = file_path
        pth,ext = os.path.splitext(fp)
        while os.path.exists(fp):
            fp = pth+'_{}'.format(suffix)+ext
            suffix += 1
        open(fp,'a').close()
        self.message_callback('plugin log file: {}'.format(fp))
        self.history_path = fp 

    def set_log_dir(self,dir_path): 
        dp,fn = os.path.split(self.history_path)
        self.set_history_path(os.path.join(dir_path,fn))

    def set_log_file(self,file_name):
        dp,fn = os.path.split(self.history_path)
        self.set_history_path(os.path.join(dp,file_name))

    def set_verbose(self,verbose_flag):
        if verbose_flag:
            self.verbose = True
        else:
            self.verbose = False 

    def set_data(self,item_key,val):
        key_parts = item_key.split('.')
        itm = self
        for p in key_parts[:-1]:
            itm = itm[p]
        itm[key_parts[-1]] = val

    def __getitem__(self,key):
        return self.get_plugin_content()[key]
    def keys(self):
        return self.get_plugin_content().keys() 
    # TODO: make plugins into DictTrees, or make them work as such
    def __setitem__(self,key,val):
        self.set_data(key,val)

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
        new_pgn.verbose = bool(self.verbose)
        #new_pgn.data_callback = self.data_callback
        #new_pgn.message_callback = self.message_callback
        return new_pgn

    def add_to_history(self,t,msg):
        """Add a timestamp and a message to the plugin's history."""
        self.history.append((t,msg))
        self.n_events += 1
        if np.mod(self.n_events,100) == 0:
            self.dump_history(90)
            # always keep the past 10 points?
            self.history = self.history[-10:]

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
        return OrderedDict(inputs=self.inputs) 

