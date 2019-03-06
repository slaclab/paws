from collections import OrderedDict

import numpy as np

from ..Operation import Operation

inputs = OrderedDict(
    x=None,
    y=None,
    dy=None,
    order=None,
    base=None)
outputs = OrderedDict(smoothed_data=None)

class SavitzkyGolay(Operation):
    """Applies a Savitzky-Golay polynomial smoothing filter to a 1d array."""

    def __init__(self):
        super(SavitzkyGolay, self).__init__(inputs, outputs)
        self.input_doc['x'] = '1d array- independent variable'
        self.input_doc['y'] = '1d array- dependent variable, same shape as x'
        self.input_doc['dy'] = '1d array, error estimate in y, same shape as y (default None)'
        self.input_doc['order'] = 'integer order of polynomial approximation (zero to five)'
        self.input_doc['base'] = '-1, 0, or positive integer'
        self.output_doc['smoothed_data'] = 'smoothed 1d array for y'

    def run(self):
        # TODO: this needs to be reviewed for correctness,
        # and thoroughly commented to explain what it does
        x = self.inputs['x']
        y = self.inputs['y']
        o = self.inputs['order']
        b = self.inputs['base']
        err = self.inputs['dy']
        nx = x.size
        if err is None:
            err = np.ones(y.shape,dtype=float)        
        # "Minimal" point base case. 
        if b == -1:
            o_odd_flag = ((o/2)*2 != o)
            npts = o+1+int(o_odd_flag)
        # "Balanced" point base case.
        elif b == 0:
            npts = 2*o+1
        # "Additional" point base case.
        elif b > 0:
            npts = 2*(o+b)+1
        y_out = np.zeros(nx, dtype=float)
        for i in range(nx):
            # choose start and end indices
            npts_half = int(npts)/2 + 1
            start = max([i-npts_half+1,0])
            end = min([i+npts_half-1,nx-1])
            if b == -1:
                if (i-npts_half+1 < 0):
                    start = 0
                    end = npts 
                elif (i+npts_half-1 > nx-1):
                    start = size-1-m
                    end = size-1
            # Formulate the equation to be solved for polynomial coefficients
            xvals = x[start:end]
            yvals = y[start:end]
            errvals = err[start:end]
            nxvals = xvals.size
            idxs = np.arange(o+1)
            # reshape vectors for matrix mult
            y_vec = np.reshape(yvals,(nxvals,1,1))
            x_vec = np.reshape(xvals,(nxvals,1,1))
            err_vec = np.reshape(errvals,(nxvals,1,1))
            idx_column = np.reshape(idxs,(nxvals,1)) 
            idx_row = np.reshape(idxs,(1,nxvals)) 
            idx_block = idx_row + idx_column
            v = (y_vec * x_vec ** idx_column * err_vec).sum(axis=0)
            m = (x_vec ** idx_block * err_vec).sum(axis=0)
            # CALL LINALG.SOLVE...
            coefs = (np.linalg.solve(m, v)).flatten()
            y_out[i] = np.sum(x[i]**np.arange(o+1)*coefs)
        self.outputs['smoothed_data'] = y_out

