from __future__ import print_function
from collections import OrderedDict
import copy

import numpy as np
from scipy.optimize import minimize as scipimin

def compute_saxs(q,flags,params):
    """Compute a SAXS intensity spectrum given some parameters.

    TODO: Document the equation.

    Parameters
    ----------
    q : array
        Array of q values at which saxs intensity should be computed.
    flags : dict
        Flags for scatterer populations. 
        Supported flags:
        - 'bad_data'
        - 'precursor_scattering' 
        - 'form_factor_scattering'
        - 'diffraction_peaks'
    params : dict
        Scattering equation parameters.
        Supported parameter keys:
        - 'I_at_0': intensity at q=0, by fitting the low-q region 
            to a polynomial with dI/dq(q=0)=0
        - 'I0_floor': magnitude of constant (flat in q) floor term 
        - 'rg_precursor': radius of gyration of precursors 
        - 'G_precursor': Guinier prefactor for precursor scattering 
        - 'I0_sphere': spherical form factor scattering intensity scaling factor 
        - 'r0_sphere': mean sphere size (Angstrom) 
        - 'sigma_sphere': fractional standard deviation of sphere size 

    Returns
    ------- 
    I : array
        Array of scattering intensities for each of the input q values
    """
    b_flag = flags['bad_data']
    s_flag = flags['diffraction_peaks']
    I = np.zeros(len(q))
    if not b_flag and not s_flag:
        pre_flag = flags['precursor_scattering']
        f_flag = flags['form_factor_scattering']
        I0_floor = params['I0_floor'] 
        I = I0_floor*np.ones(len(q))
        if pre_flag:
            rg_pre = params['rg_precursor']
            G_pre = params['G_precursor']
            # Precursor as a monodisperse spherical form factor:
            #I_pre = spherical_normal_saxs(q,r0_pre,0)
            # TODO: Finish implementing Guinier-Porod here, or similar 
            # TODO: implement G_pre as a (fixed?) parameter
            # Precursor as a Guinier-Porod equation for a small sphere:
            I_pre = guinier_porod(q,rg_pre,4,G_pre)
            I += I_pre
        if f_flag:
            I0_sph = params['I0_sphere']
            r0_sph = params['r0_sphere']
            sigma_sph = params['sigma_sphere']
            I_sph = spherical_normal_saxs(q,r0_sph,sigma_sph)
            I += I0_sph*I_sph
    return I

def spherical_normal_saxs(q,r0,sigma):
    """Compute SAXS intensity of a normally-distributed sphere population.

    Originally contributed by Amanda Fournier.

    The returned intensity is normalized 
    such that I(q=0) is equal to 1.

    Parameters
    ----------
    q : array
        array of scattering vector magnitudes
    r0 : float
        mean radius of the sphere population
    sigma : float
        fractional standard deviation of the sphere population radii

    Returns
    -------
    I : array
        Array of scattering intensities for each of the input q values
    """
    q_zero = (q == 0)
    q_nz = np.invert(q_zero) 
    I = np.zeros(q.shape)
    if sigma < 1E-9:
        x = q*r0
        V_r0 = float(4)/3*np.pi*r0**3
        I[q_nz] = V_r0**2 * (3.*(np.sin(x[q_nz])-x[q_nz]*np.cos(x[q_nz]))*x[q_nz]**-3)**2
        I_zero = V_r0**2 
    else:
        sigma_r = sigma*r0
        dr = sigma_r*0.02
        rmin = np.max([r0-5*sigma_r,dr])
        rmax = r0+5*sigma_r
        I_zero = 0
        for ri in np.arange(rmin,rmax,dr):
            xi = q*ri
            V_ri = float(4)/3*np.pi*ri**3
            # The normal-distributed density of particles with radius r_i:
            rhoi = 1./(np.sqrt(2*np.pi)*sigma_r)*np.exp(-1*(r0-ri)**2/(2*sigma_r**2))
            I_zero += V_ri**2 * rhoi*dr
            I[q_nz] += V_ri**2 * rhoi*dr*(3.*(np.sin(xi[q_nz])-xi[q_nz]*np.cos(xi[q_nz]))*xi[q_nz]**-3)**2
    if any(q_zero):
        I[q_zero] = I_zero
    I = I/I_zero 
    return I

def guinier_porod(q,r_g,porod_exponent,guinier_factor):
    """Compute the Guinier-Porod small-angle scattering intensity.
    
    Computes the Guinier-Porod scattering intensity,
    given the Guinier prefactor of the solvent/scatterer system,
    the Porod exponent of the scatterer geometry,
    and the radius of gyration of the scatterer.

    Reference
    ---------
    B. Hammouda, J. Appl. Cryst. (2010). 43, 716-719.
    """
    # q-domain boundary q_splice:
    q_splice = 1./r_g * np.sqrt(3./2*porod_exponent**2)
    idx_guinier = (q <= q_splice)
    idx_porod = (q > q_splice)
    # porod prefactor D:
    porod_factor = guinier_factor*np.exp(-1./2*porod_exponent)\
                    * (3./2*porod_exponent)**(1./2*porod_exponent)\
                    * 1./(r_g**porod_exponent)
    I = np.zeros(q.shape)
    # Guinier equation:
    if any(idx_guinier):
        I[idx_guinier] = guinier_factor * np.exp(-1./3*q[idx_guinier]**2*r_g**2)
    # Porod equation:
    if any(idx_porod):
        I[idx_porod] = porod_factor * 1./(q[idx_porod]**porod_exponent)
    return I


