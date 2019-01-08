from collections import OrderedDict
import os

import pypif.obj as pifobj
import yaml
import numpy as np
from xrsdkit.tools import piftools

from ...Operation import Operation

inputs=OrderedDict(
    recipe_data={},
    q_I=None,
    system=None,
    additional_properties={}
    )
outputs=OrderedDict(pif=None)

class FlowSynthesisPIF(Operation):
    """Build a PIF record for a flow reactor synthesis experiment"""

    def __init__(self):
        super(FlowSynthesisPIF,self).__init__(inputs,outputs)
        self.input_doc['recipe_data'] = 'Header containing recipe data'
        self.input_doc['q_I'] = 'n-by-2 array of scattering vectors and intensities'
        self.input_doc['system'] = 'xrsdkit.system.System describing '\
            'the populations and physical parameters of the material system'
        self.input_doc['additional_properties'] = 'dict of additional properties '\
            'to add to the PIF (each key is a property name, each value is a value)'
        self.output_doc['pif'] = 'pif object representing the synthesis experiment'

    def run(self):
        rcp = self.inputs['recipe_data']
        q_I = self.inputs['q_I']
        sys = self.inputs['system']
        uid = sys.sample_metadata['sample_id']
        if not uid:
            uid = 'tmp'
            if sys.sample_metadata['experiment_id']:
                uid = expt_id 
            if sys.sample_metadata['t_utc']:
                uid = uid+'_'+str(int(t_utc))

        self.message_callback('building PIF (sample_id: {})'.format(sys.sample_metadata['sample_id']))
        csys = piftools.make_pif(sys,q_I)

        for nm,val in rcp.items():
            prop = pifobj.Property(nm,val)
            prop.tags = ['flow reactor recipe data']
            prop.dataType = 'EXPERIMENTAL'
            csys.properties.append(prop)

        for nm,val in self.inputs['additional_properties'].items():
            prop = pifobj.Property(nm,val)
            csys.properties.append(prop)

        self.outputs['pif'] = csys
        return self.outputs

