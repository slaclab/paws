import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ....Operation import Operation
from .... import optools
from ....DMZ import saxstools

class SAXSParameterization(Operation):
    """
    This operation uses a SAXS spectrum (I(q) vs. q), 
    along with some profiling information,
    to establish a set of parameters
    for fitting the SAXS spectrum
    to theoretical scattering models. 

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
        + 'Possible values: 0=success, 1=error (raised an Exception), 2=warning (found not fittable)')
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
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        d_result = {'I_at_0','precursor_factor':0,'r_pre':0,'spheroid_factor':0,'r_mean':0,'sigma_r':0,'I_at_0':0,'message':''}
        #low_q_idxs = (q < q[0]+0.1*(q[-1]-q[0]))
        #high_q_idxs = (q > q[0]+0.9*(q[-1]-q[0]))
        #n_low_q = np.sum(np.array(low_q_idxs))
        #n_high_q = np.sum(np.array(high_q_idxs))
        # If the max intensity is outside the low-q region, throw flag
        #if not np.argmax(I) in range(2*n_low_q):
        #    ok_flag = False
        #    flag_msg = str('The maximum intensity '
        #    + '({} at q={}) '.format(np.max(I),q[np.argmax(I)])
        #    + 'is outside the lower 20% of the q-range '
        #    + '({} to {}).'.format(q[0],q[2*n_low_q]))
        # If there is a huge maximum somewhere, throw flag
        #elif np.max(I) > 10*np.mean(I[:2*n_low_q]):
        #    ok_flag = False
        #    flag_msg = str('The maximum intensity '
        #    + '({} at q={}) '.format(np.max(I),q[np.argmax(I)])
        #    + 'is greater than 10x the mean intensity '
        #    + 'of the lower 20% of the q-range '
        #    + '({} from {} to {}).'
        #    .format(np.mean(I[low_q_idxs]),q[0],q[n_low_q]))
        # If high-q intensity not significantly smaller than low-q, throw flag
        #elif not np.sum(I[:n_low_q]) > 10*np.sum(I[-1*n_high_q:]):
        #    ok_flag = False
        #    flag_msg = str('The lower 10% of the q-range '
        #    + '({} to {}) '.format(q[0],q[n_low_q])
        #    + 'has less than 10 times the intensity '
        #    + 'of the upper 10% of the q-range '
        #    + '({} to {}).'.format(q[-1*n_high_q],q[-1]))
        ###check correlations of input vs. some known trends...
        n_q = len(q)
        I_mean = np.mean(I)
        I_std = np.std(I)
        #flat_corr = saxstools.compute_pearson(I,np.ones(n_q)+I_std/I_mean*(np.random.rand(n_q)-0.5))
        climb_corr = saxstools.compute_pearson(I,np.linspace(0,1,n_q))
        cos_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1])))
        cos2_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1]))**2)
        invq_corr = saxstools.compute_pearson(I,q**-1)
        invq4_corr = saxstools.compute_pearson(I,q**-4)
        precursor_flag = ( (cos_corr > 0.6 and cos2_corr > 0.6)
                        or (cos_corr > 0.7 or cos2_corr > 0.7)
                        or (cos_corr > 0.9*invq_corr or cos2_corr > 0.9*invq_corr) )
        spheroid_flag = ( invq_corr > 0.9 
                        or (invq_corr > cos_corr and invq_corr > cos2_corr) )
        # TODO: come up with some heuristics for presence of diffraction peaks
        diffraction_flag = False
        #print 'flatness coef: {}'.format(flat_corr)
        print 'climbingness coef: {}'.format(climb_corr)
        print 'cos coef: {}'.format(cos_corr)
        print 'cos2 coef: {}'.format(cos2_corr)
        print 'q^-1 coef: {}'.format(invq_corr)
        print 'q^-4 coef: {}'.format(invq4_corr)
        print 'use precursor terms: {}'.format(precursor_flag)
        print 'use spheroid terms: {}'.format(spheroid_flag)
        #if flat_corr > cos2_corr and flat_corr > invq_corr and flat_corr > invq4_corr:
        #    ok_flag = False
        #    flag_msg = str('This spectrum might be predominantly flat.')
        ok_flag = True
        if climb_corr > 0.2:
            ok_flag = False
            flag_msg = str('This spectrum is not sufficiently decreasing in q.')
        elif not any([precursor_flag,spheroid_flag,diffraction_flag]):
            ok_flag = False
            flag_msg = str('This spectrum has unfamiliar characteristics.')
        #######
        # Any other up-front filters should be added here.
        #######
        if not ok_flag: 
            self.outputs['return_code'] = 2
            self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'R2_log':0,'message':flag_msg} 
            self.outputs['heuristics'] = {} 
            self.outputs['q_I_norm'] = np.array([])
            self.outputs['q_I_guess'] = np.array([])
        else:
            d_h = {'precursor_flag':precursor_flag,'spheroid_flag':spheroid_flag,'diffraction_flag':diffraction_flag}
            if precursor_flag:
                r0_pre = 10
                sigma_r_pre = 0
                
            else:
                r0_pre = 0
                sigma_r_pre = 0
            if spheroid_flag:
                d_h.update(saxstools.saxs_spherical_normal_heuristics(q,I,dI))
                width_metric = d_h['pI_qwidth']/d_h['q_at_Iqqqq_min1']
                intensity_metric = d_h['I_at_Iqqqq_min1']/d_h['I_at_0']
                # Reference values for these heuristics
                # have been fit to polynomials in (sigma_r/r0) space.
                # To recompute these polynomials,
                # run paws.core.operations.DMZ.saxstools.generate_heuristics().
                # TODO: Insert value checks for these polynomials.
                # If no match, print warning, suggest updating them,
                # set return code to warning status.
                # Possibly update them automatically?
                #######
                #
                #
                # POLYNOMIALS WITH FITS AT q0+/-10%
                # polynomial for qr0 focus (with x=sigma_r/r0):
                # -8.05459639763x^2 + -0.470989868709x + 4.50108683096
                p_qr0_focus = [-8.05459639763,-0.470989868709,4.50108683096]
                # polynomial for width metric (with x=sigma_r/r0):
                # 3.12889797288x^2 + -0.0645231661487x + 0.0576604958693
                p_w = [3.12889797288,-0.0645231661487,0.0576604958693]
                # polynomial for intensity metric (with x=sigma_r/r0):
                # -1.33327411025x^3 + 0.432533640102x^2 + 0.00263776123775x + -1.27646761062e-05
                p_I = [-1.33327411025,0.432533640102,0.00263776123775,-1.27646761062e-05]
                #
                #
                #######
                # Now find the sigma_r/r0 value that gets the extracted metrics
                # as close as possible to p_I and p_w.
                width_error = lambda x: (np.polyval(p_w,x)-width_metric)**2
                intensity_error = lambda x: (np.polyval(p_I,x)-intensity_metric)**2
                # TODO: make this objective function weight all poly's equally
                heuristics_error = lambda x: width_error(x) + intensity_error(x)
                res = minimize(heuristics_error,[0.1],bounds=[(0,0.2)]) 
                if not res.success:
                    self.outputs['return_code'] = 2 
                    msg = str('[{}] function minimization failed during '
                    + 'heuristic-based feature extraction.'.format(__name__))
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
                    self.outputs['return_code'] = 0

