import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ....Operation import Operation
from .... import optools

class SphericalNormalHeuristics(Operation):
    """
    Use a SAXS spectrum (I(q) vs. q) to 
    guess the mean and standard deviation of particle sizes
    under the assumption of spherical nanoparticles
    with a Normal size distribution.
    TODO: document the algorithm here.
    Output the mean and standard deviation of particle radius,
    and the scattered intensity at q=0.

    Assumes the data have already been background subtracted, 
    smoothed, and otherwise cleaned.
    """

    def __init__(self):
        # TODO: deprecate debug_info
        input_names = ['q', 'I', 'dI']
        output_names = ['return_code','results','q_I_norm','q_I_guess','heuristics']
        super(SphericalNormalHeuristics, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = '1d array of error estimates of intensity values (optional- input None to ignore)'
        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'Possible values: -1=error, 0=not fittable, 1=fittable')
        self.output_doc['results'] = str('dictionary containing guesses for '
        + 'the mean size, standard deviation, and I(q=0). '
        + 'Dict keys (strings): "r_mean", "sigma_r", "I_at_0". Units: Angstrom, Angstrom, counts.')
        self.output_doc['q_I_norm'] = 'The input q,I(q) spectrum normalized so that I(q=0) is near 1.'
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the ideal intensity spectrum '
        + 'for the r_mean, sigma_r, and I_at_0 values in the results output') 
        self.output_doc['heuristics'] = 'dict of heuristics taken from the input spectrum' 
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.no_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type

    def run(self):
        #try:
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        self.outputs['return_code'] = -1
        low_q_idxs = (q < 0.04)
        if not any(low_q_idxs):
            low_q_idxs = (q < q[0]+0.1*(q[-1]-q[0]))
        high_q_idxs = (q > 0.9 * q[-1])
        n_low_q = np.sum(np.array(low_q_idxs))
        # If the maximum intensity is not somewhere up front, throw the flag.
        if not np.argmax(I) in range(n_low_q):
            ok_flag = False
            flag_msg = 'Maximum intensity does not seem to occur at low q' 
        elif not np.mean(I[low_q_idxs]) > 100*np.mean(I[high_q_idxs]):
            ok_flag = False
            flag_msg = 'Low-q region does not have at least 100 times the intensity of the high-q region'
        else:
            ok_flag = True
        # TODO: flag poor low-q sampling (i.e. flag if minimum q is quite high) 
        # as it may affect the quality of the fit for I_at_0
        #######
        # Any other up-front filters should be added here.
        #######
        if not ok_flag: 
            self.outputs['return_code'] = 0
            self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'message':flag_msg} 
            self.outputs['heuristics'] = {} 
            self.outputs['q_I_norm'] = np.array([])
            self.outputs['q_I_guess'] = np.array([])
        else:
            try:
                d_h = self.saxs_heuristics(q,I,dI)
            except Exception as ex:
                self.outputs['return_code'] = -1
                self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'message':d_h['message']} 
                raise ex
            if not all([x in d_h.keys() for x in ['pI_qwidth','q_at_Iqqqq_min1','I_at_Iqqqq_min1','I_at_0']]):
                self.outputs['return_code'] = 0
                self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'message':'heuristic extraction did not finish'} 
                raise Exception('Heuristics can not continue because spectrum feature extraction did not finish')
            width_metric = d_h['pI_qwidth']/d_h['q_at_Iqqqq_min1']
            intensity_metric = d_h['I_at_Iqqqq_min1']/d_h['I_at_0']
            # Reference values for these heuristics
            # have been fit to polynomials in (sigma_r/r0) space
            #######
            # polynomial for width metric (x=sigma_r/r0): 
            # width_metric = 3.68173788182x^2 + -0.0972867340494x + 0.0266281923116
            p_w = [3.68173788182,-0.0972867340494,0.0266281923116]
            #######
            # polynomial for intensity metric (x=sigma_r/r0): 
            # intensity_metric = -1.28044626076x^3 + 0.415263527626x^2 + 0.00256174486511x + -3.33950927542e-05
            p_I = [-1.28044626076,0.415263527626,0.00256174486511,-3.33950927542e-05]
            #######
            # polynomial for qr0 focus (x=sigma_r/r0): -8.29227728608x^2 + -0.499026082663x + 4.50142008516
            # TODO: improve the fit of this polynomial
            p_qr0_focus = [-8.29227728608,-0.499026082663,4.50142008516]
            #######
            # Now find the sigma_r/r0 value that gets the extracted metrics
            # as close as possible to p_I and p_w.
            width_error = lambda x: (np.polyval(p_w,x)-width_metric)**2
            intensity_error = lambda x: (np.polyval(p_I,x)-intensity_metric)**2
            # TODO: Standardize this objective function to weight both poly's equally
            heuristics_error = lambda x: width_error(x) + intensity_error(x)
            res = minimize(heuristics_error,[0.1],bounds=[(0,0.2)]) 
            if not res.success:
                self.outputs['return_code'] = 0 
                msg = '[{}] heuristic-based feature extraction failed to minimize.'.format(__name__)
                self.outputs['results'] = {'message':msg}
            else:
                sigma_over_r = res.x[0]
                I_at_0 = d_h['I_at_0']
                qr0_focus = np.polyval(p_qr0_focus,sigma_over_r)
                # qr0_focus = x1  ==>  r0 = x1 / q1
                r0 = qr0_focus/d_h['q_at_Iqqqq_min1']
                sigma_r = sigma_over_r * r0 
                I_guess = self.compute_saxs(q,r0,sigma_r) 
                I_near_0 = self.compute_saxs(np.array([0.001]),r0,sigma_r) 
                q_I_guess = np.array([q,I_guess/I_near_0[0]]).T
                q_I_norm = np.array([q,I/I_at_0]).T
 
                self.outputs['results'] = {'r_mean':r0,'sigma_r':sigma_over_r*r0,'I_at_0':I_at_0} 
                self.outputs['heuristics'] = d_h
                self.outputs['q_I_norm'] = q_I_norm 
                self.outputs['q_I_guess'] = q_I_guess 
                self.outputs['return_code'] = 1
        #except Exception as ex:
        #    msg = str('[{}] An exception was raised during execution. '.format(__name__)
        #    + 'Error message: {}'.format(ex.message))
        #    self.outputs['return_code'] = -1
        #    ex.message = msg
        #    raise ex

    @staticmethod
    def saxs_heuristics(q,I,dI=None):
        try:
            # Save computed heuristics in a dict.
            d = {}
            d['message'] = ''
            # Weights for fitting, based on dI
            if not dI:
                # uniform weights
                wt = np.ones(q.shape)   
            else:
                # inverse error weights, 1/dI, 
                # appropriate if dI represents
                # Gaussian uncertainty with sigma=dI
                wt = 1./dI
            #######
            # Heuristics 1: the first local max
            # and first local minimum of I*q**4 for q>0
            Iqqqq = I*q**4
            # w is the number of adjacent points to consider 
            # when examining the I*q^4 curve for local extrema.
            # A greater value of w filters out smaller extrema.
            w = 10
            idxmax1, idxmin1 = 0,0
            test_range = iter(range(w,len(q)-w-1))
            idx = test_range.next() 
            stop_idx = len(q)-w-1
            while any([idxmax1==0,idxmin1==0]) and idx < stop_idx-1:
                if np.argmax(Iqqqq[idx-w:idx+w+1]) == w and idxmax1 == 0:
                    idxmax1 = idx
                if np.argmin(Iqqqq[idx-w:idx+w+1]) == w and idxmin1 == 0 and not idxmax1 == 0:
                    idxmin1 = idx
                idx = test_range.next()
            if idxmin1 == 0 or idxmax1 == 0:
                ex_msg = str('unable to find first maximum and minimum of I*q^4 '
                + 'by scanning for local extrema with a window width of {} points'.format(w))
                d['message'] = ex_msg 
                raise Exception(ex_msg)
            #######
            # Heuristics 2: characteristics of I*q**4 around idxmin1, 
            # by locally fitting a standardized polynomial.
            idx_around_min1 = (q>0.95*q[idxmin1]) & (q<1.05*q[idxmin1])
            q_min1_mean = np.mean(q[idx_around_min1])
            q_min1_std = np.std(q[idx_around_min1])
            q_min1_s = (q[idx_around_min1]-q_min1_mean)/q_min1_std
            Iqqqq_min1_mean = np.mean(Iqqqq[idx_around_min1])
            Iqqqq_min1_std = np.std(Iqqqq[idx_around_min1])
            Iqqqq_min1_s = (Iqqqq[idx_around_min1]-Iqqqq_min1_mean)/Iqqqq_min1_std
            p_min1 = np.polyfit(q_min1_s,Iqqqq_min1_s,2,None,False,
                wt[idx_around_min1]/(q[idx_around_min1]**4),False)
            # polynomial vertex horizontal coord is -b/2a
            qs_at_min1 = -1*p_min1[1]/(2*p_min1[0])
            d['q_at_Iqqqq_min1'] = qs_at_min1*q_min1_std+q_min1_mean
            # polynomial vertex vertical coord is poly(-b/2a)
            Iqqqqs_at_min1 = np.polyval(p_min1,qs_at_min1)
            d['Iqqqq_min1'] = Iqqqqs_at_min1*Iqqqq_min1_std+Iqqqq_min1_mean
            d['I_at_Iqqqq_min1'] = d['Iqqqq_min1']*float(1)/(d['q_at_Iqqqq_min1']**4)
            # The focal width of the parabola is 1/a 
            p_min1_fwidth = float(1)/p_min1[0] 
            d['pIqqqq_qwidth'] = p_min1_fwidth*q_min1_std
            # The focal point is at -b/2a,poly(-b/2a)+1/(4a)
            p_min1_fpoint = Iqqqqs_at_min1+float(1)/(4*p_min1[0])
            d['pIqqqq_Iqqqqfocus'] = p_min1_fpoint*Iqqqq_min1_std+Iqqqq_min1_mean
            #######
            # Heuristics 2b: characteristics of I(q) near min1 of Iqqqq
            I_min1_mean = np.mean(I[idx_around_min1])
            I_min1_std = np.std(I[idx_around_min1])
            I_min1_s = (I[idx_around_min1]-I_min1_mean)/I_min1_std
            pI_min1 = np.polyfit(q_min1_s,I_min1_s,
                2,None,False,wt[idx_around_min1],False)
            # polynomial vertex horizontal coord is -b/2a
            qs_vertex = -1*pI_min1[1]/(2*pI_min1[0])
            d['pI_qvertex'] = qs_vertex*q_min1_std+q_min1_mean
            # polynomial vertex vertical coord is poly(-b/2a)
            Is_vertex = np.polyval(pI_min1,qs_vertex)
            d['pI_Ivertex'] = Is_vertex*I_min1_std+I_min1_mean
            # The focal width of the parabola is 1/a 
            pI_fwidth = float(1)/pI_min1[0]
            d['pI_qwidth'] = pI_fwidth*q_min1_std
            # The focal point is at -b/2a,poly(-b/2a)+1/(4a)
            pI_fpoint = Is_vertex+float(1)/(4*pI_min1[0])
            d['pI_Ifocus'] = pI_fpoint*I_min1_std+I_min1_mean
            #######
            # Heuristics 3: I(q=0) by polynomial fitting,
            # in the region below the first max of I*q^4.
            # TODO: add constraints for slope, curv to be zero at q=0
            idx_lowq = range(idxmax1)
            I_lowq_mean = np.mean(I[idx_lowq])
            I_lowq_std = np.std(I[idx_lowq])
            lowq_mean = np.mean(q[idx_lowq])
            lowq_std = np.std(q[idx_lowq])
            I_lowq_s = (I[idx_lowq]-I_lowq_mean)/I_lowq_std
            lowq_s = (q[idx_lowq]-lowq_mean)/lowq_std
            p_lowq = np.polyfit(lowq_s,I_lowq_s,2,None,False,wt[idx_lowq],False) 
            d['I_at_0'] = np.polyval(p_lowq,-1*lowq_mean/lowq_std)*I_lowq_std+I_lowq_mean
            return d
        except Exception as ex:
            #import pdb; pdb.set_trace()
            d['message'] = d['message'] + '\n' + ex.message
            return d

    @staticmethod
    def compute_saxs(q,r0,sigma_r):
        # TODO: renormalize this so that I(q=0) = 1
        if sigma_r == 0:
            x = q*r0
            V_r0 = float(4)/3*np.pi*r0**3
            I = V_r0**2 * (3.*(np.sin(x)-x*np.cos(x))*x**-3)**2
        else:
            I = np.zeros(q.shape)
            dr = sigma_r*0.02
            rmin = np.max([r0-5*sigma_r,dr])
            rmax = r0+5*sigma_r
            for ri in np.arange(rmin,rmax,dr):
                xi = q*ri
                V_ri = float(4)/3*np.pi*ri**3
                # The normal-distributed density of particles with radius r_i:
                rhoi = 1./(np.sqrt(2*np.pi)*sigma_r)*np.exp(-1*(r0-ri)**2/(2*sigma_r**2))
                I += V_ri**2 * rhoi*dr*(3.*(np.sin(xi)-xi*np.cos(xi))*xi**-3)**2
        return I

        # more checks
        # is highest value early? is qFirstDip late?
        #if np.argmax(I) > int(0.3 * I.size):
        #    detailed_flags['late_intensity_max'] = True
        #if np.where(q < qFirstDip)[0][-1] < int(0.1 * q.size):
        #    detailed_flags['early_qFirstDip'] = True
        ## are there vaguely zinger-like or dead pixel-like features?
        #curv = (I[2:] - 2 * I[1:-1] + I[:-2])
        #var = (curv ** 2).mean() ** 0.5
        #if (curv < -5 * var).any():
        #    detailed_flags['zinger_like_feature'] = True
        #if (curv > 5 * var).any():
        #    detailed_flags['dead_pixel_like_feature'] = True
        ## vaguely figure-of-merit-like numbers
        #detailed_flags['root_mean_square_diff'] = ((Imodel - I) ** 2).mean() ** 0.5
        #logsafe = ~(np.isnan(I) | (I < 0))
        #detailed_flags['logarithmic_root_mean_square_diff'] = np.e ** (
        #((np.log((Imodel - I)[logsafe])) ** 2).mean() ** 0.5)


