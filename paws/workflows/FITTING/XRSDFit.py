import os
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 
from paws.operations.IO.NumpyLoad import NumpyLoad 
from paws.operations.IO.YAML.LoadXRSDSystem import LoadXRSDSystem
from paws.operations.IO.YAML.SaveXRSDSystem import SaveXRSDSystem
from paws.operations.PROCESSING.FITTING.XRSDFit import XRSDFit as XRSDFit_op

inputs = OrderedDict(
    q_I_file = None,
    system_file = None,
    q_I = None,
    system = None,
    source_wavelength = None,
    error_weighted = True,
    logI_weighted = True,
    q_range = [0.,float('inf')], 
    output_file = None
    )

outputs = OrderedDict(
    system_opt = None,
    system_opt_dict = None,
    q_I_opt = None,
    fit_report = None
    )

class XRSDFit(Workflow):

    def __init__(self):
        super(XRSDFit,self).__init__(inputs,outputs)
        self.add_operations(
            read_q_I = NumpyLoad(),
            read_system = LoadXRSDSystem(),
            fit = XRSDFit_op(),
            save_system = SaveXRSDSystem()
        )

    def run(self):
        q_I = self.inputs['q_I']
        if self.inputs['q_I_file']:
            read_outputs = self.operations['read_q_I'].run_with(file_path=self.inputs['q_I_file'])
            q_I = read_outputs['data']
        sys = self.inputs['system']
        if self.inputs['system_file']:
            read_outputs = self.operations['read_system'].run_with(file_path=self.inputs['system_file'])
            sys = read_outputs['system']
        fit_outputs = self.operations['fit'].run_with(
            q_I = q_I,
            source_wavelength = self.inputs['source_wavelength'],
            system = sys,
            error_weighted = self.inputs['error_weighted'],
            logI_weighted = self.inputs['logI_weighted'],
            q_range = self.inputs['q_range']
            )
        self.outputs['system_opt'] = fit_outputs['system']
        self.outputs['system_opt_dict'] = fit_outputs['system_dict']
        self.outputs['q_I_opt'] = fit_outputs['q_I_opt']
        self.outputs['fit_report'] = fit_outputs['system'].fit_report
        if self.inputs['output_file']:
            self.operations['save_system'].run_with(
                system = fit_outputs['system'],
                file_path = self.inputs['output_file']
                )
        return self.outputs       
 
