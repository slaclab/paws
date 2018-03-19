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

            new_pops = [] 
            if bool(pops['unidentified']):
                new_pops.append(dict(structure='unidentified'))
            else:
                if bool(pops['diffraction_peaks']): 
                    new_pops.append(dict(
                        name='superlattice',
                        structure='fcc'))
                        #basis={(0,0,0):dict(
                        #    spherical={'r':params['r0_sphere']}
                        #    )}
                        #))
                else:
                    new_pops.append(dict(
                        name='noise',
                        structure='diffuse',
                        basis={(0,0,0):dict(
                            flat={'amplitude':params['I0_floor']}
                            )}
                        ))
                    if bool(pops['guinier_porod']):
                        new_pops.append(dict(
                            name='precursor',
                            structure='diffuse',
                            parameters={'N':1},
                            basis={(0,0,0):dict(
                                guinier_porod={'G':params['G_gp'],'rg':params['rg_gp'],'D':params['D_gp']}
                                )}
                            ))
                    if bool(pops['spherical_normal']):
                        new_pops.append(dict(
                            name='nanoparticle',
                            structure='diffuse',
                            parameters={'N':params['I0_sphere']},
                            basis={(0,0,0):dict(
                                spherical_normal={'r0':params['r0_sphere'],'sigma':params['sigma_sphere']}
                                )}
                            ))
    
            csys = make_pif(str(expt_id)+'_'+str(int(t_utc)),expt_id,t_utc,q_I,T_C,new_pops)
            self.outputs['pif'] = csys

