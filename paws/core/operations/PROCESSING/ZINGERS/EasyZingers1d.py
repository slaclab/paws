from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

inputs = OrderedDict(q_I=None,sharpness_limit=40)
outputs = OrderedDict(q_I_dz=None,zmask=None)

class EasyZingers1d(Operation):
    """Operation for quickly removing zingers from 1d spectral data."""

    def __init__(self):
        super(EasyZingers1d, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities'
        self.input_doc['sharpness_limit'] = 'limit for the heuristic sharpness of a zinger- '\
            'turn this down to catch more zingers, turn it up to catch fewer zingers'
        self.output_doc['q_I_dz'] = 'same as input q_I but with zingers removed'
        self.output_doc['zmask'] = 'array of booleans, same shape as q, true if there is a zinger at q, else false'
        self.input_type['q_I'] = opmod.workflow_item

    def run(self):
        """Scan through the input spectrum and remove zingers.

        For each point in the spectrum, 
        the neighboring points to the right and left are analyzed
        to determine whether or not the point of interest 
        is part of an exceedingly sharp edge.
        Points that exceed the threshold are flagged as zingers,
        and in a second pass these points are subtituted 
        by the average intensity in a window around the zinger point.
        """

        q_I = self.inputs['q_I']
        I_ratio_limit = self.inputs['sharpness_limit'] 
        q = q_I[:,0]
        I = q_I[:,1]
        I_dz = np.array(I)
        zmask = np.array(np.zeros(len(q)),dtype=bool)
        w = 10 
        idx_z = []
        I_z = []
        stop_idx = len(q)-w-1
        test_range = iter(range(w,stop_idx))
        idx = test_range.next()
        while idx < stop_idx-1:
            idx_l = np.array([i for i in np.arange(idx-w,idx+1,1) if not i in idx_z])
            idx_r = np.array([i for i in np.arange(idx,idx+w+1,1) if not i in idx_z])
            Ii_l = np.array(I[idx_l])
            Ii_r = np.array(I[idx_r])
            # subtract a linear background from either side
            Ifit_l = np.polyval(np.polyfit(idx_l[:-1],Ii_l[:-1],1),idx_l)
            Ifit_r = np.polyval(np.polyfit(idx_r[1:],Ii_r[1:],1),idx_r)
            Ii_l = Ii_l - Ifit_l 
            Ii_r = Ii_r - Ifit_r 
            # subtract the minimum from either side
            #Ii_l = Ii_l - np.min(Ii_l)
            #Ii_r = Ii_r - np.min(Ii_r)
            Istd_l = np.std(Ii_l[:-1]) 
            Istd_r = np.std(Ii_r[1:]) 
            I_ratio_l = Ii_l[-1]/Istd_l
            I_ratio_r = Ii_r[0]/Istd_r
            if I_ratio_l > I_ratio_limit or I_ratio_r > I_ratio_limit:
                print('*** zinger found. *** \nI_ratio_l: {} \nI_ratio_r: {}'.format(I_ratio_l,I_ratio_r))
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
        if False:
            from matplotlib import pyplot as plt
            plt.figure(1)
            plt.semilogy(q,I)
            plt.semilogy(q,I_dz,'g')
            for i in idx_z:
                plt.semilogy(q[i],I[i],'ro')
            plt.show()
            

