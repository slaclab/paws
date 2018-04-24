from collections import OrderedDict

from ..Operation import Operation

from xrsdkit.tools.piftools import unpack_old_pif, make_pif 

inputs=OrderedDict(
    pif=None,
    flag=True)
outputs=OrderedDict(pif=None)

class PIFRefactor(Operation):
    """Build a new PIF from an old PIF"""

    def __init__(self):
        super(PIFRefactor,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'old pif object'
        self.output_doc['pif'] = 'new pif object'

    def run(self):
        if self.inputs['flag']:
            p = self.inputs['pif']
            expt_id, t_utc, q_I, T_C, feats, pops, params, rpt = unpack_old_pif(p)

            new_pops = {} 
            if bool(pops['unidentified']):
                new_pops['anonymous']=dict(structure='unidentified')
            else:
                if bool(pops['diffraction_peaks']): 
                    new_pops['superlattice']=dict(
                        structure='fcc',
                        settings={},
                        parameters={},
                        basis={})
                    new_pops['noise']=dict(
                        structure='diffuse',
                        parameters={},
                        basis={})
                    if bool(pops['guinier_porod']):
                        new_pops['precursor']=dict(
                            structure='diffuse',
                            parameters={},  
                            basis={'guinier_porod_precursor':{'guinier_porod':{}}}
                            )
                    if bool(pops['spherical_normal']):
                        new_pops['nanoparticles']=dict(
                            structure='diffuse',
                            parameters={},  
                            basis={'spherical_normal_nanoparticles':{'spherical_normal':{}}} 
                            )
                else:
                    new_pops['noise']=dict(
                        structure='diffuse',
                        parameters={'I0':params['I0_floor']},
                        basis={'flat_noise':dict(
                            flat={'amplitude':1}
                            )}
                        )
                    if bool(pops['guinier_porod']):
                        new_pops['precursor']=dict(
                            structure='diffuse',
                            parameters={'I0':1},
                            basis={'guinier_porod_precursor':dict(
                                guinier_porod={'G':params['G_gp'],'r_g':params['rg_gp'],'D':params['D_gp']}
                                )}
                            )
                    if bool(pops['spherical_normal']):
                        new_pops['nanoparticles']=dict(
                            structure='diffuse',
                            parameters={'I0':params['I0_sphere']},
                            basis={'spherical_nanoparticles':dict(
                                spherical_normal={'r0':params['r0_sphere'],'sigma':params['sigma_sphere']}
                                )}
                            )
    
            csys = make_pif(str(expt_id)+'_'+str(int(t_utc)),expt_id,t_utc,q_I,T_C,new_pops)
            self.outputs['pif'] = csys

