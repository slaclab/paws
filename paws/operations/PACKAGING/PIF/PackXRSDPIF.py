from collections import OrderedDict

from ...Operation import Operation

from xrsdkit.tools import piftools
from xrsdkit.system import System

inputs=OrderedDict(
    system=None,
    q_I=None,
    experiment_id=None,
    t_utc=None,
    temperature=None,
    source_wavelength=None,
    )
outputs=OrderedDict(pif=None)

class PackXRSDPIF(Operation):
    """Build a PIF record for an xrsdkit System and its I(q) pattern"""

    def __init__(self):
        super(PackXRSDPIF,self).__init__(inputs,outputs)
        self.input_doc['system'] = 'xrsdkit.system.System object describing scattering material, '\
            'or a dict containing the System data, in which case the dict is used '\
            'to build the system by calling the xrsdkit.system.System constructor'
        self.input_doc['q_I'] = 'n-by-2 array of scattering data, intensity (arb) versus q (1/A)'
        self.input_doc['experiment_id'] = 'string experiment id, used as a pif ID attribute'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['source_wavelength'] = 'light source wavelength in Angstroms'
        self.output_doc['pif'] = 'pif object representing the input data'

    def run(self):
        sys = self.inputs['system']
        if isinstance(sys,dict):
            sys = System(sys)
        q_I = self.inputs['q_I']
        expt_id = self.inputs['experiment_id']
        t_utc = self.inputs['t_utc']
        temp_C = self.inputs['temperature']
        src_wl = self.inputs['source_wavelength']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        csys = piftools.make_pif(uid_full,sys,q_I,expt_id,t_utc,temp_C,src_wl)
        self.outputs['pif'] = csys
        return self.outputs

