from collections import OrderedDict

import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(pifs=None,recipe_file=None,reaction_id=None)
outputs=OrderedDict(master_pif=None)

class PifNPSynthExperiment(Operation):
    """
    Analyze a series of PIFs generated in a nanoparticle synthesis experiment
    and produce a master PIF that describes the overall experiment. 
    """

    def __init__(self):
        super(PifNPSynthExperiment,self).__init__(inputs,outputs)
        self.input_doc['pifs'] = 'list of pypif.obj.ChemicalSystem objects '\
            'describing a full nanoparticle synthesis experiment. '
        self.input_doc['recipe_file'] = 'path to a YAML file '\
            'describing the synthesis recipe with a set of standard keys (TODO: document). '
        self.input_doc['reaction_id'] = 'string identifying the reaction: '\
            'because this is used as the ChemicalSystem.uid, it must be unique '\
            'among the uids in the data set where the PIF will be stored.'
        self.output_doc['master_pif'] = 'pypif.obj.ChemicalSystem object '\
            'describing the overall experiment. '

    def run(self):
        pifs = self.inputs['pifs']
        rcpfile = self.inputs['recipe_file']
        rxnid = self.inputs['reaction_id']
        csys = pifobj.ChemicalSystem()
        csys.uid = rxnid 

    def time_feature_property(self,t_f,fname,funits=''):
        pf = pifobj.Property()
        pf.name = fname 
        npts = t_f.shape[0]
        pf.scalars = [pifobj.Scalar(t_f[i,1]) for i in range(npts)]
        if funits:
            pf.units = funits 
        pf.conditions = []
        pf.conditions.append( pifobj.Value('reaction time',
                        [pifobj.Scalar(t_f[i,0]) for i in range(npts)],
                        None,None,None,'seconds') )
        return pf 



