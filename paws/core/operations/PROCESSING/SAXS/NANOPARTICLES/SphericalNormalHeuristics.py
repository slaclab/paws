import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ....Operation import Operation
from .... import optools
from ....DMZ import saxstools

class SphericalNormalHeuristics(Operation):
    """
    The algorithm employed here was developed by Amanda Fournier.    

    Use a SAXS spectrum (I(q) vs. q) to 
    guess the mean and standard deviation of particle sizes
    under the assumption of spherical nanoparticles
    with a Normal size distribution.
    TODO: document the algorithm here.

    Output a return code and diagnostics as needed,
    and a dictionary of the extracted heuristics.
    In case of success, report the size distribution parameters
    and the approximate scattered intensity at q=0.
    Also return the corresponding theoretical result for I(q),
    alongside a renormalized measured spectrum, for visual comparison.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q', 'I', 'dI']
        output_names = ['return_code','results','q_I_norm','q_I_guess','heuristics']
        super(SphericalNormalHeuristics, self).__init__(input_names, output_names)
        
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = '1d array of error estimates of intensity values (optional- input None to ignore)'
        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'Possible values: -1=error, 0=not fittable, 1=fittable')
        self.output_doc['results'] = str('dictionary containing guesses for '
        + 'the mean size, standard deviation, and I(q=0). '
        + 'Also includes the coefficient of determination '
        + 'between the logarithms of the measured and guessed spectra. '
        + 'Dict keys (strings): "r_mean", "sigma_r", "I_at_0", "R2_log". '
        + 'Units: Angstrom, Angstrom, counts, unitless.')
        self.output_doc['q_I_norm'] = 'The input q,I(q) spectrum normalized so that I(q=0) is near 1.'
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the ideal intensity spectrum '
        + 'for the r_mean, sigma_r, and I_at_0 values in the results output') 
        self.output_doc['heuristics'] = 'dict of heuristics taken from the input spectrum' 
       
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.no_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type

    def run(self):
        #try:
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        self.outputs['return_code'] = -1
        #low_q_idxs = (q < 0.04)
        #if not any(low_q_idxs):
        low_q_idxs = (q < q[0]+0.1*(q[-1]-q[0]))
        high_q_idxs = (q > q[0]+0.9*(q[-1]-q[0]))
        n_low_q = np.sum(np.array(low_q_idxs))
        n_high_q = np.sum(np.array(high_q_idxs))
        # If the max intensity is outside the low-q region, throw flag
        if not np.argmax(I) in range(2*n_low_q):
            ok_flag = False
            flag_msg = str('The peak intensity '
            + '({} at q={}) '.format(np.max(I),q[np.argmax(I)])
            + 'is outside the lower 20% of the q-range '
            + '({} to {}).'.format(q[0],q[2*n_low_q]))
        # If there is a huge maximum somewhere, throw the flag
        elif np.max(I) > 10*np.mean(I[low_q_idxs]):
            ok_flag = False
            flag_msg = str('The peak intensity '
            + '({} at q={}) '.format(np.max(I),q[np.argmax(I)])
            + 'is greater than 10x the integrated intensity '
            + 'of the lower 10% of the q-range '
            + '({} from {} to {}).'
            .format(np.mean(I[low_q_idxs]),q[0],q[n_low_q]))
        # If high-q intensity not significantly smaller than low-q, throw flag
        elif not np.mean(I[:2*n_low_q]) > 10*np.mean(I[-2*n_high_q:]):
            ok_flag = False
            flag_msg = str('The lower 20% of the q-range '
            + '({} to {}) '.format(q[0],q[2*n_low_q])
            + 'has less than 10 times the intensity '
            + 'of the upper 20% of the q-range '
            + '({} to {}).'.format(q[-2*n_high_q],q[-1]))
        else:
            ok_flag = True
        # TODO: flag poor low-q sampling (i.e. flag if minimum q is quite high) 
        # as it may affect the quality of the fit for I_at_0
        #######
        # Any other up-front filters should be added here.
        #######
        if not ok_flag: 
            self.outputs['return_code'] = 0
            self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'R2_log':0,'message':flag_msg} 
            self.outputs['heuristics'] = {} 
            self.outputs['q_I_norm'] = np.array([])
            self.outputs['q_I_guess'] = np.array([])
        else:
            try:
                d_h = saxstools.saxs_spherical_normal_heuristics(q,I,dI)
            except Exception as ex:
                self.outputs['return_code'] = -1
                self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'R2_log':0,'message':d_h['message']} 
                raise ex
            if not all([x in d_h.keys() for x in ['pI_qwidth','q_at_Iqqqq_min1','I_at_Iqqqq_min1','I_at_0']]):
                self.outputs['return_code'] = 0
                self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'R2_log':0,'message':'heuristic extraction did not finish'} 
                raise Exception('Heuristics can not continue because spectrum feature extraction did not finish')
            width_metric = d_h['pI_qwidth']/d_h['q_at_Iqqqq_min1']
            intensity_metric = d_h['I_at_Iqqqq_min1']/d_h['I_at_0']
            # Reference values for these heuristics
            # have been fit to polynomials in (sigma_r/r0) space
            # TODO: Insert some quick value checks on these polynomials.
            # If no match, print warning, suggest updating them.
            # Or maybe update them automatically?
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
            # TODO: make this objective function weight both poly's equally
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
                I_guess = saxstools.compute_spherical_normal_saxs(q,r0,sigma_r) 
                I_guess_at_0 = saxstools.compute_spherical_normal_saxs(np.array([0]),r0,sigma_r) 
                q_I_guess = np.array([q,I_guess/I_guess_at_0[0]]).T
                q_I_norm = np.array([q,I/I_at_0]).T

                I_norm_nz = np.invert( (q_I_norm[:,1]==0) )
                logI_norm = np.log(q_I_norm[I_norm_nz,1])
                logI_guess = np.log(q_I_guess[I_norm_nz,1])
                sum_logvar = np.sum( (logI_norm-np.mean(logI_norm))**2 )
                sum_logres = np.sum( (logI_guess-logI_norm)**2 ) 
                R2_log = float(1)-float(sum_logres)/sum_logvar
 
                self.outputs['results'] = {'r_mean':r0,'sigma_r':sigma_over_r*r0,'I_at_0':I_at_0,'R2_log':R2_log} 
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



