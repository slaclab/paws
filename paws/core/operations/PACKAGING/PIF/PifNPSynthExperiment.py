from collections import OrderedDict

import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(
    recipe=None,
    experiment_id=None,
    t_T=None,
    t_params=None,
    t_flags=None,
    t_reports=None)
outputs=OrderedDict(pif=None)

class PifNPSynthExperiment(Operation):
    """
    Analyze a series of PIFs generated in a nanoparticle synthesis experiment
    and produce a PIF that describes the overall experiment. 
    """

    def __init__(self):
        super(PifNPSynthExperiment,self).__init__(inputs,outputs)
        self.input_doc['recipe'] = 'dict describing '\
            'the synthesis recipe'
        self.input_doc['experiment_id'] = 'experiment id, '\
            'used as uid for output pif'
        self.output_doc['pif'] = 'pypif.obj.ChemicalSystem object '\
            'describing the synthesis experiment'

    def process_np_synth_recipe(self,rcp):
        return None,None

    def run(self):
        rcp = self.inputs['recipe']
        expt_id = self.inputs['experiment_id']
        t_T = self.inputs['t_T']
        t_pars = self.inputs['t_params']
        t_flgs = self.inputs['t_flags']
        t_rpts = self.inputs['t_reports']

        csys = pifobj.ChemicalSystem()
        csys.uid = expt_id 
        csys.ids = []
        csys.ids.append(saxs_models.id_tag('EXPERIMENT_ID',expt_id))
        
        if rcp:
            prep,comp = self.process_np_synth_recipe(rcp)
            csys.preparation = prep
            csys.composition = comp

        csys.properties = []
        if t_T is not None:
            csys.properties.append(saxs_models.time_feature_property('temperature vs. time',t_T,'seconds','degrees C'))
        if t_pars is not None:
            # I0_floor vs. time
            t_I0floor = np.array([[t_pars[it,0],t_pars[it,1]['I0_floor']] for
                it in range(t_pars.shape[0]) if 'I0_floor' in t_pars[it,1]])
            if t_I0floor.any():
                csys.properties.append(saxs_models.time_feature_property(
                    'I0_floor vs. time',t_I0floor,'seconds','arb'))
            # G_precursor vs. time
            t_Gpre = np.array([[t_pars[it,0],t_pars[it,1]['G_precursor']] for
                it in range(t_pars.shape[0]) if 'G_precursor' in t_pars[it,1]])
            if t_Gpre.any():
                csys.properties.append(saxs_models.time_feature_property(
                    'Precursor guinier factor vs. time',t_Gpre,'seconds','arb'))
            # rg_precursor vs. time
            t_rgpre = np.array([[t_pars[it,0],t_pars[it,1]['rg_precursor']] for
                it in range(t_pars.shape[0]) if 'rg_precursor' in t_pars[it,1]])
            if t_rgpre.any():
                csys.properties.append(saxs_models.time_feature_property(
                    'Precursor radius of gyration vs. time',t_rgpre,'seconds','Angstroms'))
            # I0_sphere vs. time
            t_I0sph = np.array([[t_pars[it,0],t_pars[it,1]['I0_sphere']] for
                it in range(t_pars.shape[0]) if 'I0_sphere' in t_pars[it,1]])
            if t_I0sph.any():
                csys.properties.append(saxs_models.time_feature_property(
                    'Spherical scatterer intensity vs. time',t_I0sph,'seconds','arb'))
            # r0_sphere vs. time
            t_r0sph = np.array([[t_pars[it,0],t_pars[it,1]['r0_sphere']] for
                it in range(t_pars.shape[0]) if 'r0_sphere' in t_pars[it,1]])
            if t_r0sph.any():
                csys.properties.append(saxs_models.time_feature_property(
                    'Spherical scatterer mean radius vs. time',t_r0sph,'seconds','Angstroms'))
            # sigma_sphere vs. time
            t_sigsph = np.array([[t_pars[it,0],t_pars[it,1]['sigma_sphere']] for
                it in range(t_pars.shape[0]) if 'sigma_sphere' in t_pars[it,1]])
            if t_sigsph.any():
                csys.properties.append(saxs_models.time_feature_property(
                    'Spherical scatterer fractional polydispersity vs. time',t_sigsph,'seconds'))

        if t_rpts is not None:
            # fit obj vs. time
            t_obj = np.array([[t_rpts[it,0],t_rpts[it,1]['objective_value']] for
                it in range(t_rpts.shape[0]) if 'objective_value' in t_rpts[it,1]])
            if t_obj.any():
                csys.properties.append(saxs_models.time_feature_property(
                    'Spectrum fitting error vs. time',t_obj,'arb'))

        self.outputs['pif'] = csys

