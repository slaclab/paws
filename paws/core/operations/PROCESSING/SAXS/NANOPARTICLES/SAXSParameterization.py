from collections import OrderedDict

import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ....Operation import Operation
from .... import optools
from .. import saxstools

class SAXSParameterization(Operation):
    """
    The algorithm for guessing parameters
    for the size distributions of spherical nanoparticles 
    was developed and originally contributed by Amanda Fournier.    

    This operation uses a SAXS spectrum (I(q) vs. q), 
    along with some profiling information,
    to guess a set of parameters
    for fitting the SAXS spectrum
    to theoretical scattering models. 
    The SAXS model employed here 
    assumes that the spectrum is a sum of the SAXS spectra
    of its constituent particles,
    which can be either precursors (small monodisperse spheres),
    spherical nanoparticles (spheres with a normal size distribution),
    or crystalline arrangements yielding diffraction peaks.
    Any number of populations of these three types can be specified.

    A precursor is modeled by a dilute, monodisperse spherical form factor.
    A spherical nanoparticle population is modeled by
    a discrete sum over a probability distribution
    of dilute, monodisperse spherical form factors. 
    A crystalline arrangement is modeled by a pseudo-Voigt profile.

    Outputs a return code,
    the parameter guesses, 
    and a dictionary of metrics taken from the input spectrum.
    Also outputs the theoretical result for I(q)
    and a renormalized measured spectrum, for visual comparison.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q', 'I', 'n_precursors', 'n_spherical_nps', 'n_diffpks']
        output_names = ['return_code','results','q_I_norm','q_I_guess','metrics']
        super(SphericalNormalHeuristics, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['n_precursors'] = str('The number of precursor populations '
        + 'to include in the parameterization, with 2 parameters per population')
        self.input_doc['n_spherical_nps'] = str('The number of spherical nanoparticle populations '
        + 'to include in the parameterization, with 3 parameters per population')
        self.input_doc['n_diffpks'] = str('The number of diffraction peaks '
        + 'to include in the parameterization, with 3 parameters per peak')
        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'Possible values: 0=success, 1=error (raised an Exception), 2=warning (found not fittable)')
        self.output_doc['results'] = str('dictionary containing SAXS parameters ' 
        + 'for populations according to inputs n_precursors, n_spherical_nps, and n_diffpks. '
        + 'For each precursor population, there is a radius (in Angstroms) '
        + 'and a unitless scaling factor. '
        + 'For each spherical nanoparticle population, '
        + 'there is a mean radius (Angstroms), '
        + 'standard deviation (Angstroms) , and unitless scaling factor. '
        + 'For each diffraction peak, '
        + 'there is the peak center (1/Angstrom), '
        + 'the peak width (1/Angstrom), and a unitless scaling factor.'
        + 'Also includes the spectral intensity at q=0, '
        + 'found by fitting the low-q region '
        + 'to a polynomial that is constrained to have zero slope at q=0.'
        + 'Also includes correlation coefficients '
        + 'between the logarithms of the measured and modeled spectra. '
        + 'Dict keys (strings): "I_at_0", "R2_log", "r_pearson", '
        + '"precursor_params", "spherical_np_params", diffraction_pk_params."')
        self.output_doc['q_I_norm'] = 'The input q,I(q) spectrum normalized so that I(q=0) is near 1.'
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the modeled intensity spectrum '
        + 'for the parameters given in the results output') 
        self.output_doc['metrics'] = 'dictionary of metrics taken from the input spectrum.' 
       
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['n_precursors'] = optools.text_input
        self.input_src['n_spherical_nps'] = optools.text_input
        self.input_src['n_diffpks'] = optools.text_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['n_precursors'] = optools.int_type
        self.input_type['n_spherical_nps'] = optools.int_type
        self.input_type['n_diffpks'] = optools.int_type
        self.inputs['n_precursors'] = 0
        self.inputs['n_spherical_nps'] = 0
        self.inputs['n_diffpks'] = 0

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        d_result = OrderedDict({'I_at_0':0,'R2_log':float('nan'),
        'r_pearson':float('nan'),'precursor_params':{},
        'spherical_np_params':{},'diffraction_pk_params':{},'message':''})
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
                # POLYNOMIALS FITTED FOR q0+/-10%,
                # where q0 is the argmin of a parabola
                # that is fit around the first minimum of I*q**4.
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

    def generate_heuristics():
        sigma_over_r = []
        width_metric = []
        intensity_metric = []
        qr0_focus = []
        r0_vals = np.arange(10,41,10,dtype=float)              #Angstrom
        for ir,r0 in zip(range(len(r0_vals)),r0_vals):
            q = np.arange(0.001/r0,float(10)/r0,0.001/r0)       #1/Angstrom
            sigma_r_vals = np.arange(0*r0,0.21*r0,0.01*r0)      #Angstrom
            for isig,sigma_r in zip(range(len(sigma_r_vals)),sigma_r_vals):
                I = compute_spherical_normal_saxs(q,r0,sigma_r) 
                d = saxs_spherical_normal_heuristics(q,I)
                sigma_over_r.append(float(sigma_r)/r0)
                qr0_focus.append(d['q_at_Iqqqq_min1']*r0)
                width_metric.append(d['pI_qwidth']/d['q_at_Iqqqq_min1'])
                intensity_metric.append(d['I_at_Iqqqq_min1']/d['I_at_0'])
        # TODO: standardize before fitting, then revert after
        p_qr0_focus = np.polyfit(sigma_over_r,qr0_focus,2,None,False,None,False)
        p_w = np.polyfit(sigma_over_r,width_metric,2,None,False,None,False)
        p_I = np.polyfit(sigma_over_r,intensity_metric,3,None,False,None,False)
        print('polynomial for qr0 focus (with x=sigma_r/r0): {}x^2 + {}x + {}'.format(p_qr0_focus[0],p_qr0_focus[1],p_qr0_focus[2]))
        print('polynomial for width metric (with x=sigma_r/r0): {}x^2 + {}x + {}'.format(p_w[0],p_w[1],p_w[2]))
        print('polynomial for intensity metric (with x=sigma_r/r0): {}x^3 + {}x^2 + {}x + {}'.format(p_I[0],p_I[1],p_I[2],p_I[3]))
        plot = True
        if plot: 
            from matplotlib import pyplot as plt
            plt.figure(1)
            plt.scatter(sigma_over_r,width_metric)
            plt.plot(sigma_over_r,np.polyval(p_w,sigma_over_r))
            plt.figure(2)
            plt.scatter(sigma_over_r,intensity_metric)
            plt.plot(sigma_over_r,np.polyval(p_I,sigma_over_r))
            plt.figure(3)
            plt.scatter(sigma_over_r,qr0_focus)
            plt.plot(sigma_over_r,np.polyval(p_qr0_focus,sigma_over_r))
            plt.figure(4)
            plt.scatter(width_metric,intensity_metric) 
            plt.show()


