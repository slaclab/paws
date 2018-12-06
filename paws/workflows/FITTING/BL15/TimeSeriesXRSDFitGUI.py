import copy

from paws.workflows.FITTING.BL15 import TimeSeriesXRSDFit
from paws.workflows.FITTING import XRSDFitGUI

class TimeSeriesXRSDFitGUI(TimeSeriesXRSDFit.TimeSeriesXRSDFit):

    def __init__(self):
        super(TimeSeriesXRSDFitGUI,self).__init__()
        self.add_operation('fit',XRSDFitGUI.XRSDFitGUI())

