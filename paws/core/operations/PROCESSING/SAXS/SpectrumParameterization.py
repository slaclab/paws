from collections import OrderedDict

import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ...Operation import Operation
from ... import optools
from . import saxstools

class SpectrumParameterization(Operation):
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

    Outputs a return code and initial guesses for SAXS model parameters. 
    Also outputs the theoretical result for I(q)
    and a renormalized measured spectrum, for visual comparison.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q', 'I', 'precursor_flag', 'form_flag', 'structure_flag']
        output_names = ['return_code','params','q_I_norm','q_I_guess']
        super(SpectrumParameterization, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['precursor_flag'] = str('Boolean for whether or not to include '
        + 'monodisperse spherical precursor parameters '
        + '(2 parameters: precursor radius and intensity scaling factor).')
        self.input_doc['form_flag'] = str('Boolean for whether or not to include '
        + 'normally-distributed spherical form factor parameters '
        + '(3 parameters: mean radius, standard deviation of radius, intensity scaling factor).')
        self.input_doc['structure_flag'] = str('Boolean for whether or not to include '
        + 'a set of Pseudo-Voigt fcc diffraction peak parameters '
        + '(3 parameters: principal peak location, peak width, intensity scaling factor).')
        self.output_doc['return_code'] = str('integer indicating whether or not '
        + 'the spectrum was successfully parameterized for the given flags. '
        + 'Possible values: 0=success, 1=error (raised an Exception), '
        + '2=warning (spectrum exhibits unexpected features).')
        self.output_doc['params'] = str('dictionary containing SAXS spectrum parameters ' 
        + 'for populations corresponding to the input flags. ' 
        + 'Dict keys and descriptions: \n' 
        + 'I_at_0: Intensity at q=0, by fitting a polynomial to the low-q region with dI/dq(q=0)=0. \n' 
        + 'r0_pre: precursor term radius (Angstrom). \n'
        + 'I0_pre: precursor intensity scaling factor. \n'
        + 'r0_sphere: mean radius (Angstrom) of sphere population. \n'
        + 'sigma_sphere: standard deviation (Angstroms) of sphere population radii. \n'
        + 'I0_sphere: spherical population intensity scaling factor. \n'
        + 'q_pk0: q value (1/Angstrom) for location of fundamental structure factor peak. \n' 
        + 'sigma_pk: width parameter for Pseudo-Voigt diffraction peak profile. \n' 
        + 'I0_pk: structure factor intensity scaling factor.')
        self.output_doc['q_I_norm'] = 'The input spectrum normalized so that I(q=0) is near 1.'
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the modeled intensity spectrum '
        + 'for the parameters given in the params output') 
       
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['precursor_flag'] = optools.wf_input
        self.input_src['form_flag'] = optools.wf_input
        self.input_src['structure_flag'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['precursor_flag'] = optools.bool_type
        self.input_type['form_flag'] = optools.bool_type
        self.input_type['structure_flag'] = optools.bool_type
        self.inputs['precursor_flag'] = False 
        self.inputs['form_flag'] = False
        self.inputs['structure_flag'] = False

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        p = {} 
        #p = dict.fromkeys(['I_at_0','r0_pre','I0_pre','r0_sphere','sigma_sphere','I0_sphere','q_pk0','sigma_pk','I0_pk']) 
        # Perform a low-q spectrum fit to get I(q=0).
        # Use the lower 5% of the q range.
        I_at_0 = saxstools.fit_I0(q,I,q[0]+float(q[-1]-q[0])*0.1)
        p['I_at_0'] = I_at_0
        if self.inputs['precursor_flag']:
            p['r0_pre'] = 10
        if self.inputs['form_flag']:
            m = saxstools.saxs_Iq4_metrics(q,I)
            width_metric = m['pI_qwidth']/m['q_at_Iqqqq_min1']
            intensity_metric = m['I_at_Iqqqq_min1']/I_at_0
            #######
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
            #######
            # Now find the sigma_r/r0 value that gets the extracted metrics
            # as close as possible to p_I and p_w.
            width_error = lambda x: (np.polyval(p_w,x)-width_metric)**2
            intensity_error = lambda x: (np.polyval(p_I,x)-intensity_metric)**2
            # TODO: make the objective function weight all errors equally
            heuristics_error = lambda x: width_error(x) + intensity_error(x)
            res = minimize(heuristics_error,[0.1],bounds=[(0,0.3)]) 
            if not res.success:
                self.outputs['return_code'] = 2 
                msg = str('[{}] function minimization failed during '
                + 'form factor parameter extraction.'.format(__name__))
                self.outputs['results'] = {'message':msg}
            sigma_over_r = res.x[0]
            qr0_focus = np.polyval(p_qr0_focus,sigma_over_r)
            # qr0_focus = x1  ==>  r0 = x1 / q1
            r0 = qr0_focus/m['q_at_Iqqqq_min1']
            sigma_r = sigma_over_r * r0 
            p['r0_sphere'] = r0
            p['sigma_sphere'] = sigma_r
        if self.inputs['precursor_flag'] and self.inputs['form_flag']:
            p['I0_pre'] = 0.1
            p['I0_sphere'] = 0.9 
        elif self.inputs['precursor_flag']:
            p['I0_pre'] = 1.0 
        elif self.inputs['form_flag']:
            p['I0_sphere'] = 1.0 
        # TODO: process diffraction pk parameters.
        # For now, skip.
        #if self.inputs['structure_flag']:
        #    p['q_pk0'] = 0
        #    p['sigma_pk'] = 0
        #    p['I0_pk'] = 0

        I_guess = saxstools.compute_saxs(q,p)
        I_guess_at_0 = saxstools.compute_saxs(np.array([0]),p)
        q_I_guess = np.array([q,I_guess/I_guess_at_0[0]]).T
        q_I_norm = np.array([q,I/I_at_0]).T
        #### Get logarithmic coef of determination to assess fit quality:
        I_norm_nz = np.invert( (q_I_norm[:,1]==0) )
        #import pdb; pdb.set_trace()
        logI_norm = np.log(q_I_norm[I_norm_nz,1])
        logI_guess = np.log(q_I_guess[I_norm_nz,1])
        sum_logvar = np.sum( (logI_norm-np.mean(logI_norm))**2 )
        sum_logres = np.sum( (logI_guess-logI_norm)**2 ) 
        R2_log = float(1)-float(sum_logres)/sum_logvar
        p['R2_log'] = R2_log
        ####
        self.outputs['q_I_norm'] = q_I_norm 
        self.outputs['q_I_guess'] = q_I_guess 
        self.outputs['params'] = p 
        self.outputs['return_code'] = 0

    def generate_heuristics():
        sigma_over_r = []
        width_metric = []
        intensity_metric = []
        qr0_focus = []
        # TODO: generate heuristics on a 1-d grid of sigma/r
        # instead of the 2-d grid being used here now.
        r0_vals = np.arange(10,41,10,dtype=float)              #Angstrom
        for ir,r0 in zip(range(len(r0_vals)),r0_vals):
            q = np.arange(0.001/r0,float(10)/r0,0.001/r0)       #1/Angstrom
            sigma_r_vals = np.arange(0*r0,0.21*r0,0.01*r0)      #Angstrom
            for isig,sigma_r in zip(range(len(sigma_r_vals)),sigma_r_vals):
                I = compute_spherical_normal_saxs(q,r0,sigma_r) 
                I_at_0 = compute_spherical_normal_saxs(0,r0,sigma_r) 
                d = saxs_spherical_normal_heuristics(q,I)
                sigma_over_r.append(float(sigma_r)/r0)
                qr0_focus.append(d['q_at_Iqqqq_min1']*r0)
                width_metric.append(d['pI_qwidth']/d['q_at_Iqqqq_min1'])
                intensity_metric.append(d['I_at_Iqqqq_min1']/I_at_0)
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


