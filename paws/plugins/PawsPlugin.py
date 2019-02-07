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
# log files are created at __init__().

class PawsPlugin(object):
    """Base class for building PAWS Plugins."""

    def __init__(self,thread_blocking=False,verbose=False,log_file=None):
        """Create a PawsPlugin.

        Parameters
        ----------
        thread_blocking : bool
            indicates whether or not this plugin runs continually in its thread-
            if thread_blocking is True, the start() method 
            clones the plugin and asks the clone to run() in its own thread
        verbose : bool
            if verbose, various status messages are fed to self.message_callback()
        log_file : str
            path to a file used for logging time-stamped plugin activities
        """
        super(PawsPlugin,self).__init__()
        self.message_callback = self.tagged_print
        self.thread_blocking = thread_blocking 
        # py_version is used to determine notify() syntax 
        self.py_version = int(sys.version[0])
        self.running = False
        # thread-blocking plugins acquire running_lock before modifying self.running 
        self.running_lock = Condition()
        self.history = []
        self.n_events = 0
        # plugins acquire history_lock before modifying self.history
        self.history_lock = Condition()
        # timestamps are used for logging
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        self.t0 = datetime.datetime.now(self.tz)
        self.t0_epoch = (self.t0-self.ep).total_seconds()
        # set verbosity and log file
        self.verbose = verbose
        self.log_file = None
        if log_file: self.set_log_file(log_file)
        # thread_clone is a functional clone of this object,
        # which is meant to run() in its own thread, 
        # which it may block freely without stalling the main thread
        self.thread_clone = None
        # proxy is the thread_clone's ref to this object, 
        # i.e., self.thread_clone.proxy is self.
        self.proxy = None

    def get_elapsed_time(self):
        t_now = datetime.datetime.now(self.tz)
        t_elapsed = (t_now-self.t0).total_seconds()
        return t_elapsed

    def get_epoch_time(self):
        t_now = datetime.datetime.now(self.tz)
        t_epoch = (t_now-self.ep).total_seconds()
        return t_epoch

    def get_date_time(self):
        return str(datetime.datetime.now(self.tz))

    def set_log_file(self,file_path=None):
        if not file_path:
            log_file = '{}_{}.log'.format(type(self).__name__,int(self.t0_utc*1000))
            file_path = os.path.join(pawstools.paws_scratch_dir,log_file)
        if file_path == self.log_file:
            return
        suffix = 1
        pth,ext = os.path.splitext(file_path)
        while os.path.exists(file_path):
            file_path = pth+'_{}'.format(suffix)+ext
            suffix += 1
        open(file_path,'a').close()
        if self.verbose: self.message_callback('plugin log file: {}'.format(file_path))
        self.log_file = file_path 

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

        Assuming a plugin's attributes have been properly set,
        PawsPlugin.start() should prepare the plugin and its thread_clone, 
        e.g. by setting attributes, opening connections, reading files, etc. 
        Reimplement this in PawsPlugin subclasses as needed.
        """
        self.running = True 
        if self.thread_blocking: 
            self.run_clone()
        else:
            self.run()
        msg = '{} plugin started'.format(type(self).__name__)
        self.add_to_history(msg)

    def run(self):
        """Run the plugin. Any meaningful plugin activities should happen here."""
        pass

    def run_clone(self):
        self.thread_clone = self.build_clone()
        self.thread_clone.proxy = self
        #self.proxy = self
        th = Thread(target=self.thread_clone.run)
        th.start()
        self.running = True

    @classmethod
    def clone(cls):
        return cls()

    def build_clone(self):
        """Thread blocking plugins must implement build_clone()."""
        raise NotImplementedError('Thread-blocking plugins must implement build_clone().') 

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
        if self.log_file:
            self.dump_history()

    def add_to_history(self,msg):
        """Add a timestamp and a message to the plugin's history."""
        with self.history_lock:
            dt = self.get_date_time()
            self.history.append((dt,msg))
            self.n_events += 1
            if np.mod(self.n_events,100) == 0:
                self.dump_history(90)
                # always keep the past 10 points?
                self.history = self.history[-10:]

    def dump_history(self,n_events=None):
        with self.history_lock:
            if self.log_file:
                dump_file = open(self.log_file,'a')
                h = self.history
                if n_events is not None: h = self.history[:n_events]
                for t,msg in h:
                    dump_file.write('{}: {}'.format(t,msg)+os.linesep)
                dump_file.close()

    #def notify_locks(self,locks):
    #    if not isinstance(locks,list):
    #        locks = [locks]
    #    for l in locks:
    #        with l:
    #            if int(self.py_version) == 2:
    #                l.notifyAll()
    #            else:
    #                l.notify_all()