def profile_spectrum(q_I):
    """Numerical profiling of a SAXS spectrum.

    Profile a saxs spectrum (n-by-2 array q_I) 
    by taking several fast numerical metrics 
    from the measured data.
    The metrics should be consistent for spectra
    with different intensity scaling 
    or different q domains.   

    This method should execute gracefully
    for any n-by-2 input array,
    such that it can be used to profile any type of spectrum. 
    TODO: document the returned metrics here.

    Parameters
    ----------
    q_I : array
        n-by-2 array of scattering vector q and scattered intensity I
    
    Returns
    -------
    params : dict
        dictionary of scattering equation parameters,
        for input to compute_saxs() 
    """ 
    q = q_I[:,0]
    I = q_I[:,1]
    # I metrics
    idxmax = np.argmax(I)
    idxmin = np.argmin(I)
    I_min = I[idxmin]
    I_max = I[idxmax] 
    q_Imax = q[idxmax]
    I_range = I_max - I_min
    #I_sum = np.sum(I)
    I_mean = np.mean(I)
    Imax_over_Imean = I_max/I_mean
    # log(I) metrics
    nz = I>0
    q_nz = q[nz]
    I_nz = I[nz]
    logI_nz = np.log(I_nz)
    logI_max = np.max(logI_nz)
    logI_min = np.min(logI_nz)
    logI_range = logI_max - logI_min
    logI_std = np.std(logI_nz)
    logI_max_over_std = logI_max / logI_std
    # I_max peak shape analysis
    idx_around_max = ((q > 0.9*q_Imax) & (q < 1.1*q_Imax))
    Imean_around_max = np.mean(I[idx_around_max])
    Imax_sharpness = I_max / Imean_around_max

    ### fluctuation analysis
    # array of the difference between neighboring points:
    nn_diff = logI_nz[1:]-logI_nz[:-1]
    # keep indices where the sign of this difference changes.
    # also keep first index
    nn_diff_prod = nn_diff[1:]*nn_diff[:-1]
    idx_keep = np.hstack((np.array([True]),nn_diff_prod<0))
    fluc = np.sum(np.abs(nn_diff[idx_keep]))
    logI_fluctuation = fluc/logI_range

    # TODO: add some pearson metrics.
    # TODO: add qmin, qmax as metrics

    params = OrderedDict()
    params['q_Imax'] = q_Imax
    params['Imax_over_Imean'] = Imax_over_Imean
    params['Imax_sharpness'] = Imax_sharpness
    params['logI_fluctuation'] = logI_fluctuation
    params['logI_max_over_std'] = logI_max_over_std
    return params 

