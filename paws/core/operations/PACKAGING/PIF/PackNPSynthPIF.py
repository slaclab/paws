from collections import OrderedDict

import numpy as np
import pypif.obj as pifobj
from saxskit import saxs_math, saxs_piftools

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(
    recipe=None,
    experiment_id=None,
    t_T=None,
    t_params=None,
    t_populations=None,
    t_reports=None)
outputs=OrderedDict(pif=None)

class PifNPSynthExperiment(Operation):
    """
    Analyze a series of PIFs generated in a nanoparticle synthesis experiment
    and produce a PIF that describes the overall experiment. 
    """

    def __init__(self):
        super(PifNPSynthExperiment,self).__init__(inputs,outputs)
        self.input_doc['recipe'] = 'dict describing the synthesis recipe'
        self.input_doc['experiment_id'] = 'experiment id'
        self.input_doc['t_T'] = 'n-by-2 array, Temperature vs. time'
        self.input_doc['t_params'] = 'n-by-2 array, saxs params vs. time'
        self.input_doc['t_populations'] = 'n-by-2 array, populations vs. time'
        self.input_doc['t_reports'] = 'n-by-2 array, fit reports vs. time'
        self.output_doc['pif'] = 'pypif.obj.ChemicalSystem object '\
            'describing the synthesis experiment'

    def run(self):
        rcp = self.inputs['recipe']
        expt_id = self.inputs['experiment_id']
        t_T = self.inputs['t_T']
        t_pars = self.inputs['t_params']
        t_pops = self.inputs['t_populations']
        t_rpts = self.inputs['t_reports']

        csys = pifobj.ChemicalSystem()
        csys.uid = expt_id 
        csys.ids = []
        csys.ids.append(saxs_piftools.id_tag('EXPERIMENT_ID',expt_id))
        
        if rcp:
            prep,comp = self.process_np_synth_recipe(rcp)
            csys.preparation = prep
            csys.composition = comp

        csys.properties = []

        if t_T is not None:
            csys.properties.append(
                self.property_vs_time(
                    'temperature',t_T,'seconds','degrees C'))

        if t_pars is not None:
            for pname in saxs_math.parameter_keys:
                nt = len(t_pars)
                # collect the time and parameter list for all times where pname is reported
                t = np.array([t_pars[it][0] for it in range(nt) if pname in t_pars[it][1].keys()])
                par = [t_pars[it][1][pname] for it in range(nt) if pname in t_pars[it][1].keys()]
                # count the instances of this parameter at each time point
                npar = np.array([len(pari) for pari in par])
                # TODO: this needs some additional work 
                # to ensure the continuity of parameter identities,
                # e.g., so that a given peak retains its identity
                # throughout the synthesis reaction
                for ipar in range(max(npar)):
                    # get all t points at which this parameter exists
                    tt = t[(npar>ipar)]
                    # harvest the parameter value at all of those t points
                    nt_pari = len(tt)
                    pari = [par[it][ipar] for it in range(nt_pari)]
                    t_pari = zip(list(tt),pari)
                    if any(t_pari):
                        property_name = saxs_piftools.parameter_description[pname]
                        if max(npar) > 1:
                            property_name = property_name + ' ({})'.format(ipar)
                        csys.properties.append(self.property_vs_time(
                        property_name,t_pari,'seconds',\
                        saxs_piftools.parameter_units[pname]))

        if t_rpts is not None:
            # fit obj vs. time
            nrpts = len(t_rpts)
            t_obj = [[t_rpts[it][0],t_rpts[it][1]['objective_value']] for
                it in range(nrpts) if 'objective_value' in t_rpts[it][1]]
            if any(t_obj):
                csys.properties.append(self.property_vs_time(
                    'spectrum fitting error',t_obj,'arb'))

        self.outputs['pif'] = csys

    def property_vs_time(self,name,t_param,t_units=None,param_units=None):
        pf = pifobj.Property()
        pf.name = name 
        npts = len(t_param) 
        pf.scalars = [pifobj.Scalar(t_param[i][1]) for i in range(npts)]
        if param_units:
            pf.units = param_units 
        pf.conditions = []
        pf.conditions.append( pifobj.Value('reaction time',
            [pifobj.Scalar(t_param[i][0]) for i in range(npts)],
            None,None,None,t_units) )
        return pf 

    def process_np_synth_recipe(self,rcp):
        return None,None

