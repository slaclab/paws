from __future__ import print_function
from collections import OrderedDict
from .PawsPlugin import PawsPlugin
import datetime
import copy
import time
from threading import Condition

import tzlocal
import numpy as np

class Timer(PawsPlugin):
    """A Paws plugin for signaling the passage of time."""

    def __init__(self,dt=1.,t_max=10.,verbose=False,log_file=None):
        """Create a Timer.

        Parameters
        ----------
        dt : float
            Time in seconds between ticks
            (each tick notifies self.dt_lock)
        t_max : float
            Time in seconds after which the timer stops itself
        """
        super(Timer,self).__init__(thread_blocking=True,verbose=verbose,log_file=log_file)
        self.dt = dt
        self.t_max = t_max
        self.dt_lock = Condition()

    @classmethod
    def clone(cls,dt,t_max,verbose,log_file):
        return cls(dt,t_max,verbose,log_file)

    def build_clone(self):
        cln = self.clone(self.dt,self.t_max,self.verbose,self.log_file)
        return cln

    def start(self):
        super(Timer,self).start()

    def run(self):
        # self.thread_clone runs this method in its own thread.
        self.tz = tzlocal.get_localzone()
        # self.ep: datetime object representing the epoch
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        # self.t0: t0 as a datetime object
        self.t0 = datetime.datetime.now(self.tz)
        # self.t0_epoch: t0 in seconds since the epoch
        self.t0_epoch = (self.t0-self.ep).total_seconds()
        t_elapsed = self.get_elapsed_time()
        keep_going = True
        # initial tick notification:
        self.proxy.dt_notify()
        while t_elapsed < self.t_max and keep_going:
            if self.proxy.verbose: self.proxy.message_callback('timer tick {}/{}'.format(t_elapsed,self.t_max))
            # attempt to nail the next dt point:
            t_rem = self.dt-np.mod(self.get_elapsed_time(),self.dt)
            time.sleep(t_rem)
            # tick notification
            self.proxy.dt_notify()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
                if self.verbose and not keep_going: self.message_callback('timer STOPPED')
        # if time ran out naturally, proxy must be told to stop()
        with self.proxy.running_lock:
            self.proxy.stop()
        # one final tick to mobilize any plugins 
        # that are waiting on dt_lock
        self.proxy.dt_notify()
        if self.verbose: self.message_callback('Timer FINISHED')

    def dt_notify(self):
        with self.dt_lock:
            if int(self.py_version) == 2:
                self.dt_lock.notifyAll()
            else:
                self.dt_lock.notify_all()

