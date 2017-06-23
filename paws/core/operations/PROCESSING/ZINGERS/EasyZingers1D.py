import numpy as np

from ...Operation import Operation
from ... import optools

class EasyZingers1D(Operation):
    """
    This Operation attempts to remove zingers 
    from 1-D spectral data (I(q) versus q).
    Zingers are replaced with the average intensity
    in a window around where the zinger was found.
    """

    def __init__(self):
        input_names = ['q_I']
        output_names = ['q_I_dz','q_z']
        super(EasyZingers1D, self).__init__(input_names, output_names)
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities'
        self.output_doc['q_I_dz'] = 'same as input q_I but with zingers removed'
        self.output_doc['q_z'] = 'list of q values at which zingers were found'
        self.input_src['q_I'] = optools.wf_input
        self.input_type['q_I'] = optools.ref_type

    def run(self):
        q_I = self.inputs['q_I']
        q = q_I[:,0]
        I = q_I[:,1]
        w = 10
        I_ratio_limit = 10
        idx_z = []
        I_z = []
        stop_idx = len(q)-w-1
        test_range = iter(range(w,stop_idx))
        idx = test_range.next()
        Is = (I - np.mean(I))/np.std(I) 
        while idx < stop_idx-1:
            # TODO: this is f'd up?
            I_ratio = float(Is[idx])/np.mean( list(Is[idx-w:idx])+list(Is[idx+1:idx+w+1]) )
            print '{}: {}'.format(q[idx],I_ratio)
            if float(Is[idx])/np.mean( np.vstack([Is[idx-w:idx],Is[idx+1:idx+w+1]]) ) > I_ratio_limit:
                idx_z.append(idx)
                I_z.append(I[idx])
            idx = test_range.next() 
        q_z = [q[i] for i in idx_z]
        #if any(q_z):
        from matplotlib import pyplot as plt
        plt.figure(1)
        plt.semilogy(q,I)
        for i in range(len(q_z)):
            plt.semilogy(q_z[i],I_z[i],'ro')
        plt.show()
            

