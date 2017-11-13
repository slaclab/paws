from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(pif=None)
outputs=OrderedDict(
    q_I=None,
    temperature=None,
    flags=None,
    params=None,
    report=None)

class UnpackNPSolutionSAXS(Operation):
    """Unpack a nanoparticle solution SAXS record"""

    def __init__(self):
        super(UnpackNPSolutionSAXS,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'pif object to be unpacked'
        self.output_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.output_doc['temperature'] = 'temperature in degrees C'
        self.output_doc['flags'] = 'dict of boolean flags indicating scatterer populations'
        self.output_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.output_doc['report'] = 'dict reporting fit objectives, etc. '
        self.input_type['pif'] = opmod.workflow_item

    def run(self):
        p = self.inputs['pif']
        
        f = OrderedDict() 
        par = OrderedDict() 
        r = OrderedDict() 
        for prop in p.properties:
            print(prop.name)
            if prop.name == 'SAXS intensity':
                I = [float(sca.value) for sca in prop.scalars]
                for val in prop.conditions:
                    if val.name == 'scattering vector':
                        q = [float(sca.value) for sca in val.scalars]
                    if val.name == 'temperature':
                        temp = float(val.scalars[0].value)
                        self.outputs['temperature'] = temp 
                q_I = np.array(zip(q,I)).T
                self.outputs['q_I'] = q_I
            elif prop.name[-5:] == '_flag' and prop.data_type == 'EXPERIMENTAL':
                f[prop.name[:-5]] = bool(prop.scalars[0].value)
            elif prop.name in ['I0_sphere','r0_sphere','sigma_sphere',\
                            'G_precursor','rg_precursor',\
                            'I0_floor']:
                par[prop.name] = float(prop.scalars[0].value)
            elif prop.tags is not None:
                if 'spectrum fitting quantity' in prop.tags:
                    r[prop.name] = float(prop.scalars[0].value)

        self.outputs['flags'] = f
        self.outputs['params'] = par
        self.outputs['report'] = r

        import pdb; pdb.set_trace()
