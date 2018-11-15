from ....IO.BL15.LEGACY.ReadTimeSeries import ReadTimeSeries 
from .. import PlotTimeSeries as PlotTimeSeries_new

class PlotTimeSeries(PlotTimeSeries_new.PlotTimeSeries):
    
    def __init__(self):
        super(PlotTimeSeries,self).__init__()
        # replace reader with LEGACY reader
        self.add_operation('read',ReadTimeSeries())



