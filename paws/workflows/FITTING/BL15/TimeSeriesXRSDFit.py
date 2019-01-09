import os
import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 

from paws.workflows.IO.BL15 import ReadTimeSeries
from paws.workflows.FITTING import XRSDFit

inputs = copy.deepcopy(ReadTimeSeries.inputs)
inputs.update(copy.deepcopy(XRSDFit.inputs))
inputs.update({'experiment_id':None})

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
        for ib,outfile,q_I,sys,hdr,q_I_file in zip(range(nb),
        ts_data['system_files'],ts_data['q_I'],ts_data['system'],
        ts_data['header_data'],ts_data['q_I_files']):
            self.message_callback('RUNNING {} / {}'.format(ib+1,nb))
            if not sys:
                if previous_sys:
                    sys = previous_sys
                else:
                    sys = self.inputs['system']
            samp_id = None
            if self.inputs['experiment_id'] and hdr:
                if 't_utc' in hdr:
                    samp_id = str(self.inputs['experiment_id'])+'_'+str(int(hdr['t_utc']))
            data_fp = None
            if q_I_file: data_fp = os.path.split(q_I_file)[1]
            fit_outputs = self.operations['fit'].run_with(
                system = sys,
                q_I = q_I,
                error_weighted = self.inputs['error_weighted'],
                logI_weighted = self.inputs['logI_weighted'],
                q_range = self.inputs['q_range'],
                output_file = outfile,
                experiment_id = self.inputs['experiment_id'],
                sample_id = samp_id, 
                data_file_path = data_fp 
                )
            previous_sys = fit_outputs['system_opt']
        return self.outputs