def parameterize_spectrum(q_I,flags):
    """Determine scattering equation parameters for a given spectrum.

    Parameters
    ----------
    q_I : array
        n-by-2 array of q (scattering vector in 1/A) and I (intensity)
    flags : dict
        dictionary of population flags, like SaxsClassifier.classify() output

    Returns
    -------
    params : dict
        dict of scattering equation parameters
        corresponding to the flagged populations,
        similar to the input params for compute_saxs().
    """
    #print('parameterizing for: {}'.format(flags))
    d = OrderedDict()
    #if flags['bad_data']:
    #    return d 
    q = q_I[:,0]
    I = q_I[:,1]
    n_q = len(q)
    # Get a number for I(q=0)
    # TODO: add units to this package
    # Disregard lowest-q values if they are far from the mean, 
    # as these points are likely dominated by experimental error,
    # such as interference from beam stops, etc.
    idx_lowq = (q<0.06)
    Imean_lowq = np.mean(I[idx_lowq])
    Istd_lowq = np.std(I[idx_lowq])
    idx_good = ((I[idx_lowq] < Imean_lowq+Istd_lowq) & (I[idx_lowq] > Imean_lowq-Istd_lowq))
    I_at_0 = fit_I0(q[idx_lowq][idx_good],I[idx_lowq][idx_good],4)
    # safety check in case of low-q errors (e.g. beam stop interference, beam drift)...
    if not I_at_0 > 0 or I_at_0 < 0.5*Imean_lowq: 
        #print('TRYING TO GET BETTER I0')
        idx_fit = ((q>0.06)&(q<0.1))
        I_at_0 = fit_I0(q[idx_fit],I[idx_fit],2)
    #elif flags['precursor_scattering']:
    #    I_at_0 = fit_I0(q,I,3)
    d['I_at_0'] = I_at_0

    #TODO: add parameters for diffraction peaks
    #if flags['diffraction_peaks']:
    #    .... 

    if flags['form_factor_scattering']:
        # TODO: insert cases for non-spherical form factors
        r0_sphere, sigma_sphere = spherical_normal_heuristics(
            np.array(zip(q,I)),I_at_0)
        #I_nz = np.invert((I<=0))
        #I_error = lambda x: np.sum( 
        #    (x*spherical_normal_saxs(q,r0_sphere,sigma_sphere) - I)**2 )
        #res = scipimin(I_error,[1E-6],bounds=[(0,None)])
        #I0_sphere = res.x[0]
        #I_sphere = I0_sphere*spherical_normal_saxs(q,r0_sphere,sigma_sphere)
        d['r0_sphere'] = r0_sphere
        d['sigma_sphere'] = sigma_sphere

    if flags['precursor_scattering']: 
        rg_pre, G_pre = precursor_heuristics(
            np.array(zip(q,I)))
        #idx_highq = (q > q[int(n_q*3./4)]) 
        #I_error = lambda x: np.sum( 
        #    (x*guinier_porod(q,rg_pre,4,G_pre)[idx_highq] - I[idx_highq])**2 )
        #res = scipimin(I_error,[1E-6],bounds=[(0,None)])
        #I0_pre = res.x[0]
        #I_pre = I0_pre*guinier_porod(q,rg_pre,4,G_pre)
        I_pre = guinier_porod(q,rg_pre,4,G_pre)
        d['rg_precursor'] = rg_pre 
        d['G_precursor'] = G_pre 

    #from matplotlib import pyplot as plt
    #plt.figure(1)
    #plt.plot(q,I)
    #plt.plot(q,I_sphere,'g')
    #plt.show()

    #I_floor = np.ones(n_q)
    #I_pre = np.zeros(n_q)
    #I_form = np.zeros(n_q)
    #if flags['precursor_scattering']: 
    #    I_pre = guinier_porod(q,rg_pre,4,G_pre)
    #if flags['form_factor_scattering']:
    #    I_form = spherical_normal_saxs(q,r0_sphere,sigma_sphere)
    #if flags['diffraction_peaks']:
    #   I_peaks = .....

    # Run a quick least-squares to get initial guesses for intensity prefactors
    #if flags['precursor_scattering'] and flags['form_factor_scattering']:
    #    x_init = [0.0,I_at_0]
    #    x_bounds = [(0.0,None),(1E-9,None)]
    #    Ifunc = lambda x: x[0]*I_floor + I_pre + x[1]*I_form 
    #elif flags['precursor_scattering']:
    #    x_init = [0.0]
    #    x_bounds = [(0.0,None)]
    #    Ifunc = lambda x: x[0]*I_floor + I_pre 
    f_pre = flags['precursor_scattering']
    f_form = flags['form_factor_scattering']
    f_pks = flags['diffraction_peaks']
    n_q = len(q)
    I_nz = np.invert((I<=0))
    if f_pre and f_form: 
        Ifunc = lambda x: x[0]*np.ones(n_q) \
            + guinier_porod(q,rg_pre,4,x[1]) \
            + x[2]*spherical_normal_saxs(q,r0_sphere,sigma_sphere) 
        I_error = lambda x: np.sum( (np.log(Ifunc(x)[I_nz]) - np.log(I[I_nz]))**2 )
        res = scipimin(I_error,[0.0,G_pre,I_at_0],
            bounds=[(0.0,None),(1E-6,None),(1E-6,None)],
            constraints=[{'type':'eq','fun':lambda x:np.sum(x)-I_at_0}])
        d['I0_floor'] = res.x[0]
        d['G_precursor'] = res.x[1]
        d['I0_sphere'] = res.x[2]
    elif f_pre:
        d['I0_floor'] = 0
        #Ifunc = lambda x: x[0]*np.ones(n_q) \
        #    + guinier_porod(q,rg_pre,4,x[1]) 
        #I_error = lambda x: np.sum( (np.log(Ifunc(x)[I_nz]) - np.log(I[I_nz]))**2 )
        #res = scipimin(I_error,[0.0,G_pre],bounds=[(0.0,None),(0.0,None)])
        #d['I0_floor'] = res.x[0]
        #d['G_precursor'] = res.x[1]
    elif f_form:
        I0_floor = np.mean(I[int(n_q*0.9):])
        d['I0_floor'] = I0_floor 
        d['I0_sphere'] = I_at_0 - I0_floor
        #Ifunc = lambda x: x[0]*np.ones(n_q) \
        #    + x[1]*spherical_normal_saxs(q,r0_sphere,sigma_sphere) 
        #I_error = lambda x: np.sum( (np.log(Ifunc(x)[I_nz]) - np.log(I[I_nz]))**2 )
        #res = scipimin(I_error,[0.0,I_at_0],bounds=[(0.0,None),(0.0,None)])
        #d['I0_floor'] = res.x[0]
        #d['I0_sphere'] = res.x[1]

        #if flags['precursor_scattering'] and flags['form_factor_scattering']:
        #    #I0_pre = res.x[1] 
        #    I0_sphere = res.x[2]
        #    #d['I0_precursor'] = I0_pre 
        #    d['I0_sphere'] = I0_sphere 
        #elif flags['precursor_scattering']:
        #    I0_pre = res.x[1]
        #    d['I0_precursor'] = I0_pre 
        #elif flags['form_factor_scattering']:
        #    I0_form = res.x[1]
        #    d['I0_sphere'] = I0_form 
        #d['I0_floor'] = I0_floor 
    I_guess = compute_saxs(q,flags,d)
    q_I_guess = np.array([q,I_guess]).T
    nz = ((I>0)&(I_guess>0))
    logI_nz = np.log(I[nz])
    logIguess_nz = np.log(I_guess[nz])
    Imean = np.mean(logI_nz)
    Istd = np.std(logI_nz)
    logI_nz_s = (logI_nz - Imean) / Istd
    logIguess_nz_s = (logIguess_nz - Imean) / Istd
    #d['R2log_guess'] = compute_Rsquared(logI_nz,logIguess_nz)
    #d['chi2log_guess'] = compute_chi2(logI_nz_s,logIguess_nz_s)
    return d

