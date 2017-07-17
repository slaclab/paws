import numpy as np

from ... import Operation as op
from ...Operation import Operation

class EasyZingers1D(Operation):
    """
    This Operation attempts to remove zingers 
    from 1-D spectral data (I(q) versus q).
    Zingers are replaced with the average intensity
    in a window around where the zinger was found.
    """

    def __init__(self):
        input_names = ['q_I']
        output_names = ['q_I_dz','zmask']
        super(EasyZingers1D, self).__init__(input_names, output_names)
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities'
        self.output_doc['q_I_dz'] = 'same as input q_I but with zingers removed'
        self.output_doc['zmask'] = 'array of booleans, same shape as q, true if there is a zinger at q, else false'
        self.input_src['q_I'] = op.wf_input
        self.input_type['q_I'] = op.ref_type

    def run(self):
        q_I = self.inputs['q_I']
        q = q_I[:,0]
        I = q_I[:,1]
        I_dz = np.array(I)
        zmask = np.array(np.zeros(len(q)),dtype=bool)
        w = 10
        I_ratio_limit = 10
        idx_z = []
        I_z = []
        stop_idx = len(q)-w-1
        test_range = iter(range(w,stop_idx))
        idx = test_range.next()
        while idx < stop_idx-1:
            Ii_l = np.array(I[idx-w:idx+1])
            Ii_r = np.array(I[idx:idx+w+1])
            #Ii = np.vstack( Iileft,Iiright )
            #Iimin = np.min(Ii)
            #Ii = Ii - Iimin 
            #I_ratio = float(I[idx]-Iimin)/np.mean( Ii )
            Iimin_l = np.min(Ii_l)
            Iimin_r = np.min(Ii_r)
            Ii_l = Ii_l - Iimin_l
            Ii_r = Ii_r - Iimin_r
            I_ratio_l = Ii_l[-1]/np.mean(Ii_l[:-1]) 
            I_ratio_r = Ii_r[0]/np.mean(Ii_r[1:]) 
            #print '{}: {}, {}'.format(q[idx],I_ratio_l,I_ratio_r)
            if I_ratio_l > I_ratio_limit or I_ratio_r > I_ratio_limit:
                idx_z.append(idx)
                zmask[idx] = True
                I_dz[idx] = np.nan
            idx = test_range.next() 
        q_z = [q[i] for i in idx_z]
        I_z = [I[i] for i in idx_z]
        newIvals = np.zeros(len(q_z)) 
        for qi,zi in zip(idx_z,range(len(idx_z))):
            Idzi = I_dz[qi-w:qi+w+1]
            Idzi = Idzi[~np.isnan(Idzi)]
            newIvals[zi] = np.mean(Idzi)
        for i,iq in zip(range(len(idx_z)),idx_z):
            I_dz[iq] = newIvals[i]
        self.outputs['q_I_dz'] = np.array(zip(q,I_dz))
        self.outputs['zmask'] = zmask

        #if any(idx_z):
        #if True:
        #    from matplotlib import pyplot as plt
        #    plt.figure(1)
        #    plt.semilogy(q,I)
        #    plt.semilogy(q,I_dz,'g')
        #    for i in idx_z:
        #        plt.semilogy(q[i],I[i],'ro')
        #    plt.show()
            

