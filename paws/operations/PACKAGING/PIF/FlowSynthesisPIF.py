from collections import OrderedDict

from ...Operation import Operation
import pypif.obj as pifobj

from xrsdkit.tools import piftools

inputs=OrderedDict(
    experiment_id=None,
    t_utc=None,
    recipe=None,
    q_I=None,
    source_wavelength=None,
    populations=None)
outputs=OrderedDict(pif=None)

class FlowSynthesisPIF(Operation):
    """Build a PIF record for a flow reactor synthesis experiment"""

    def __init__(self):
        super(FlowSynthesisPIF,self).__init__(inputs,outputs)
        self.input_doc['experiment_id'] = 'string experiment id '\
            '(pif uid = experiment_id+"_"+t_utc)'
        self.input_doc['t_utc'] = 'acquisition time in seconds utc'
        self.input_doc['recipe'] = 'dict describing flow reactor settings'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities'
        self.input_doc['source_wavelength'] = 'lightsource wavelength, in Angstroms'
        self.input_doc['populations'] = 'dict describing scatterer populations'
        self.output_doc['pif'] = 'pif object representing the synthesis experiment'

    def run(self):
        expt_id = self.inputs['experiment_id']
        t_utc = self.inputs['t_utc']
        pops = self.inputs['populations']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        q_I = self.inputs['q_I']
        src_wl = self.inputs['source_wavelength']
        rcp = self.inputs['recipe']
        T_set = rcp.pop('T_set') 
        csys = piftools.make_pif(uid_full,expt_id,t_utc,q_I,T_set,src_wl,pops)
        csys.properties.append(piftools.scalar_property(
            'T_set',T_set,'temperature setpoint','EXPERIMENTAL','degrees C'))
        for rg_name,flowrate in rcp.items():
            rgfp = piftools.scalar_property(
                rg_name+'_flowrate',flowrate,'flowrate setpoint','EXPERIMENTAL','microlitres per minute')
            csys.properties.append(rgfp)

        self.outputs['pif'] = csys

