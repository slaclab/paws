import datetime
import time
from threading import Thread, Condition

import tzlocal
import numpy as np

from .PawsPlugin import PawsPlugin

class Timer(PawsPlugin):
    """A Paws plugin for signaling the passage of time."""

    def __init__(self,dt=1.,t_max=float('inf'),verbose=False,log_file=None):
        """Create a Timer.

        Parameters
        ----------
        dt : float
            Time in seconds between ticks
            (each tick notifies self.dt_lock)
        t_max : float
            Time in seconds after which the timer stops itself
        """
        super(Timer,self).__init__(verbose=verbose,log_file=log_file)
        self.dt = dt
        self.t_max = t_max
        self.dt_lock = Condition()
        self.timer_thread = None 

    def start(self):
        super(Timer,self).start()

    def _run(self):
        self.tz = tzlocal.get_localzone()
        # self.ep: datetime object representing the epoch
        self.ep = datetime.datetime.fromtimestamp(0,self.tz)
        # self.t0: t0 as a datetime object
        self.t0 = datetime.datetime.now(self.tz)
        # self.t0_epoch: t0 in seconds since the epoch
        self.t0_epoch = (self.t0-self.ep).total_seconds()
        # launch a process that runs self.run_timer()
        self.timer_thread = Thread(target=self.run_timer)
        self.timer_thread.start()

    def run_timer(self):
        # notify self.dt_lock every self.dt seconds
        t_elapsed = self.get_elapsed_time()
        keep_going = True
        # initial tick notification:
        self.dt_notify()
        while t_elapsed < self.t_max and keep_going:
            if self.verbose: self.message_callback('timer: {}/{}'.format(t_elapsed,self.t_max))
            # attempt to nail the next dt point:
            t_rem = self.dt-np.mod(self.get_elapsed_time(),self.dt)
            time.sleep(t_rem)
            # tick notification
            self.dt_notify()
            # check if we are still running
            with self.running_lock:
                keep_going = bool(self.running)
                if self.verbose and not keep_going: self.message_callback('timer STOPPED')
        # if time ran out naturally, stop the timer 
        self.stop()
        # one final tick to mobilize any plugins 
        # that might have ended up waiting on dt_lock
        self.dt_notify()
        if self.verbose: self.message_callback('Timer FINISHED')

    def dt_notify(self):
        with self.dt_lock:
            if int(self.py_version) == 2:
                self.dt_lock.notifyAll()
            else:
                self.dt_lock.notify_all()

