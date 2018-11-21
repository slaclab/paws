import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 

from paws.workflows.IO.BL15 import ReadTimeSeries
from paws.operations.VISUALIZATION.XRSDPlot import SortBatch

inputs = copy.deepcopy(ReadTimeSeries.inputs)
inputs.update(
    source_wavelength = None,
    show_plots = False
    )

outputs = OrderedDict(
    figures = [] 
    ) 

class PlotTimeSeries(Workflow):

    def __init__(self):
        self.add_operations(
            read = ReadTimeSeries.ReadTimeSeries(),
            plot = XRSDPlot()
            )

    def run(self):
        self.outputs = copy.deepcopy(outputs)
        self.operations['read'].operations['read_batch'].operations['read'].disable_ops('read_image')
        read_inputs = OrderedDict([(k,self.inputs[k]) for k in ReadTimeSeries.inputs.keys()])
        read_outputs = self.operations['read'].run_with(**read_inputs)

        for q_I, dI, sys in zip(read_outputs['q_I'],read_outputs['dI'],read_outputs['system']):
            plot_outputs = self.operations['plot'].run_with(
                q_I = q_I,
                source_wavelength = self.inputs['source_wavelength'],
                dI = dI,
                system = sys,
                show_plot = self.inputs['show_plots']
            )
            self.outputs['figures'].append(plot_outputs['figure'])
        return self.outputs

