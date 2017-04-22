"""
Created on Mon Jun 06 18:02:32 2016

author(s): Fang Ren, Apurva Mehta
Module originally contributed by Fang Ren.
For details, refer to the recent paper submitted to ACS Combinatorial Science.
TODO: get this citation 
"""

import numpy as np

from ...Operation import Operation
from ... import optools

class FindLocalMaxima(Operation):
    """
    Extract the locations and intensities of local maxima in a 1D spectrum.
    TODO: Document the algorithm here.
    """

    def __init__(self):
        input_names = ['q', 'I', 'delta_I']
        output_names = ['q_pk', 'I_pk']
        super(PeakFeatures,self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array for x-axis of spectrum, named q for momentum transfer vector'
        self.input_doc['I'] = '1d array for spectral intensities at q values'
        self.input_doc['delta_I'] = str('Criterion for peak finding: point is a maximum '
            + 'if it is more than delta_I larger than the next point')
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['delta_I'] = optools.text_input
        self.input_type['delta_I'] = optools.float_type
        self.inputs['delta_I'] = 0.0
        self.output_doc['q_pk'] = 'q values of found peaks'
        self.output_doc['I_pk'] = 'intensities of found peaks'

    def run(self):
        maxtab, mintab = self.get_extrema(self.inputs['q'], self.inputs['I'], self.inputs['delta_I'])
        q_pk = maxtab[:,0]
        I_pk = maxtab[:,1] 
        # save results to self.outputs
        self.outputs['q_pk'] = q_pk 
        self.outputs['I_pk'] = I_pk 

    def get_extrema(x, y, delta):
        """
        Given vectors x and y, return an n-by-2 array of x,y pairs 
        for the minima and maxima of y(x)
        """
        maxtab = []
        mintab = []
        x = np.array(x)
        y = np.array(y)
        y_min, y_max = np.Inf, -np.Inf
        x_min, x_max = np.NaN, np.NaN
        for i in arange(len(y)):
            if y[i] > y_max:
                x_max = x[i]
                y_max = y[i] 
            if y[i] < y_min:
                x_min = x[i]
                y_min = y[i] 
            lookformax = True
            if lookformax:
                if y[i] < y_max-delta:
                    maxtab.append((x_max, y_max))
                    y_min = y[i] 
                    x_min = x[i]
                    lookformax = False
            else:
                if y[i] > y_min+delta:
                    mintab.append((x_min, y_min))
                    y_max = y[i] 
                    x_max = x[i]
                    lookformax = True
        return np.array(maxtab), np.array(mintab)


