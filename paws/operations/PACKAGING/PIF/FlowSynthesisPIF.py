from collections import OrderedDict
import os

import pypif.obj as pifobj
import yaml
import numpy as np
from xrsdkit.tools import load_fit,piftools

from ...Operation import Operation

inputs=OrderedDict(
    experiment_id=None,
    header_file=None,
    recipe_file=None,
    q_I_file=None,
    populations_file=None)
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
        self.input_doc['header_file'] = 'path to sample header file'
        self.input_doc['recipe_file'] = 'path to sample recipe file'
        self.input_doc['q_I_file'] = 'path to scattering data file'
        self.input_doc['populations_file'] = 'path to population definitions file'
        self.output_doc['pif'] = 'pif object representing the synthesis experiment'

    def run(self):
        expt_id = self.inputs['experiment_id']
        hdrf = self.inputs['header_file']
        self.outputs['header_dir_path'],self.outputs['header_filename']  = os.path.split(hdrf)
        rcpf = self.inputs['recipe_file']
        q_If = self.inputs['q_I_file']
        popsf = self.inputs['populations_file']
        self.message_callback('loading header: {}'.format(hdrf))
        hdr = yaml.load(open(hdrf,'r'))
        self.message_callback('loading recipe: {}'.format(rcpf))
        rcp = yaml.load(open(rcpf,'r'))
        self.message_callback('loading scattering data: {}'.format(q_If))
        q_I = np.loadtxt(open(q_If,'r'))
        self.message_callback('loading populations: {}'.format(popsf))
        pops,fp,pb,pc,rpt = load_fit(popsf)

        flow_hdr = hdr['flow_reactor_header']
        t_utc = flow_hdr['t_utc']
        uid_full = 'tmp'
        if expt_id is not None:
            uid_full = expt_id 
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        src_wl = hdr['source_wavelength']
        csys = piftools.make_pif(uid_full,expt_id,t_utc,q_I,None,src_wl,pops,fp,pb,pc)
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

