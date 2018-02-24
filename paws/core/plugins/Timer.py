from __future__ import print_function
from collections import OrderedDict
from .PawsPlugin import PawsPlugin
import datetime
import time
import sys
from threading import Condition

import tzlocal
import numpy as np

inputs = OrderedDict(dt=1.,t_max=None)

class Timer(PawsPlugin):
    """A Paws plugin for marking the passage of time"""

    def __init__(self):
        super(Timer,self).__init__(inputs)
        self.input_doc['dt'] = 'Wait time between signals, in seconds'
        self.input_doc['t_max'] = 'Time in seconds after which the timer stops'
        #self.clock = Event()
        self.tz = tzlocal.get_localzone()
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        self.dt_lock = Condition()
        #self.dt_lock.acquire()
        self.t0 = None 
        self.t0_utc = None 
        self.dt_now = 0.
        self.time_points = []
        self.content = OrderedDict(
            time_points=self.time_points)

    def start(self):
        self.dt = self.inputs['dt'] 
        self.t_max = self.inputs['t_max']
        # set zero-time point 
        self.t0 = datetime.datetime.now(self.tz)
        self.t0_utc = (self.t0-self.ep).total_seconds()
        # acquire lock, set initial time point, notify, release
        with self.dt_lock:
            self.dt_now = self.dt_utc()
            if int(sys.version[0]) == 2:
                self.dt_lock.notifyAll()
            else:
                self.dt_lock.notify_all()
            self.time_points.append(self.dt_now)
        self.running = True
        while self.running:
            # attempt to nail the next dt point:
            t_rem = self.dt-np.mod(self.dt_utc(),self.dt)
            time.sleep(t_rem)
            with self.dt_lock:
                self.dt_now = self.dt_utc()
                if int(sys.version[0]) == 2:
                    self.dt_lock.notifyAll()
                else:
                    self.dt_lock.notify_all()
                self.time_points.append(self.dt_now)
            if self.dt_now > self.t_max:
                self.running = False

    def dt_utc(self):
        t = datetime.datetime.now(self.tz)
        return (t-self.ep).total_seconds()-self.t0_utc

    def description(self):
        desc = str('Timer Plugin for Paws: '\
            'Signals the passage of time, '\
            'as a convenience for other plugins '\
            'who depend on a clock to trigger their actions')
        return desc


