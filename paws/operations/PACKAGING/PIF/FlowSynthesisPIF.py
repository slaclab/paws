from collections import OrderedDict
import os

import pypif.obj as pifobj
import yaml
import numpy as np
from xrsdkit.tools import piftools
from xrsdkit.system import load_from_yaml

from ...Operation import Operation

inputs=OrderedDict(
    experiment_id=None,
    t_utc=None,
    recipe={},
    header_data={},
    design_goals={},
    q_I=None,
    system=None)
outputs=OrderedDict(
    pif=None)

class FlowSynthesisPIF(Operation):
    """Build a PIF record for a flow reactor synthesis experiment"""

    def __init__(self):
        super(FlowSynthesisPIF,self).__init__(inputs,outputs)
        self.input_doc['experiment_id'] = 'string experiment id '\
            '(pif uid = experiment_id+"_"+t_utc)'
        self.input_doc['t_utc'] = 'timestamp in seconds UTC'
        self.input_doc['recipe'] = 'setpoints for the synthesis recipe'
        self.input_doc['header_data'] = 'FlowReactor header containing '\
            'readout values for recipe parameters'
        self.input_doc['design_goals'] = 'dict describing the recipe objectives'
        self.input_doc['q_I'] = 'n-by-2 array of scattering vectors and intensities'
        self.input_doc['system'] = 'xrsdkit.system.System describing '\
            'the populations and physical parameters of the material system'
        self.output_doc['pif'] = 'pif object representing the synthesis experiment'

    def run(self):
        expt_id = self.inputs['experiment_id']
        t_utc = self.inputs['t_utc']
        rcp_set = self.inputs['recipe']
        hdr = self.inputs['header_data']
        design_goals = self.inputs['design_goals']
        q_I = self.inputs['q_I']
        sys = self.inputs['system']
        src_wl = sys.fit_report['source_wavelength']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        T_read = hdr['T_read_A']

        csys = piftools.make_pif(uid_full,sys,q_I,expt_id,t_utc,T_read,src_wl)

        for nm,val in rcp_set.items():
            prop = pifobj.Property(nm,val)
            prop.tags = ['recipe setpoint']
            prop.dataType = 'EXPERIMENTAL'
            csys.properties.append(prop)

        for nm,val in hdr.items():
            prop = pifobj.Property(nm,val)
            prop.tags = ['flow reactor readout']
            prop.dataType = 'EXPERIMENTAL'
            csys.properties.append(prop)

        for prop_nm,val in design_goals.items():
            # TODO: formulate this property based on the type of goal at hand
            prop = pifobj.Property(prop_nm,val)
            prop.tags = ['design objective']
            prop.dataType = 'MACHINE_LEARNING'
            csys.properties.append(prop)

        self.outputs['pif'] = csys
        return self.outputs

