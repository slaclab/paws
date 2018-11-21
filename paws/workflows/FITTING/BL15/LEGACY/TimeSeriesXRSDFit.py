from .. import TimeSeriesXRSDFit as TimeSeriesXRSDFit_new
from ....IO.BL15.LEGACY.ReadTimeSeries import ReadTimeSeries 

class TimeSeriesXRSDFit(TimeSeriesXRSDFit_new.TimeSeriesXRSDFit):

    def __init__(self):
        super(TimeSeriesXRSDFit,self).__init__()
        self.add_operation('read_timeseries',ReadTimeSeries())