def fit_spectrum(q_I,flags,params,fixed_params,objective='chi2log'):
    """Fit a SAXS spectrum, given population flags and parameter guesses.

    Parameters
    ----------
    q_I : array
        n-by-2 array of scattering vector q (1/Angstrom) and intensity.
    flags : dict
        dictionary of flags indicating various scatterer populations.
    params : dict
        scattering equation parameters to use as intial condition for fitting.
    fixed_params : list
        list of keys (strings) indicating which entries in `params` 
        should be held constant during the optimization. 
    objective : str
        choice of objective function for the fitting. supported objectives:
        - 'chi2log': sum of difference of logarithm, squared, across entire q range. 
        - 'chi2log_fixI0': like chi2log, but with I(q=0) constrained. 

    Returns
    -------
    params_opt : dict
        Dict of scattering equation parameters 
        optimized to fit `q_I` under `objective`.
    """

    f_bd = flags['bad_data']
    f_pre = flags['precursor_scattering']
    f_form = flags['form_factor_scattering']
    f_pks = flags['diffraction_peaks']
    q = q_I[:,0]
    n_q = len(q)
    I = q_I[:,1]

    # trim non-flagged populations out of fit_params:
    # fit as few of the requested fit_params as possible
    #if not f_pre:
    #    if 'rg_precursor' in fit_params:
    #        fit_params.pop(fit_params.index('rg_precursor')) 
    #    if 'G_precursor' in fit_params:
    #        fit_params.pop(fit_params.index('G_precursor')) 
    #if not f_form:
    #    if 'I0_sphere' in fit_params:
    #        fit_params.pop(fit_params.index('I0_sphere')) 
    #    if 'r0_sphere' in fit_params:
    #        fit_params.pop(fit_params.index('r0_sphere')) 
    #    if 'sigma_sphere' in fit_params:
    #        fit_params.pop(fit_params.index('sigma_sphere')) 

    # index the params into an array 
    x_init = np.zeros(len(params))
    x_bounds = [] 
    I_keys = ['I0_floor','G_precursor','I0_sphere']
    p_idx = {} 
    I_idx = {} 
    for i,k in zip(range(len(params)),params.keys()):
        p_idx[k] = i 
        x_init[i] = params[k]
        if k in I_keys:
            I_idx[k] = i
        if k in ['rg_precursor','r0_sphere']:
            x_bounds.append((1E-3,None))
        elif k in ['G_precursor','I0_sphere','I0_floor']:
            x_bounds.append((0.0,None))
        elif k in ['sigma_sphere']:
            x_bounds.append((0.0,0.45))
        else:
            x_bounds.append((None,None))
    
    c = []
    if objective in ['chi2log_fixI0']:
        if len(I_idx) > 0:
            # Set up a constraint to keep I(q=0) fixed
            I0_init = np.sum([x_init[i] for i in I_idx])
            cfun = lambda x: np.sum([x[i] for i in I_idx] - I0_init)
            c.append({'type':'eq','fun':cfun})

    for fixk in fixed_params:
        cfun = lambda x: x[p_idx[fixk]] - params[fixk]
        c.append({'type':'eq','fun':cfun})

    p_opt = copy.deepcopy(params) 
    # Only proceed if there is work to do.
    if not f_pks and not f_bd:
        saxs_fun = lambda q,x,p: compute_saxs_with_substitutions(q,flags,p,params.keys(),x)
        if objective in ['chi2log','chi2log_fixI0']:
            #idx_fit = ((I>0)&(q>0.1))
            if f_pre and not f_form and not f_pks:
                # if we are fitting only precursors,
                # intensities should be relatively low,
                # so low-q region can be problematic. 
                # TODO: consider whether this special case is justified,
                # or come up with a better way to filter high-error low-q points
                idx_fit = ((I>0)&(np.arange(len(q))>n_q*1./4))
            else:
                idx_fit = (I>0)
            q_fit = q[idx_fit]
            I_fit = I[idx_fit]
            Imean_fit = np.mean(I_fit)
            Istd_fit = np.std(I_fit)
            Is_fit = (I_fit-Imean_fit)/Istd_fit
            fit_obj = lambda x: compute_chi2(
            (np.log(saxs_fun(q_fit,x,params))-Imean_fit)/Istd_fit , Is_fit)
        p_opt['objective_before'] = fit_obj(x_init)
        res = scipimin(fit_obj,x_init,
            method='SLSQP',bounds=x_bounds,
            options={'ftol':1E-3},constraints=c)
        p_opt['objective_after'] = fit_obj(res.x)
        for k,xk in zip(params.keys(),res.x):
            p_opt[k] = xk
        p_opt['fixed_params'] = fixed_params
        p_opt['objective'] = objective 

    #print('precursors: {}, spheres: {}, peaks: {}'.format(f_pre,f_form,f_pks))
    #print('params: {}'.format(d_opt))

    #I_guess = compute_saxs(q,flags,params) 
    #I_opt = compute_saxs(q,flags,d_opt) 
    
    #from matplotlib import pyplot as plt
    #plt.figure(2)
    #plt.plot(q,I)
    #plt.plot(q,I_guess,'r')
    #plt.plot(q,I_opt,'g')
    #plt.figure(12)
    #plt.semilogy(q,I)
    #plt.semilogy(q,I_guess,'r')
    #plt.semilogy(q,I_opt,'g')
    #plt.show()

    return p_opt    

        #if d_opt['objective_after'] > d_opt['objective_before']:
        #    print('WARNING: optimization has increased the objective function. why?')
        #    print('x_init: {}'.format(x_init))
        #    print('obj_init: {}'.format(d_opt['objective_before']))
        #    print('x_opt: {}'.format(x_opt))
        #    print('obj_opt: {}'.format(d_opt['objective_after']))
        #    x_opt = x_init


    #Supported objective functions: 
    #(1) 'chi2': sum of difference squared across entire q range. 
    #(3) 'chi2norm': sum of difference divided by measured value, squared, aross entire q range. 
    #(4) 'low_q_chi2': sum of difference squared in only the lowest half of measured q range. 
    #(5) 'low_q_chi2log': sum of difference of logarithm, squared, in lowest half of measured q range. 
    #(6) 'pearson': pearson correlation between measured and modeled spectra. 
    #(7) 'pearson_log': pearson correlation between logarithms of measured and modeled spectra.
    #(8) 'low_q_pearson': pearson correlation between measured and modeled spectra. 
    #(9) 'low_q_pearson_log': pearson correlation between logarithms of measured and modeled spectra. 

    #Supported constraints: 
    #(1) 'fix_I0': keeps I(q=0) fixed to the value specified in the input params.

    #TODO: document the objective functions, etc.
    #    I_nz = (I>0)
    #    n_q = len(q)
    #    idx_lowq = (q<0.4)
    #    if objfun == 'chi2':
    #        fit_obj = lambda x: compute_chi2(
    #        saxs_fun(q,x,params),I)
    #    elif objfun == 'chi2log':
    #        fit_obj = lambda x: compute_chi2(
    #        np.log(saxs_fun(q[I_nz],x,params)),
    #        np.log(I[I_nz]))
    #    elif objfun == 'chi2norm':
    #        fit_obj = lambda x: compute_chi2(
    #        saxs_fun(q[I_nz],x,params),
    #        I[I_nz] , weights=float(1)/I[I_nz])
    #    elif objfun == 'low_q_chi2':
    #        fit_obj = lambda x: compute_chi2(
    #        saxs_fun(q[idx_lowq],x,params),I[idx_lowq] )
    #    elif objfun == 'pearson':
    #        fit_obj = lambda x: -1*compute_pearson(
    #        saxs_fun(q,x,params),I)
    #    elif objfun == 'low_q_pearson':
    #        fit_obj = lambda x: -1*compute_pearson( 
    #        saxs_fun(q[idx_lowq],x,params),
    #        I[idx_lowq] )
    #    elif objfun == 'low_q_chi2log':
    #        fit_obj = lambda x: compute_chi2( 
    #        np.log(saxs_fun(q[I_nz][idx_lowq[I_nz]],x,params)), 
    #        np.log(I[I_nz][idx_lowq[I_nz]]) ) 
    #    elif objfun == 'pearson_log':
    #        fit_obj = lambda x: -1*compute_pearson( 
    #        np.log(saxs_fun(q[I_nz],x,params)),np.log(I[I_nz])) 
    #    elif objfun == 'low_q_pearson_log':
    #        fit_obj = lambda x: -1*compute_pearson( 
    #        np.log(saxs_fun(q[I_nz][idx_lowq[I_nz]],x,params)), 
    #        np.log(I[I_nz][idx_lowq[I_nz]]) ) 
    #    else:
    #        msg = 'objective function {} not supported'.format(objfun)
    #        raise ValueError(msg)
    #    #d_opt['R2log_fit'] = compute_Rsquared(np.log(I[I_nz]),np.log(I_opt[I_nz]))
    #    #d_opt['chi2log_fit'] = compute_chi2(logI_nz_s,logIopt_nz_s)
        #I_keys = []
        #if 'I0_floor' in fit_params:
        #    I_keys.append('I0_floor')
        #if 'G_precursor' in fit_params:
        #    I_keys.append('G_precursor')
        #if 'I0_sphere' in fit_params:
        #    I_keys.append('I0_sphere')
        ##if 'I0_structure' in fit_params:
        ##    I_keys.append('I0_structure')
        #if len(I_keys) == 0:
        #    # constraint inherently satisfied: do nothing.
        #    pass
        #elif len(I_keys) == 1:
        #    # satisfy constraint by removing this key from fit_params. 
        #    fit_params.pop(fit_params.index(I_keys[0])) 
        #else:
        #    # find the indices of the relevant fit_params and form a constraint function.
        #    iargs = []
        #    Icons = 0
        #    for ik,k in zip(range(len(fit_params)),fit_params):
        #        if k in I_keys:
        #            iargs.append(ik)
        #            Icons += params[k]
        #    # Constrain I(q=0) to be fixed during fit
        #    #constraints=[{'type':'eq','fun':lambda x:np.sum(x)-I_at_0}]) 
        #    cfun = lambda x: sum([x[i] for i in iargs]) - Icons 
        #    c_fixI0 = {'type':'eq','fun':cfun}
        #    x_constraints.append(c_fixI0)

