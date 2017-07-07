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
    TODO: document scattering models.

    A precursor is modeled by a dilute, monodisperse spherical form factor.
    A spherical nanoparticle population is modeled by
    a discrete sum over a probability distribution
    of dilute, monodisperse spherical form factors. 
    A crystalline arrangement is modeled by 
    a sum of pseudo-Voigt peaks.

    Outputs a return code and heuristic guesses for SAXS model parameters. 
    Also outputs the theoretical result for I(q) with the guessed parameters.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q', 'I', 'features', 'fixed_params', 'fixed_param_values']
        output_names = ['return_code','features','q_I_guess']
        super(SpectrumParameterization, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['features'] = str('dict of outputs from spectrum profiler operation. \n'
        + 'This operation makes use of the following keys: \n'
        + 'precursor_flag: Boolean for whether or not to include '
        + 'monodisperse spherical precursor parameters '
        + '(2 parameters: precursor radius and intensity scaling factor). \n'
        + 'form_flag: Boolean for whether or not to include '
        + 'normally-distributed spherical form factor parameters '
        + '(3 parameters: mean radius, standard deviation of radius, intensity scaling factor). \n'
        + 'structure_flag: Boolean for whether or not to include '
        + 'a set of Pseudo-Voigt diffraction peak parameters '
        + '(3 parameters: principal peak location, peak width, intensity scaling factor). \n'
        + 'form_id: string indicating the form factor '
        + '(options: sphere). \n'
        + 'structure_id: string indicating the structure to use in setting the diffraction peaks '
        + '(options: currently none, eventually fcc, hcp, bcc, etc).')
        self.input_doc['fixed_params'] = str('list of strings indicating which parameters '
        + 'should be fixed to specified values- these correspond one-to-one with fixed_param_values.')
        self.input_doc['fixed_param_values'] = 'list of values to which the corresponding fixed_params will be set.'

        self.output_doc['return_code'] = str('integer indicating whether or not '
        + 'the spectrum was successfully parameterized for the given flags. '
        + 'Possible values: 0=success, 1=error (raised an Exception), '
        + '2=warning (spectrum exhibits unexpected features).')
        self.output_doc['features'] = str('dict of features, same as input features, ' 
        + 'but updated with parameters for the flagged populations. ' 
        + 'Dict keys and descriptions: \n' 
        + 'I_at_0: Intensity at q=0, by fitting the low-q region to a polynomial with dI/dq(q=0)=0. \n' 
        + 'r0_pre: precursor term radius (Angstrom). \n'
        + 'I0_pre: precursor intensity scaling factor. \n'
        + 'r0_form: mean characteristic size (Angstrom) of form factor population. \n'
        + 'sigma_form: fractional standard deviation of characteristic size of form factor population \n'
        + 'I0_form: form factor scattering intensity scaling factor \n'
        + 'q0_structure: q value (1/Angstrom) for location of fundamental structure factor peak \n' 
        + 'I0_structure: structure factor intensity scaling factor \n'
        + 'sigma_structure: width parameter for Pseudo-Voigt diffraction peak profile') 
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the intensity spectrum '
        + 'corresponding to the population parameters in the features dict.')

        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['features'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['features'] = optools.ref_type

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        p = self.inputs['features'] 
        if p['bad_data_flag']:
            # sabotage
            self.outputs['return_code'] = 2
            p['PARAMETERIZE_ERROR'] = '[{}] found bad_data flag, aborting'.format(__name__)
            self.outputs['features'] = p
            return 
        pre_flag = p['precursor_flag']
        f_flag = p['form_flag']
        s_flag = p['structure_flag']
        fix_keys = self.inputs['fixed_params']
        fix_vals = self.inputs['fixed_param_values']
        fixed_params = {} 
        for k,v in zip(fix_keys,fix_vals):
            fixed_params[k] = v


        # Check for overconstrained system
        if 'I_at_0' in fix_keys and 'I0_form' in fix_keys and 'I0_pre' in fix_keys:
            val1 = fixed_params['I_at_0']
            val2 = fixed_params['I0_form'] + fixed_params['I0_pre'] 
            if not val1 == val2:
                msg = str('Spectrum intensity is overconstrained. '
                + 'I_at_0 is constrained to {}, '
                + 'but I0_form + I0_pre = {}. '.format(val1,val2))
                raise ValueError(msg)
        
        #if 'I_at_0' in fix_keys:
        #    if not fixed_params['I_at_0'] == 0:
        #        I_at_0 = fixed_params['I_at_0']
        #    else:
        #        # Perform a low-q spectrum fit to get I(q=0).
        #        # If there are form or structure factor terms,
        #        # use the lower 10% of the q range.
        #        if f_flag or s_flag:
        #            qmax_fit = q[0]+float(q[-1]-q[0])*0.1
        #            idx_lowq = (q<qmax_fit)
        #            I_at_0 = saxstools.fit_I0(q[idx_lowq],I[idx_lowq])
        #        else:
        #            I_at_0 = saxstools.fit_I0(q,I)
        if 'I0_form' in fix_keys and 'I0_pre' in fix_keys:
            I_at_0 = fixed_params['I0_pre'] + fixed_params['I0_form']
        else:
            # Perform a low-q spectrum fit to get I(q=0).
            # If there are form or structure factor terms,
            # use the lower 10% of the q range.
            if f_flag or s_flag:
                qmax_fit = q[0]+float(q[-1]-q[0])*0.1
                idx_lowq = (q<qmax_fit)
                I_at_0 = saxstools.fit_I0(q[idx_lowq],I[idx_lowq])
            else:
                I_at_0 = saxstools.fit_I0(q,I)
            if I_at_0 > 1.5*I[0] or I_at_0 < 0.5*I[0]:
                #sabotage 
                msg = 'polynomial fit for I(q=0) deviates too far from low-q values' 
                p['ERROR_MESSAGE'] = msg
                p['I_at_0'] = I_at_0
                p['bad_data_flag'] = True 
                self.outputs['features'] = p
                self.outputs['return_code'] = 1
                raise Exception(msg) 
        p['I_at_0'] = I_at_0

        r0_form = None
        sigma_form = None
        if f_flag:
            if ('r0_form' in fix_keys and 'sigma_form' in fix_keys):
                r0_form = fixed_params['r0_form']
                sigma_form = fixed_params['sigma_form']
            else:
                try:
                    r0_form, sigma_form = saxstools.spherical_normal_heuristics(q,I,I_at_0=I_at_0)
                except Exception as ex:
                    # sabotage
                    p['ERROR_MESSAGE'] = ex.message
                    p['bad_data_flag'] = True 
                    self.outputs['features'] = p
                    self.outputs['return_code'] = 1
                    raise ex 
                if 'r0_form' in fix_keys:
                    r0_form = fixed_params['r0_form']
                if 'sigma_form' in fix_keys:
                    sigma_form = fixed_params['sigma_form']
        p['r0_form'] = r0_form
        p['sigma_form'] = sigma_form
        
        r0_pre = None
        if pre_flag:
            if 'r0_pre' in fix_keys:
                r0_pre = fixed_params['r0_pre']
            else:
                r0_pre = saxstools.precursor_heuristics(q,I,I_at_0=I_at_0)
        p['r0_pre'] = r0_pre 

        I0_pre = None
        I0_form = None
        if pre_flag and f_flag:
            if 'I0_pre' in fix_keys and 'I0_form' in fix_keys:
                I0_pre = fixed_params['I0_pre']
                I0_form = fixed_params['I0_form']
            elif 'I0_pre' in fix_keys:
                I0_pre = fixed_params['I0_pre']
                I0_form = I_at_0 - I0_pre
            elif 'I0_form' in fix_keys:
                I0_form = fixed_params['I0_form']
                I0_pre = I_at_0 - I0_form
            else:
                I_pre = saxstools.compute_spherical_normal_saxs(q,r0_pre,0)
                I_form = saxstools.compute_spherical_normal_saxs(q,r0_form,sigma_form)
                I_nz = np.invert((I<=0))
                I_error = lambda x: np.sum( (np.log(I_at_0*(x*I_pre+(1.-x)*I_form)[I_nz])-np.log(I[I_nz]))**2 )
                x_res = minimize(I_error,[0.1],bounds=[(0.0,1.0)]) 
                x_fit = x_res.x[0]
                I0_form = (1.-x_fit)*I_at_0
                I0_pre = x_fit*I_at_0
        elif pre_flag:
            if 'I0_pre' in fix_keys:
                I0_pre = fixed_params['I0_pre']
            else:
                I0_pre = I_at_0 
        elif f_flag:
            if 'I0_form' in fix_keys:
                I0_form = fixed_params['I0_form'] 
            else:
                I0_form = I_at_0 
        p['I0_pre'] = I0_pre 
        p['I0_form'] = I0_form 

        q0_structure = None
        I0_structure = None
        sigma_structure = None
        #if s_flag:
        #   .....   
        p['q0_structure'] = q0_structure 
        p['I0_structure'] = I0_structure 
        p['sigma_structure'] = sigma_structure

        I_guess = saxstools.compute_saxs(q,p)
        q_I_guess = np.array([q,I_guess]).T
        self.outputs['q_I_guess'] = q_I_guess 
        self.outputs['features'] = p 
        self.outputs['return_code'] = 0

        #### Get logarithmic coef of determination to assess fit quality:
        #I_norm_nz = np.invert( (q_I_norm[:,1]<=0) )
        #logI_norm = np.log(q_I_norm[I_norm_nz,1])
        #logI_guess = np.log(q_I_guess[I_norm_nz,1])
        #sum_logvar = np.sum( (logI_norm-np.mean(logI_norm))**2 )
        #sum_logres = np.sum( (logI_guess-logI_norm)**2 ) 
        #R2_log = float(1)-float(sum_logres)/sum_logvar
        #p['R2_log'] = R2_log
        ####

        #from matplotlib import pyplot as plt
        #print self.outputs['features']
        #plt.figure(1)
        #plt.semilogy(q_I_norm[:,0],q_I_norm[:,1])
        #plt.semilogy(q_I_guess[:,0],q_I_guess[:,1],'r')
        #plt.show()




