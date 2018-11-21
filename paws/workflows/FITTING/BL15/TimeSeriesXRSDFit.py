import os
import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 

from paws.workflows.IO.BL15 import ReadTimeSeries
from paws.workflows.FITTING import XRSDFit

inputs = copy.deepcopy(ReadTimeSeries.inputs)
inputs.update(copy.deepcopy(XRSDFit.inputs))

outputs = copy.deepcopy(ReadTimeSeries.outputs)
outputs.update(copy.deepcopy(XRSDFit.outputs))
for k in XRSDFit.outputs.keys(): outputs[k] = []

class TimeSeriesXRSDFit(Workflow):

    def __init__(self):
        super(TimeSeriesXRSDFit,self).__init__(inputs,outputs)
        self.add_operation('read_timeseries',ReadTimeSeries.ReadTimeSeries())
        self.add_operation('fit',XRSDFit.XRSDFit())

    def run(self):
        read_inputs = OrderedDict([(k,self.inputs[k]) for k in ReadTimeSeries.inputs.keys()])
        self.operations['read_timeseries'].operations['read_batch'].operations['read'].disable_op('read_image')
        ts_data = self.operations['read_timeseries'].run_with(**read_inputs) 
        nb = len(ts_data['system_files'])
        self.message_callback('STARTING BATCH ({})'.format(nb))
        previous_sys = None
        for ib,outfile,q_I,sys in zip(range(nb),ts_data['system_files'],ts_data['q_I'],ts_data['system']):
            self.message_callback('RUNNING {} / {}'.format(ib+1,nb))
            if not sys:
                if previous_sys:
                    sys = previous_sys
                else:
                    sys = self.inputs['system']    
            fit_outputs = self.operations['fit'].run_with(
                system = sys,
                q_I = q_I,
                source_wavelength = self.inputs['source_wavelength'],
                error_weighted = self.inputs['error_weighted'],
                logI_weighted = self.inputs['logI_weighted'],
                q_range = self.inputs['q_range'],
                output_file = outfile
                )
            previous_sys = fit_outputs['system_opt']
