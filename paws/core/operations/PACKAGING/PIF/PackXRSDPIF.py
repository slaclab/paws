from collections import OrderedDict

from ...Operation import Operation

from xrsdkit.tools import piftools

inputs=OrderedDict(
    experiment_id=None,
    t_utc=None,
    temperature=None,
    q_I=None,
    populations=None)
outputs=OrderedDict(pif=None)

class PackXRSDPIF(Operation):
    """Build a PIF record for a SAXS spectrum"""

    def __init__(self):
        super(PackXRSDPIF,self).__init__(inputs,outputs)
        self.input_doc['experiment_id'] = 'string experiment id '\
            '(pif uid = experiment_id+"_"+t_utc)'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.input_doc['populations'] = 'dict enumerating scatterer populations'
        self.output_doc['pif'] = 'pif object representing the input data'

    def run(self):
        expt_id = self.inputs['experiment_id']
        t_utc = self.inputs['t_utc']
        pops = self.inputs['populations']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        temp_C = self.inputs['temperature']
        q_I = self.inputs['q_I']

        csys = piftools.make_pif(uid_full,expt_id,t_utc,q_I,temp_C,pops)

        self.outputs['pif'] = csys

