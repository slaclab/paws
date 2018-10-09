from collections import OrderedDict

import numpy as np
import pypif.obj as pifobj
from xrsdkit.tools import piftools

from ...Operation import Operation

inputs=OrderedDict(
    recipe=None,
    experiment_id=None,
    t_T=None,
    t_params=None,
    t_systems=None,
    t_reports=None)
outputs=OrderedDict(pif=None)

class PackNPSynthPIF(Operation):
    """
    Analyze a series of PIFs generated in a nanoparticle synthesis experiment
    and produce a PIF that describes the overall experiment. 
    """

    def __init__(self):
        super(PackNPSynthPIF,self).__init__(inputs,outputs)
        self.input_doc['recipe'] = 'dict describing the synthesis recipe'
        self.input_doc['experiment_id'] = 'experiment id'
        self.input_doc['t_T'] = 'n-by-2 array, Temperature vs. time'
        self.input_doc['t_params'] = 'n-by-2 array, params vs. time'
        self.input_doc['t_systems'] = 'n-by-2 array, xrsdkit.system.System objects vs. time'
        self.input_doc['t_reports'] = 'n-by-2 array, fit reports vs. time'
        self.output_doc['pif'] = 'pypif.obj.ChemicalSystem object '\
            'describing the synthesis experiment'

    def run(self):
        rcp = self.inputs['recipe']
        expt_id = self.inputs['experiment_id']
        t_T = self.inputs['t_T']
        t_pars = self.inputs['t_params']
        t_sys = self.inputs['t_systems']
        t_rpts = self.inputs['t_reports']

        csys = pifobj.ChemicalSystem()
        csys.uid = expt_id 
        csys.ids = []
        csys.ids.append(piftools.id_tag('EXPERIMENT_ID',expt_id))
        
        if rcp:
            prep,comp = self.process_np_synth_recipe(rcp)
            csys.preparation = prep
            csys.composition = comp

        csys.properties = []

        if t_T is not None:
            csys.properties.append(
                self.property_vs_time(
                    'temperature',t_T,'seconds','degrees C'))

        if t_sys is not None:
            # TODO: process time-dependent system parameters
            pass

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