def precursor_heuristics(q_I):
    """Guess radius of gyration and Guinier prefactor of scatterers.

    Parameters
    ----------
    q_I : array
        n-by-2 array of q (scattering vector magnitude) 
        and I (intensity at q)

    Returns
    -------
    rg_pre : float
        estimated radius of gyration 
    G_pre : float
        estimated Guinier factor
    """
    n_q = len(q_I[:,0])
    ## use the higher-q regions 
    highq_I = q_I[int(n_q*1./2):,:] 
    #highq_I = q_I[int(n_q*3./4):,:] 
    fit_obj = lambda x: fit_guinier_porod(highq_I,x[0],4,x[1])
    idx_nz = highq_I[:,1]>0
    #fit_obj = lambda x: -1*compute_pearson(
    #    np.log(guinier_porod(highq_I[idx_nz,0],x[0],4,x[1])),
    #    np.log( highq_I[idx_nz,1]) )
    ##res = scipimin(fit_ojb,[0.1],bounds=[(0,0.3)]) 
    res = scipimin(fit_obj,[1,1],bounds=[(1E-3,10),(1E-3,None)])
    rg_opt, G_opt = res.x
    I_pre = guinier_porod(q_I[:,0],rg_opt,4,G_opt)
    return rg_opt, G_opt

