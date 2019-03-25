from __future__ import print_function
import sys
import os
from threading import Condition
#if int(sys.version[0]) == 2:
#    import Queue as queue
#else:
#    import queue 

import numpy as np
import tzlocal
import datetime

from .. import pawstools

class PawsPlugin(object):
    """Base class for building PAWS Plugins."""

    def __init__(self,verbose=False,log_file=None):
        """Create a PawsPlugin.

        Parameters
        ----------
        verbose : bool
            if verbose, various status messages are fed to self.message_callback()
        log_file : str
            path to a file used for logging time-stamped plugin activities
        """
        super(PawsPlugin,self).__init__()
        self.message_callback = self.tagged_print
        # py_version is used to determine notify() syntax 
        self.py_version = int(sys.version[0])
        # plugins with threads must acquire running_lock before modifying self.running;
        # running_lock is also used sometimes for a plugin to wait for a thread to finish setup
        self.running_lock = Condition()
        self.running = False
        # plugins with threads must acquire history_lock before modifying self.history
        self.history_lock = Condition()
        self.history = []
        self.n_events = 0
        # timestamps are used for logging
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        self.t0 = datetime.datetime.now(self.tz)
        self.t0_epoch = (self.t0-self.ep).total_seconds()
        # set verbosity and log file
        self.verbose = verbose
        self.log_file = None
        if log_file: self.set_log_file(log_file)

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
        print('[{}], {} \n{}'.format(type(self).__name__,self.get_date_time(),msg))

    def start(self):
        """Start the plugin.

        Assuming a plugin's attributes have been properly set,
        PawsPlugin.start() should prepare the plugin, 
        e.g. by setting attributes, opening connections, reading files, etc. 
        Reimplement this in PawsPlugin subclasses as needed.
        """
        self.running = True 
        self._run()
        msg = '{} plugin started'.format(type(self).__name__)
        self.add_to_history(msg)

    def _run(self):
        """Run the plugin. 

        Meaningful plugin activities, such as control loops, 
        data logging, etc., should happen here.
        """
        pass

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

