from collections import OrderedDict

from xrsdkit.tools import piftools

from ...Operation import Operation

inputs=OrderedDict(
    experiment_id=None,
    header_data=None,
    recipe=None,
    q_I=None,
    populations=None)
outputs=OrderedDict(
    pif=None,
    header_dir_path=None,
    header_filename=None)

class FlowSynthesisPIF(Operation):
    """Build a PIF record for a flow reactor synthesis experiment"""

    def __init__(self):
        super(FlowSynthesisPIF,self).__init__(inputs,outputs)
        self.input_doc['experiment_id'] = 'string experiment id '\
            '(pif uid = experiment_id+"_"+t_utc)'
        self.input_doc['header_data'] = 'dict of sample header data'
        self.input_doc['recipe'] = 'dict of sample recipe data'
        self.input_doc['q_I'] = 'n-by-2 array of q and intensity values'
        self.input_doc['populations'] = 'sample populations dict'
        self.output_doc['pif'] = 'pif object representing the synthesis experiment'

    def run(self):
        expt_id = self.inputs['experiment_id']
        hdr = self.inputs['header_data']
        rcp = self.inputs['recipe']
        q_I = self.inputs['q_I']
        pops = self.inputs['populations']
        #self.message_callback('loading populations: {}'.format(popsf))
        #pops,fp,pb,pc,rpt = load_fit(popsf)
        # TODO: add fixed_params, param_bounds, param_constraints, after xrsdkit refac

        flow_hdr = hdr['flow_reactor_header']
        t_utc = flow_hdr['t_utc']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        src_wl = hdr['source_wavelength']
        #csys = piftools.make_pif(uid_full,expt_id,t_utc,q_I,None,src_wl,pops,fp,pb,pc)
        csys = piftools.make_pif(uid_full,expt_id,t_utc,q_I,None,src_wl,pops,{},{},{})

        csys.properties.append(piftools.scalar_property(
            'T_set',rcp['T_set'],'temperature setpoint','EXPERIMENTAL','degrees C'))
        csys.properties.append(piftools.scalar_property(
            'flowrate',rcp['flowrate'],'total flowrate','EXPERIMENTAL','microlitres per minute'))
        solv_frac = 1.
        for rg_name,frac in rcp['reagent_volume_fractions'].items():
            csys.properties.append(piftools.scalar_property(
                rg_name+'_fraction',frac,'{} volume fraction'.format(rg_name),'EXPERIMENTAL'))
            solv_frac -= frac
        csys.properties.append(piftools.scalar_property(
            rcp['solvent']+'_solvent_fraction',solv_frac,'solvent volume fraction','EXPERIMENTAL'))

        self.outputs['pif'] = csys

