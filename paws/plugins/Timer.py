from __future__ import print_function
from collections import OrderedDict
from .PawsPlugin import PawsPlugin
import datetime
import copy
import time
from threading import Condition

import tzlocal
import numpy as np

content = OrderedDict(
    dt=1.,
    t_max=None,
    dt_now=None,
    utc_now=None)

class Timer(PawsPlugin):
    """A Paws plugin for marking the passage of time"""

    def __init__(self):
        super(Timer,self).__init__(content)
        self.content_doc['dt'] = 'Wait time between signals, in seconds'
        self.content_doc['t_max'] = 'Seconds after which the timer stops itself'
        self.content_doc['dt_now'] = 'Seconds from Timer.start() to the most recent Timer.dt_now()'
        self.content_doc['t_now'] = 'Time in seconds since the Unix epoch at the most recent Timer.dt_now()'
        # A lock for the "tick" trigger 
        self.dt_lock = Condition()
        self.t0 = None 
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        self.t0_epoch = None 
        self.thread_blocking = True

    def start(self):
        self.tz = tzlocal.get_localzone()
        # self.ep: datetime object representing the epoch
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        # self.t0: t0 as a datetime object
        self.t0 = datetime.datetime.now(self.tz)
        # self.t0_epoch: t0 in seconds since the epoch
        self.t0_epoch = (self.t0-self.ep).total_seconds()
        super(Timer,self).start()

    def run(self):
        # self.thread_clone runs this method in its own thread.
        if self.verbose: self.message_callback('timer STARTED')
        #with self.proxy.dt_lock:
        dt = self.content['dt'] 
        t_max = self.content['t_max']
        keep_going = True
        # set zero-time points 
        self.t0 = copy.deepcopy(self.proxy.t0)
        self.t0_epoch = copy.deepcopy(self.proxy.t0_epoch)
        t_now = self.get_elapsed_time()
        # initial tick notification:
        self.proxy.dt_notify()
        while t_elapsed < t_max and keep_going:
            if self.verbose: self.message_callback('tick: {}/{}'.format(t_elapsed,t_max))
            # attempt to nail the next dt point:
            t_rem = dt-np.mod(self.get_elapsed_time(),dt)
            time.sleep(t_rem)
            # get_elapsed_time to update time stamps
            t_elapsed = self.get_elapsed_time()
            # tick notification
            self.proxy.dt_notify()
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
                if self.verbose and not keep_going: self.message_callback('timer STOPPED')
        # take a few extra ticks for listening plugins to stop themselves?
        if self.verbose: self.message_callback('Ticking a few more times before stopping')
        for itick in range(3):
            time.sleep(dt)
            self.proxy.dt_notify()
        with self.proxy.running_lock:
            self.proxy.stop()
        # now that the plugin is stopped, notify any other plugins that are waiting on dt_lock
        #with self.proxy.dt_lock:
        self.proxy.dt_notify()
        if self.verbose: self.message_callback('Timer FINISHED')

    def dt_notify(self):
        with self.dt_lock:
            if int(self.py_version) == 2:
                self.dt_lock.notifyAll()
            else:
                self.dt_lock.notify_all()

    def t_epoch(self):
        """Get time in seconds since the epoch"""
        t = datetime.datetime.now(self.tz)
        return float((t-self.ep).total_seconds())

    def time_as_string(self):
        """Get string representing current time"""
        return str(datetime.datetime.now(self.tz))

    def get_elapsed_time(self):
        """Get time in seconds since timer started"""
        # time in seconds since epoch
        tnow = self.t_epoch()
        # minus t0_epoch = elapsed timer time
        t_elapsed = float(tnow-self.t0_epoch)
        self.content['t_now'] = tnow
        self.content['t_elapsed'] = t_elapsed 
        return t_elapsed 

    def description(self):
        desc = str('Timer Plugin for Paws: '\
            'Signals the passage of time, '\
            'as a convenience for other plugins '\
            'who depend on a clock to trigger their actions')
        return desc


