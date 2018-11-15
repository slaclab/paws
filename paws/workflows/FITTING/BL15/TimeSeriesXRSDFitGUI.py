import copy

from paws.workflows.FITTING.BL15 import TimeSeriesXRSDFit
from paws.workflows.FITTING import XRSDFitGUI

inputs = copy.deepcopy(TimeSeriesXRSDFit.inputs)
inputs.update(copy.deepcopy(XRSDFitGUI.inputs))

outputs = copy.deepcopy(TimeSeriesXRSDFit.outputs)
outputs.update(copy.deepcopy(XRSDFitGUI.outputs))
for k in XRSDFitGUI.outputs.keys(): outputs[k] = []

class TimeSeriesXRSDFitGUI(TimeSeriesXRSDFit.TimeSeriesXRSDFit):

    def __init__(self):
        super(TimeSeriesXRSDFitGUI,self).__init__()
        self.add_operation('fit',XRSDFitGUI.XRSDFitGUI())
        self.declare_inputs(inputs)
        self.declare_outputs(outputs)

