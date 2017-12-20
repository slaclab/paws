from collections import OrderedDict

import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_fit 

inputs=OrderedDict(uid=None,q_I=None)
outputs=OrderedDict(pif=None)

class Pif1dScatteringIntensity(Operation):
    """Build a simple pypif.obj.ChemicalSystem containing the scattering intensity."""

    def __init__(self):
        super(Pif1dScatteringIntensity,self).__init__(inputs,outputs)
        self.input_doc['uid'] = 'PIF uid (string)'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding scattering intensities'
        self.output_doc['pif'] = 'pif object representing the input data'

    def run(self):
        uid = self.inputs['uid']
        q_I = self.inputs['q_I']

        csys = pifobj.ChemicalSystem()
        csys.uid = uid
        csys.properties = []
        csys.tags = ['unlabeled scattering intensity']

        # Pack q_I into a property
        pI = self.q_I_property(q_I)
        pI.name = 'SAXS intensity' 
        csys.properties.append(pI)
        self.outputs['pif'] = csys

    def q_I_property(self,q_I):
        pI = pifobj.Property()
        n_qpoints = q_I.shape[0]
        pI.scalars = [pifobj.Scalar(q_I[i,1]) for i in range(n_qpoints)]
        pI.units = 'counts'
        pI.conditions = []
        pI.conditions.append( pifobj.Value('scattering vector', 
                            [pifobj.Scalar(q_I[i,0]) for i in range(n_qpoints)],
                            None,None,None,'1/Angstrom') )
        return pI 
        
