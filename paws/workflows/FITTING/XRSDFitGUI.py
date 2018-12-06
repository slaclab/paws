import os

from paws.workflows.FITTING.XRSDFit import XRSDFit 
from paws.operations.PROCESSING.FITTING.XRSDFitGUI import XRSDFitGUI as XRSDFitGUI_op

class XRSDFitGUI(XRSDFit):

    def __init__(self):
        super(XRSDFitGUI,self).__init__()
        self.add_operations(fit = XRSDFitGUI_op())