def fit_guinier_porod(q_I,rg,porod_exp,G):
    #I_mean = np.mean(q_I[:,1])
    #I_std = np.std(q_I[:,1])
    #I_max = np.max(q_I[:,1])
    #I_s = q_I[:,1] / I_max
    Igp = guinier_porod(q_I[:,0],rg,porod_exp,G)
    #Igp_s = (Igp-np.mean(Igp)) / np.std(Igp)
    return np.sum( (q_I[:,1]-Igp)**2 )

def spherical_normal_heuristics(q_I,I_at_0):
    """Guess mean and std of radii for spherical scatterers.

    This algorithm was developed and 
    originally contributed by Amanda Fournier.    

    Performs some heuristic measurements on the input spectrum,
    in order to make educated guesses 
    for the parameters of a size distribution
    (mean and standard deviation of radius)
    for a population of spherical scatterers.

    TODO: Document algorithm here.
    """
    m = saxs_Iq4_metrics(q_I)

    width_metric = m['pI_qwidth']/m['q_at_Iqqqq_min1']
    intensity_metric = m['I_at_Iqqqq_min1']/I_at_0
    #######
    #
    # The function spherical_normal_heuristics_setup()
    # (in this same module) should be used to regenerate these polynomials
    # if any part of saxs_Iq4_metrics() is changed.
    # polynomial coefs for qr0 focus: 
    p_f = [16.86239254,8.85709143,-11.10439599,-0.26735688,4.49884714]
    # polynomial coefs for width metric: 
    p_w = [12.42148677,-16.85723287,7.43401497,-0.38234993,0.06203096]
    # polynomial coefs for intensity metric: 
    p_I = [1.19822603,-1.20386273,2.88652860e-01,1.78677430e-02,-2.67888841e-04]
    #
    #######
    # Find the sigma_r/r0 value that gets the extracted metrics
    # as close as possible to p_I and p_w.
    width_error = lambda x: (np.polyval(p_w,x)-width_metric)**2
    intensity_error = lambda x: (np.polyval(p_I,x)-intensity_metric)**2
    # TODO: make the objective function weight all errors equally
    heuristics_error = lambda x: width_error(x) + intensity_error(x)
    res = scipimin(heuristics_error,[0.1],bounds=[(0,0.45)]) 
    sigma_over_r = res.x[0]
    qr0_focus = np.polyval(p_f,sigma_over_r)
    # qr0_focus = x1  ==>  r0 = x1 / q1
    r0 = qr0_focus/m['q_at_Iqqqq_min1']
    #print('r0: {}, sigma/r: {}'.format(r0,sigma_over_r))
    return r0,sigma_over_r

