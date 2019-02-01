import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 

from paws.workflows.IO.BL15 import ReadTimeSeries

inputs = copy.deepcopy(ReadTimeSeries.inputs)
inputs.update(show_plots = False)

outputs = OrderedDict(figures = []) 

class PlotTimeSeries(Workflow):

    def __init__(self):
        super(PlotTimeSeries,self).__init__()
        self.add_operation('read',ReadTimeSeries())

    def run(self):
        self.outputs = copy.deepcopy(outputs)
        self.operations['read'].operations['read_batch'].operations['read'].disable_ops('read_image')
        read_inputs = dict([(k,self.inputs[k]) for k in ReadTimeSeries.inputs.keys()])
        read_outputs = self.operations['read'].run_with(**read_inputs)

        for q_I, dI, sys in zip(read_outputs['q_I'],read_outputs['dI'],read_outputs['system']):
            fig, I_comp = xrsdvis.plot_xrsd_fit(sys,q_I[:,0],q_I[:,1],dI=dI,show_plot=self.inputs['show_plots'])
            self.outputs['figures'].append(fig)
        return self.outputs
