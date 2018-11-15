from .. import TimeSeriesXRSDFitGUI as TimeSeriesXRSDFitGUI_new
from ....IO.BL15.LEGACY.ReadTimeSeries import ReadTimeSeries 

class TimeSeriesXRSDFitGUI(TimeSeriesXRSDFitGUI_new.TimeSeriesXRSDFitGUI):

    def __init__(self):
        super(TimeSeriesXRSDFitGUI,self).__init__()
        self.add_operation('read_timeseries',ReadTimeSeries())