def saxs_Iq4_metrics(q_I):
    """
    From an input spectrum q and I(q),
    compute several properties of the I(q)*q^4 curve.
    This was designed for spectra that are 
    dominated by a dilute spherical form factor term.
    The metrics extracted by this Operation
    were originally intended as an intermediate step
    for estimating size distribution parameters 
    for a population of dilute spherical scatterers.

    Returns a dict of metrics.
    Dict keys and meanings:
    q_at_Iqqqq_min1: q value at first minimum of I*q^4
    I_at_Iqqqq_min1: I value at first minimum of I*q^4
    Iqqqq_min1: I*q^4 value at first minimum of I*q^4
    pIqqqq_qwidth: Focal q-width of polynomial fit to I*q^4 near first minimum of I*q^4 
    pIqqqq_Iqqqqfocus: Focal point of polynomial fit to I*q^4 near first minimum of I*q^4
    pI_qvertex: q value of vertex of polynomial fit to I(q) near first minimum of I*q^4  
    pI_Ivertex: I(q) at vertex of polynomial fit to I(q) near first minimum of I*q^4
    pI_qwidth: Focal q-width of polynomial fit to I(q) near first minimum of I*q^4
    pI_Iforcus: Focal point of polynomial fit to I(q) near first minimum of I*q^4

    TODO: document the algorithm here.
    """
    q = q_I[:,0]
    I = q_I[:,1]
    d = {}
    #if not dI:
    #    # uniform weights
    #    wt = np.ones(q.shape)   
    #else:
    #    # inverse error weights, 1/dI, 
    #    # appropriate if dI represents
    #    # Gaussian uncertainty with sigma=dI
    #    wt = 1./dI
    #######
    # Heuristics step 1: Find the first local max
    # and subsequent local minimum of I*q**4 
    Iqqqq = I*q**4
    # w is the number of adjacent points to consider 
    # when examining the I*q^4 curve for local extrema.
    # A greater value of w filters out smaller extrema.
    w = 10
    idxmax1, idxmin1 = 0,0
    stop_idx = len(q)-w-1
    test_range = iter(range(w,stop_idx))
    idx = test_range.next() 
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
        raise RuntimeError(ex_msg)
    #######
    # Heuristics 2: Characterize I*q**4 around idxmin1, 
    # by locally fitting a standardized polynomial.


    idx_around_min1 = (q>0.9*q[idxmin1]) & (q<1.1*q[idxmin1])
    # keep only the lower-q side, to encourage upward curvature
    #idx_around_min1 = (q>0.8*q[idxmin1]) & (q<q[idxmin1])


    q_min1_mean = np.mean(q[idx_around_min1])
    q_min1_std = np.std(q[idx_around_min1])
    q_min1_s = (q[idx_around_min1]-q_min1_mean)/q_min1_std
    Iqqqq_min1_mean = np.mean(Iqqqq[idx_around_min1])
    Iqqqq_min1_std = np.std(Iqqqq[idx_around_min1])
    Iqqqq_min1_s = (Iqqqq[idx_around_min1]-Iqqqq_min1_mean)/Iqqqq_min1_std
    #Iqqqq_min1_quad = lambda x: np.sum((x[0]*q_min1_s**2 + x[1]*q_min1_s + x[2] - Iqqqq_min1_s)**2)
    #res = scipimin(Iqqqq_min1_quad,[1E-3,0,0],bounds=[(0,None),(None,None),(None,None)])
    #p_min1 = res.x
    p_min1 = np.polyfit(q_min1_s,Iqqqq_min1_s,2,None,False,np.ones(len(q_min1_s)),False)
    # polynomial vertex horizontal coord is -b/2a
    qs_at_min1 = -1*p_min1[1]/(2*p_min1[0])
    d['q_at_Iqqqq_min1'] = qs_at_min1*q_min1_std+q_min1_mean
    # polynomial vertex vertical coord is poly(-b/2a)
    Iqqqqs_at_min1 = np.polyval(p_min1,qs_at_min1)
    d['Iqqqq_min1'] = Iqqqqs_at_min1*Iqqqq_min1_std+Iqqqq_min1_mean
    d['I_at_Iqqqq_min1'] = d['Iqqqq_min1']*float(1)/(d['q_at_Iqqqq_min1']**4)
    # The focal width of the parabola is 1/a 
    p_min1_fwidth = abs(1./p_min1[0])
    d['pIqqqq_qwidth'] = p_min1_fwidth*q_min1_std
    # The focal point is at -b/2a,poly(-b/2a)+1/(4a)
    p_min1_fpoint = Iqqqqs_at_min1+float(1)/(4*p_min1[0])
    d['pIqqqq_Iqqqqfocus'] = p_min1_fpoint*Iqqqq_min1_std+Iqqqq_min1_mean
    #######
    # Heuristics 2b: Characterize I(q) near min1 of I*q^4.
    I_min1_mean = np.mean(I[idx_around_min1])
    I_min1_std = np.std(I[idx_around_min1])
    I_min1_s = (I[idx_around_min1]-I_min1_mean)/I_min1_std
    #I_min1_error = lambda x: np.sum((x[0]*q_min1_s**2 + x[1]*q_min1_s + x[2] - I_min1_s)**2)
    #res = scipimin(I_min1_error,[0,0,0],bounds=[(0,None),(None,None),(None,None)])
    #pI_min1 = res.x
    pI_min1 = np.polyfit(q_min1_s,I_min1_s,2,None,False,np.ones(len(q_min1_s)),False)
    # polynomial vertex horizontal coord is -b/2a
    qs_vertex = -1*pI_min1[1]/(2*pI_min1[0])
    d['pI_qvertex'] = qs_vertex*q_min1_std+q_min1_mean
    # polynomial vertex vertical coord is poly(-b/2a)
    Is_vertex = np.polyval(pI_min1,qs_vertex)
    d['pI_Ivertex'] = Is_vertex*I_min1_std+I_min1_mean
    # The focal width of the parabola is 1/a 
    pI_fwidth = abs(1./pI_min1[0])
    d['pI_qwidth'] = pI_fwidth*q_min1_std
    # The focal point is at -b/2a,poly(-b/2a)+1/(4a)
    pI_fpoint = Is_vertex+float(1)/(4*pI_min1[0])
    d['pI_Ifocus'] = pI_fpoint*I_min1_std+I_min1_mean
    #######
    return d

def compute_saxs_with_substitutions(q,flags,params,x_keys,x_vals):
    p_sub = copy.deepcopy(params)
    for k,v in zip(x_keys,x_vals):
        p_sub[k] = copy.copy(v)
    return compute_saxs(q,flags,p_sub)

def compute_chi2(y1,y2,weights=None):
    """
    Compute the sum of the difference squared between input arrays y1 and y2.
    """
    if weights is None:
        return np.sum( (y1 - y2)**2 )
    else:
        weights = weights / np.sum(weights)
        return np.sum( (y1 - y2)**2*weights )

def compute_Rsquared(y1,y2):
    """
    Compute the coefficient of determination between input arrays y1 and y2.
    """
    sum_var = np.sum( (y1-np.mean(y1))**2 )
    sum_res = np.sum( (y1-y2)**2 ) 
    return float(1)-float(sum_res)/sum_var

