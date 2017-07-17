import numpy as np

from ... import Operation as op
from ...Operation import Operation

class SavitzkyGolay(Operation):
    """
    Applies a Savitzky-Golay (polynomial fit approximation) filter to 1d data.
    Uses error bars on intensity if available (default None).  
    """
    def __init__(self):
        input_names = ['x', 'y', 'dy', 'order', 'base']
        output_names = ['smoothdata']
        super(SavitzkyGolay, self).__init__(input_names, output_names)
        self.input_doc['x'] = '1d array- independent variable'
        self.input_doc['y'] = '1d array- dependent variable, same shape as x'
        self.input_doc['dy'] = '1d array, error estimate in y, same shape as y (default None)'
        self.input_doc['order'] = 'integer order of polynomial approximation (zero to five)'
        self.input_doc['base'] = '-1, 0, or positive integer; see class docs'
        self.output_doc['smoothdata'] = 'smoothed 1d array for y'
        self.input_src['x'] = op.wf_input
        self.input_src['y'] = op.wf_input
        self.input_src['dy'] = op.wf_input
        self.input_src['order'] = op.text_input
        self.input_src['base'] = op.text_input
        self.input_type['x'] = op.ref_type
        self.input_type['y'] = op.ref_type
        self.input_type['dy'] = op.ref_type
        self.input_type['order'] = op.int_type
        self.input_type['base'] = op.int_type

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        err = self.inputs['dy']
        o = int(self.inputs['order'])
        b = int(self.inputs['base'])
        nx = x.size
        if err is None:
            err = np.ones(y.shape,dtype=float)        
        # TODO: document what is being done here.
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
        # TODO: build y_out in a list comprehension.
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
            # TODO: document what is happening here
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
        self.outputs['smoothdata'] = y_out

