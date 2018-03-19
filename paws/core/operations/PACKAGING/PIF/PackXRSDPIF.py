from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation

from saxskit import saxs_math, saxs_piftools

inputs=OrderedDict(
    experiment_id=None,
    t_utc=None,
    temperature=None,
    q_I=None,
    populations=None,
    params=None)
outputs=OrderedDict(pif=None)

class PifSAXS(Operation):
    """Build a PIF record for a SAXS spectrum"""
    # TODO: include the scattering equation in this record somehow

    def __init__(self):
        super(PifSAXS,self).__init__(inputs,outputs)
        self.input_doc['experiment_id'] = 'string experiment id '\
            '(pif uid = experiment_id+"_"+t_utc)'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.input_doc['populations'] = 'dict enumerating scatterer populations'
        self.input_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.output_doc['pif'] = 'pif object representing the input data'

    def run(self):
        expt_id = self.inputs['experiment_id']
        t_utc = self.inputs['t_utc']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        temp_C = self.inputs['temperature']
        q_I = self.inputs['q_I']

        all_pops = OrderedDict.fromkeys(saxs_math.population_keys)
        pops = self.inputs['populations']
        par = self.inputs['params']
        all_pops.update(pops)

        csys = saxs_piftools.make_pif(uid_full,expt_id,t_utc,q_I,temp_C,all_pops,par)

        self.outputs['pif'] = csys