def compute_pearson(y1,y2):
    """
    Compute the Pearson correlation coefficient between input arrays y1 and y2.
    """
    y1mean = np.mean(y1)
    y2mean = np.mean(y2)
    y1std = np.std(y1)
    y2std = np.std(y2)
    return np.sum((y1-y1mean)*(y2-y2mean))/(np.sqrt(np.sum((y1-y1mean)**2))*np.sqrt(np.sum((y2-y2mean)**2)))

def fit_I0(q,I,order=4):
    """
    Find an estimate for I(q=0) by polynomial fitting.
    All of the input q, I(q) values are used in the fitting.
    """
    #TODO: add a sign constraint, at least
    I_mean = np.mean(I)
    I_std = np.std(I)
    q_mean = np.mean(q)
    q_std = np.std(q)
    I_s = (I-I_mean)/I_std
    q_s = (q-q_mean)/q_std
    p = fit_with_slope_constraint(q_s,I_s,-1*q_mean/q_std,0,order) 
    I_at_0 = np.polyval(p,-1*q_mean/q_std)*I_std+I_mean
    return I_at_0

def fit_with_slope_constraint(q,I,q_cons,dIdq_cons,order,weights=None):
    """
    Perform a polynomial fitting 
    of the low-q region of the spectrum
    with dI/dq(q=0) constrained to be zero.
    This is performed by forming a Lagrangian 
    from a quadratic cost function 
    and the Lagrange-multiplied constraint function.
    
    TODO: Explicitly document cost function, constraints, Lagrangian.

    Inputs q and I are not standardized in this function,
    so they should be standardized beforehand 
    if standardized fitting is desired.
    At the provided constraint point, q_cons, 
    the returned polynomial will have slope dIdq_cons.

    Because of the form of the Lagrangian,
    this constraint cannot be placed at exactly zero.
    This would result in indefinite matrix elements.
    """
    Ap = np.zeros( (order+1,order+1),dtype=float )
    b = np.zeros(order+1,dtype=float)
    # TODO: vectorize the construction of Ap
    for i in range(0,order):
        for j in range(0,order):
            Ap[i,j] = np.sum( q**j * q**i )
        Ap[i,order] = -1*i*q_cons**(i-1)
    for j in range(0,order):
        Ap[order,j] = j*q_cons**(j-1)
        b[j] = np.sum(I*q**j)
    b[order] = dIdq_cons
    p_fit = np.linalg.solve(Ap,b) 
    p_fit = p_fit[:-1]  # throw away Lagrange multiplier term 
    p_fit = p_fit[::-1] # reverse coefs to get np.polyfit format
    #from matplotlib import pyplot as plt
    #plt.figure(3)
    #plt.plot(q,I)
    #plt.plot(q,np.polyval(p_fit,q))
    #plt.plot(np.arange(q_cons,q[-1],q[-1]/100),np.polyval(p_fit,np.arange(q_cons,q[-1],q[-1]/100)))
    #plt.plot(q_cons,np.polyval(p_fit,q_cons),'ro')
    #plt.show()
    return p_fit
 
def spherical_normal_heuristics_setup():
    sigma_over_r = []
    width_metric = []
    intensity_metric = []
    qr0_focus = []
    # TODO: generate heuristics on a 1-d grid of sigma/r
    # instead of the 2-d grid being used here now.
    # Document proof that a 1-d grid is sufficient.
    #r0_vals = np.arange(10,41,10,dtype=float)              #Angstrom
    #for ir,r0 in zip(range(len(r0_vals)),r0_vals):
    r0 = 10
    q = np.arange(0.001/r0,float(20)/r0,0.001/r0)       #1/Angstrom
    # NOTE: algorithm works for sigma/r up to 0.45
    sigma_r_vals = np.arange(0*r0,0.46*r0,0.01*r0)      #Angstrom
    for isig,sigma_r in zip(range(len(sigma_r_vals)),sigma_r_vals):
        I = spherical_normal_saxs(q,r0,sigma_r/r0) 
        I_at_0 = spherical_normal_saxs(np.array([0]),r0,sigma_r/r0)[0] 
        print('getting I*q**4 metrics for sigma_r/r0 = {}'.format(sigma_r/r0))
        d = saxs_Iq4_metrics(np.array(zip(q,I)))
        sigma_over_r.append(float(sigma_r)/r0)
        qr0_focus.append(d['q_at_Iqqqq_min1']*r0)
        width_metric.append(d['pI_qwidth']/d['q_at_Iqqqq_min1'])
        intensity_metric.append(d['I_at_Iqqqq_min1']/I_at_0)
    # TODO: standardize before fitting, then revert after
    p_f = np.polyfit(sigma_over_r,qr0_focus,4,None,False,None,False)
    p_w = np.polyfit(sigma_over_r,width_metric,4,None,False,None,False)
    p_I = np.polyfit(sigma_over_r,intensity_metric,4,None,False,None,False)
    print('polynomial coefs for qr0 focus: {}'.format(p_f))
    print('polynomial coefs for width metric: {}'.format(p_w))
    print('polynomial coefs for intensity metric: {}'.format(p_I))
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
        plt.plot(sigma_over_r,np.polyval(p_f,sigma_over_r))
        plt.figure(4)
        plt.scatter(width_metric,intensity_metric) 
        plt.show()



