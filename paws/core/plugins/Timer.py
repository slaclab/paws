from __future__ import print_function
from collections import OrderedDict
from .PawsPlugin import PawsPlugin
import datetime
import time
import sys
import os
from threading import Thread, Condition

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
        #self.clock = Event()
        # A lock for thread-safe run/stop:
        self.running_lock = Condition()
        # A lock for the "tick" trigger 
        self.dt_lock = Condition()
        self.time_points = []
        self.py_version = int(sys.version[0])
        self.thread_clone = None
        self.proxy = None
        self.t0 = None 
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        self.t0_utc = None 

    def start(self):
        with self.running_lock:
            self.running = True
        self.thread_clone = self.build_clone()
        self.thread_clone.proxy = self
        th = Thread(target=self.thread_clone.run)
        th.start()

    def run(self):
        # self.thread_clone runs this method in its own thread.
        vb = self.inputs['verbose']
        if vb: self.message_callback('timer STARTED')
        with self.proxy.dt_lock:
            dt = self.inputs['dt'] 
            t_max = self.inputs['t_max']
            keep_going = True
            # set zero-time point 
            self.t0 = datetime.datetime.now(self.tz)
            self.t0_utc = (self.t0-self.ep).total_seconds()
            dt_now = self.dt_utc()
            self.proxy.time_points.append(dt_now)
            self.proxy.notify()
            #dt_err = np.mod(dt_now,dt)
            # TODO: implement feedback to hone the timer
        while dt_now < t_max and keep_going:
            if vb: self.message_callback('tick: {}/{}'.format(dt_now,t_max))
            # attempt to nail the next dt point:
            t_rem = dt-np.mod(self.dt_utc(),dt)
            #time.sleep(t_rem-dt_err)
            time.sleep(t_rem)
            # acquire proxy dt lock, take time point, notify, release
            with self.proxy.dt_lock:
                dt_now = self.dt_utc()
                self.proxy.time_points.append(float(dt_now))
                self.proxy.notify()
            #dt_err = np.mod(dt_now,dt)
            # TODO: implement feedback to hone the timer
            # acquire proxy running_lock, check if we are still running
            with self.proxy.running_lock:
                keep_going = bool(self.proxy.running)
                if vb and not keep_going: self.message_callback('timer STOPPED')
        with self.proxy.running_lock:
            if vb: self.message_callback('timer FINISHED')
            self.proxy.stop()

    def notify(self):
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

    def get_plugin_content(self):
        return {'time_points':self.time_points}

