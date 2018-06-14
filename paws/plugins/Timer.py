from __future__ import print_function
from collections import OrderedDict
from .PawsPlugin import PawsPlugin
import datetime
import copy
import time
from threading import Condition

import tzlocal
import numpy as np

inputs = OrderedDict(
    dt=1.,
    t_max=None,
    verbose=False)

class Timer(PawsPlugin):
    """A Paws plugin for marking the passage of time"""

    def __init__(self):
        super(Timer,self).__init__(inputs)
        self.input_doc['dt'] = 'Wait time between signals, in seconds'
        self.input_doc['t_max'] = 'Time in seconds after which the timer stops'
        # A lock for the "tick" trigger 
        self.dt_lock = Condition()
        self.t0 = None 
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        self.t0_utc = None 
        self.thread_blocking = True

    def start(self):
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        self.t0 = datetime.datetime.now(self.tz)
        self.t0_utc = (self.t0-self.ep).total_seconds()
        self.run_clone() 

    def run(self):
        # self.thread_clone runs this method in its own thread.
        vb = self.inputs['verbose']
        if vb: self.message_callback('timer STARTED')
        with self.proxy.dt_lock:
            dt = self.inputs['dt'] 
            t_max = self.inputs['t_max']
            keep_going = True
            # set zero-time point 
            self.t0 = copy.deepcopy(self.proxy.t0)
            self.t0_utc = copy.deepcopy(self.proxy.t0_utc)
            dt_now = self.dt_utc()
            self.proxy.dt_notify()
            #dt_err = np.mod(dt_now,dt)
        while dt_now < t_max and keep_going:
            if vb: self.message_callback('tick: {}/{}'.format(dt_now,t_max))
            # attempt to nail the next dt point:
            t_rem = dt-np.mod(self.dt_utc(),dt)
            #time.sleep(t_rem-dt_err)
            time.sleep(t_rem)
            # acquire proxy dt lock, take time point, dt_notify, release
            with self.proxy.dt_lock:
                dt_now = self.dt_utc()
                self.proxy.dt_notify()
            #dt_err = np.mod(dt_now,dt)
            # TODO: implement feedback to hone the timer
            # acquire proxy running_lock, check if we are still running
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
                if vb and not keep_going: self.message_callback('timer STOPPED')
        with self.proxy.running_lock:
            self.proxy.stop()
        # now that the plugin is stopped, notify any other plugins that are waiting on dt_lock
        with self.proxy.dt_lock:
            self.proxy.dt_notify()
        if vb: self.message_callback('Timer FINISHED')

    def dt_notify(self):
        if int(self.py_version) == 2:
            self.dt_lock.notifyAll()
        else:
            self.dt_lock.notify_all()

    def dt_utc(self):
        t = datetime.datetime.now(self.tz)
        return float((t-self.ep).total_seconds()-self.t0_utc)

    def description(self):
        desc = str('Timer Plugin for Paws: '\
            'Signals the passage of time, '\
            'as a convenience for other plugins '\
            'who depend on a clock to trigger their actions')
        return desc


