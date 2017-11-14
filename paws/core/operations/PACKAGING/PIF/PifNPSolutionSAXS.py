from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_classify,saxs_fit,saxs_pif 

inputs=OrderedDict(
    uid_prefix=None,
    t_utc=None,
    temperature=None,
    q_I=None,
    flags=None,
    params=None,
    report=None)
outputs=OrderedDict(pif=None)

class PifNPSolutionSAXS(Operation):
    """Build a PIF record for a nanoparticle solution SAXS experiment"""
    # TODO: include the scattering equation in this record somehow

    def __init__(self):
        super(PifNPSolutionSAXS,self).__init__(inputs,outputs)
        self.input_doc['uid_prefix'] = 'string for pif uid prefix '\
            '(pif uid = uid_prefix+t_utc), and also the '
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.input_doc['flags'] = 'dict of boolean flags indicating scatterer populations'
        self.input_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.input_doc['report'] = 'dict reporting key results '\
            'for the SAXS processing workflow, including fitting objectives, etc.'
        self.output_doc['pif'] = 'pif object representing the input data'
        self.input_type['t_utc'] = opmod.workflow_item
        self.input_type['temperature'] = opmod.workflow_item
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.input_type['params'] = opmod.workflow_item
        self.input_type['report'] = opmod.workflow_item

    def run(self):
        uid_pre = self.inputs['uid_prefix']
        t_utc = self.inputs['t_utc']
        uid_full = 'tmp'
        if uid_pre is not None:
            uid_full = uid_pre
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        temp_C = self.inputs['temperature']
        q_I = self.inputs['q_I']

        flg = self.inputs['flags']
        par = self.inputs['params']
        rpt = self.inputs['report']

        csys = saxs_pif.make_pif(uid_full,expt_id,t_utc,q_I,temp_C,flg,par,rpt)

        self.outputs['pif'] = csys

