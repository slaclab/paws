from collections import OrderedDict

import numpy as np

from ..Operation import Operation

inputs = OrderedDict(
    q_I=None,
    sharpness_limit=40,
    window_width=10
    )
outputs = OrderedDict(
    q_I_dz=None,
    zmask=None
    )

class EasyZingers1d(Operation):
    """Operation for quickly removing zingers from 1d spectral data.

    For each point (or "pixel") in the spectrum, 
    the neighboring points within a specified window width
    to the right and left are analyzed
    to determine whether or not the point of interest 
    is part of an exceedingly sharp edge.
    Points that exceed the sharpness limit are flagged as zingers,
    and in a second pass these points are subtituted 
    by the average intensity in the same window around the zinger point.

    Let pixel_i be a candidate zinger. The analysis is as follows:
    1. Take window_width pixels on either side of pixel_i.
        Call these pixels_left and pixels_right.

    2. (TODO: finish this)
        
    3. (TODO: finish this) 
        
    4. If either of the results in step (3) is greater than sharpness_limit,
        flag pixel_i as a zinger.

    After all zingers are flagged, they are replaced.
    Going over all pixels again, let pixel_i be a zinger:

    1. For pixel_i, take the average of all pixels_left and pixels_right,
        counting only pixels that are not flagged as zingers. 

    2. Replace I(pixel_i) with this window-average value.

    Note, this will result in unusually "flat" 
    regions where zingers used to be,
    as the local window-averaging effectively hides the noise.
    """

    def __init__(self):
        super(EasyZingers1d, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities'
        self.input_doc['sharpness_limit'] = 'sharpness limit '\
            'for flagging zingers- turn this down to catch more zingers, '\
            'turn it up to catch fewer zingers'
        self.input_doc['window_width'] = 'number of points '\
            'on either side of a given pixel '\
            'used to evaluate sharpness of the pixel'
        self.output_doc['q_I_dz'] = 'same as input q_I but with zingers removed'
        self.output_doc['zmask'] = 'array of booleans, same shape as q, true if there is a zinger at q, else false'

    def run(self):
        q_I = self.inputs['q_I']
        I_ratio_limit = self.inputs['sharpness_limit'] 
        w = self.inputs['window_width'] 
        q = q_I[:,0]
        I = q_I[:,1]
        I_dz = np.array(I)
        zmask = np.array(np.zeros(len(q)),dtype=bool)
        idx_z = []
        I_z = []
        stop_idx = len(q)-w-1
        test_range = iter(range(w,stop_idx))
        idx = next(test_range)
        while idx < stop_idx-1:
            idx_l = np.array([i for i in np.arange(idx-w,idx+1,1) if not i in idx_z])
            idx_r = np.array([i for i in np.arange(idx,idx+w+1,1) if not i in idx_z])
            Ii_l = np.array(I[idx_l])
            Ii_r = np.array(I[idx_r])
            # subtract a linear background from either side
            #Ii_l = Ii_l - np.polyval(np.polyfit(idx_l[:-1],Ii_l[:-1],1),idx_l)
            #Ii_r = Ii_r - np.polyval(np.polyfit(idx_r[1:],Ii_r[1:],1),idx_r)
            # Subtract an approximate linear background from either side
            q_ratio_l = (q[idx_l[-1]] - q[idx_l[:-1]]) / (q[idx_l[-1]]-q[idx_l[0]])  
            q_ratio_r = (q[idx_r[1:]] - q[idx_r[0]])   / (q[idx_r[-1]]-q[idx_r[0]])  
            Ii_l[:-1] = Ii_l[:-1] - q_ratio_l * (Ii_l[0]-Ii_l[-2]) 
            Ii_r[1:] = Ii_r[1:] - q_ratio_r * (Ii_r[-1]-Ii_r[1]) 
            Istd_l = np.std(Ii_l[:-1]) 
            Istd_r = np.std(Ii_r[1:]) 
            
            #I_ratio_l = Ii_l[-1]/Istd_l
            #I_ratio_r = Ii_r[0]/Istd_r
            #I_ratio_l = (Ii_l[-1]-Ii_l[-2])/Imean_diff_l
            #I_ratio_r = (Ii_r[0]-Ii_r[1])/Imean_diff_r
            if Istd_l and Istd_r:
                I_ratio_l = (Ii_l[-1]-Ii_l[-2])/Istd_l
                I_ratio_r = (Ii_r[0]-Ii_r[1])/Istd_r
                if I_ratio_l > I_ratio_limit or I_ratio_r > I_ratio_limit:
                    self.message_callback('found a zinger: q = {}, I = {}'.format(q[idx],I[idx]))
                    idx_z.append(idx)
                    zmask[idx] = True
                    I_dz[idx] = np.nan
            idx = next(test_range) 
        q_z = [q[i] for i in idx_z]
        I_z = [I[i] for i in idx_z]
        newIvals = np.zeros(len(q_z)) 
        for qi,zi in zip(idx_z,range(len(idx_z))):
            Idzi = I_dz[qi-w:qi+w+1]
            Idzi = Idzi[~np.isnan(Idzi)]
            newIvals[zi] = np.mean(Idzi)
        for i,iq in zip(range(len(idx_z)),idx_z):
            I_dz[iq] = newIvals[i]
        self.outputs['q_I_dz'] = np.array([q,I_dz]).T
        self.outputs['zmask'] = zmask
        return self.outputs

