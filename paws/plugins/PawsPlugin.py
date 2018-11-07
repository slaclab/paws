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

# TODO: clones pass history back to proxy,
# proxy keeps the log file.
# log files are created at start().

# TODO: ensure plugins run clean either as clones or standalone

class PawsPlugin(object):
    """Base class for building PAWS Plugins."""

    def __init__(self,content):
        super(PawsPlugin,self).__init__()
        self.content = OrderedDict(copy.deepcopy(content))
        self.content_doc = OrderedDict.fromkeys(self.content.keys()) 
        self.message_callback = self.tagged_print
        self.data_callback = None 
        # take the running_lock when toggling the run flag 
        self.running_lock = Condition()
        self.running = False
        # use command_lock to add or pop commands from the queue
        self.command_lock = Condition()
        self.commands = queue.Queue() 
        # use history lock to edit the history
        self.history_lock = Condition()
        self.history = []
        self.n_events = 0
        # proxy is the thread_clone's ref to this object, 
        # i.e. self.thread_clone.proxy is self.
        self.thread_clone = None
        self.proxy = None
        # keep track of py version for convenience
        self.py_version = int(sys.version[0])
        self.log_file = None
        self.verbose = False
        self.thread_blocking = False
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        t0 = datetime.datetime.now(self.tz)
        self.t0_utc = (t0-self.ep).total_seconds()

    def t_utc(self):
        t_now = datetime.datetime.now(self.tz)
        t_utc = (t_now-self.ep).total_seconds()
        return t_utc

    def dt_utc(self):
        t_utc_now = self.t_utc()
        return t_utc_now-self.t0_utc

    def get_date_time(self):
        return str(datetime.datetime.now(self.tz))

    def set_log_file(self,file_path=None):
        log_file = '{}_{}.log'.format(type(self).__name__,int(self.t0_utc*1000))
        if not file_path:
            file_path = os.path.join(pawstools.paws_scratch_dir,log_file)
        if file_path == self.log_file:
            return
        suffix = 1
        pth,ext = os.path.splitext(file_path)
        while os.path.exists(file_path):
            file_path = pth+'_{}'.format(suffix)+ext
            suffix += 1
        open(file_path,'a').close()
        self.message_callback('plugin log file: {}'.format(file_path))
        self.log_file = file_path 

    def set_log_dir(self,dir_path): 
        dp,fn = os.path.split(self.log_file)
        self.set_log_file(os.path.join(dir_path,fn))

    #def set_log_file(self,file_name):
    #    dp,fn = os.path.split(self.log_file)
    #    self.set_log_file(os.path.join(dp,file_name))

    def set_verbose(self,verbose_flag):
        if verbose_flag:
            self.verbose = True
        else:
            self.verbose = False 

    def set_data(self,item_key,val):
        key_parts = item_key.split('.')
        itm = self.content
        for p in key_parts[:-1]:
            itm = itm[p]
        itm[key_parts[-1]] = val

    def __getitem__(self,key):
        return self.content[key]
    def keys(self):
        return self.content.keys() 
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

        Assuming a plugin's content has been properly set,
        PawsPlugin.start() should prepare the plugin for use, 
        e.g. by opening connections, reading files, etc. 
        Reimplement this in PawsPlugin subclasses as needed.
        It can be useful to call super().start() 
        for a default log file and proper thread setup.
        """
        self.set_log_file()
        self.running = True 
        if self.thread_blocking: 
            self.run_clone()
        else:
            self.run()

    def run(self):
        """Use the plugin in a continuing thread.
    
        Plugins with some continuous function should implement run().
        During start(), plugins that must run continually may be cloned, 
        and the continuous functionality is carried out by clone.run(), 
        with thread locks used to share data with the original plugin.
        """
        pass

    def run_clone(self):
        with self.running_lock:
            self.running = True
        #self.thread_clone = self.build_clone()
        #self.thread_clone.proxy = self
        self.thread_clone.log_file = self.log_file
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
        with self.running_lock:
            self.running = False 
        if self.thread_clone:
            self.thread_clone.stop()

    @classmethod
    def clone(cls):
        return cls()

    def build_clone(self):
        """Clone the Plugin."""
        new_pgn = self.clone()
        for nm,val in self.content.items():
            new_pgn.content[nm] = copy.deepcopy(val) 
        new_pgn.verbose = bool(self.verbose)
        #new_pgn.data_callback = self.data_callback
        #new_pgn.message_callback = self.message_callback
        return new_pgn

    # TODO: refactor: optional timestamp, if None get current utc
    def add_to_history(self,t,msg):
        """Add a timestamp and a message to the plugin's history."""
        self.history.append((t,msg))
        self.n_events += 1
        if np.mod(self.n_events,100) == 0:
            self.dump_history(90)
            # always keep the past 10 points?
            self.history = self.history[-10:]

    def dump_history(self,n_events=None):
        dump_file = open(self.log_file,'a')
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

