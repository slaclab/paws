from collections import OrderedDict

from ...Operation import Operation

from xrsdkit.tools import piftools,load_fit

inputs=OrderedDict(
    experiment_id=None,
    t_utc=None,
    temperature=None,
    source_wavelength=None,
    q_I_file=None,
    populations_file=None)
outputs=OrderedDict(pif=None)

class PackXRSDPIF(Operation):
    """Build a PIF record for a XRSD pattern"""

    def __init__(self):
        super(PackXRSDPIF,self).__init__(inputs,outputs)
        self.input_doc['experiment_id'] = 'string experiment id, used as a pif ID attribute'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['source_wavelength'] = 'light source wavelength in Angstroms'
        self.input_doc['q_I_file'] = 'path to scattering data file'
        self.input_doc['populations_file'] = 'path to population definitions file'
        self.output_doc['pif'] = 'pif object representing the input data'

    def run(self):
        expt_id = self.inputs['experiment_id']
        t_utc = self.inputs['t_utc']
        temp_C = self.inputs['temperature']
        src_wl = self.inputs['source_wavelength']
        popsf = self.inputs['populations_file']
        q_If = self.inputs['q_I_file']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        self.message_callback('loading scattering data: {}'.format(q_If))
        q_I = np.loadtxt(open(q_If,'r'))
        self.message_callback('loading populations: {}'.format(popsf))
        pops,fp,pb,pc,rpt = load_fit(popsf)

        csys = piftools.make_pif(uid_full,expt_id,t_utc,q_I,temp_C,src_wl,pops)

        self.outputs['pif'] = csys

