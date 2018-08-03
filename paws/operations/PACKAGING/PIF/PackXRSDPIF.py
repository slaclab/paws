from collections import OrderedDict

from ...Operation import Operation

from xrsdkit.tools import piftools

inputs=OrderedDict(
    experiment_id=None,
    t_utc=None,
    temperature=None,
    source_wavelength=None,
    q_I=None,
    populations={},
    fixed_params={},
    param_bounds={},
    param_constraints={})
outputs=OrderedDict(pif=None)

class PackXRSDPIF(Operation):
    """Build a PIF record for a XRSD pattern"""

    def __init__(self):
        super(PackXRSDPIF,self).__init__(inputs,outputs)
        self.input_doc['experiment_id'] = 'string experiment id, used as a pif ID attribute'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['source_wavelength'] = 'light source wavelength in Angstroms'
        self.input_doc['q_I'] = 'n-by-2 array of scattering data, intensity (arb) versus q (1/A)'
        self.input_doc['populations'] = 'scattering populations data (dict)'
        self.input_doc['fixed_params'] = 'scattering populations fixed params'
        self.input_doc['param_bounds'] = 'scattering populations param bounds'
        self.input_doc['param_constraints'] = 'scattering populations param constraints'
        self.output_doc['pif'] = 'pif object representing the input data'

    def run(self):
        expt_id = self.inputs['experiment_id']
        t_utc = self.inputs['t_utc']
        temp_C = self.inputs['temperature']
        src_wl = self.inputs['source_wavelength']
        pops = self.inputs['populations']
        fp = self.inputs['fixed_params']
        pb = self.inputs['param_bounds']
        pc = self.inputs['param_constraints']
        q_I = self.inputs['q_I']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))

        csys = piftools.make_pif(uid_full,expt_id,t_utc,q_I,temp_C,src_wl,pops,fp,pb,pc)

        self.outputs['pif'] = csys

