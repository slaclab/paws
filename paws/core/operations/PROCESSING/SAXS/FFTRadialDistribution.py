import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_math 

inputs = OrderedDict(q_I=None)
outputs = OrderedDict(
    r_gofr=None,
    r_max=None)

class FFTRadialDistribution(Operation):
    """Obtain the radial distribution function from a SAXS pattern via FFT."""

    def __init__(self):
        super(FFTRadialDistribution, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q (1/Angstrom) versus I.'
        self.output_doc['r_gofr'] = 'n-by-2 array of r (Angstrom) versus g(r).'
        self.output_doc['r_max'] = 'the integral from zero to r_max of g(r) '\
                            'is 0.99 times the full integral of g(r)'

    def run(self):
        q_I = self.inputs['q_I']
        r_gofr,r_max = saxs_math.g_of_r(q_I)
        self.outputs['r_gofr'] = r_gofr
        self.outputs['r_max'] = r_max

