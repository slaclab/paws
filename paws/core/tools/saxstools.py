from __future__ import print_function
from collections import OrderedDict
import copy

import numpy as np
from scipy.optimize import minimize as scipimin

def compute_saxs(q,flags,params):
    """
    Given q, a dict of population flags,
    and a dict of scattering equation parameters,
    compute the saxs spectrum.
    Supported parameters are... TODO: fill in 

    TODO: Document the equation.
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
            # TODO: This should employ a Guinier-Porod or similar equation
            I0_pre = params['I0_precursor']
            r0_pre = params['r0_precursor']
            I_pre = compute_spherical_normal_saxs(q,r0_pre,0)
            I += I0_pre*I_pre
        if f_flag:
            # TODO: support non-spherical form factors 
            I0_sph = params['I0_sphere']
            r0_sph = params['r0_sphere']
            sigma_sph = params['sigma_sphere']
            I_sph = compute_spherical_normal_saxs(q,r0_sph,sigma_sph)
            I += I0_sph*I_sph
    return I

def profile_spectrum(q,I):
    """
    Profile a saxs spectrum (q,I) 
    by taking several fast numerical metrics 
    from the measured data.

    Returns a dictionary of scalar metrics.
    Dict keys and descriptions:
    'low_q_ratio': fraction of total intensity in the range q<0.4
    'high_q_ratio': fraction of total intensity in the range q>=0.4
    'q_Imax': q value of the maximum intensity.
    'Imax_over_Imean': maximum intensity divided by mean intensity.
    'Imax_over_Ilowq': Maximum intensity divided by mean intensity in the range q<0.4.
    'Imax_over_Ihighq': Maximum intensity divided by mean intensity in the range q>0.4.
    'Imax_sharpness': maximum intensity divided by the mean intensity in the range 0.9*q_Imax<q<1.1*q_Imax.
    'q_bin_edges' : array of q-values to use as upper bin limits for intensity integration.
    'q_bin_strengths' : array of integrated log(I) within the bins specified by q_bin_edges.
    'log_fluctuation': Integrated fluctuation of log(I):
    sum of difference in log(I) between adjacent points,
    taken only where this difference changes sign, divided by the maximum of log(I).
    """ 

    idx_lowq = np.array(q<0.4)
    idx_highq = np.array(q>=0.4)
    # log(I) analysis
    nz = I>0
    q_nz = q[nz]
    I_nz = I[nz]
    logI_nz = np.log(I_nz)
    logI_max = np.max(logI_nz)
    # I analysis
    I_sum = np.sum(I)
    I_mean = np.mean(I)
    I_lowq_mean = np.mean(I[idx_lowq])
    I_highq_mean = np.mean(I[idx_highq])
    idxmax = np.argmax(I)
    idxmin = np.argmin(I)
    Imin = I[idxmin]
    Imax = I[idxmax] 
    q_Imax = q[idxmax]
    Irange = Imax - Imin
    # I_max peak shape analysis
    idx_around_max = ((q > 0.9*q_Imax) & (q < 1.1*q_Imax))
    Imean_around_max = np.mean(I[idx_around_max])
    Imax_sharpness = Imax / Imean_around_max
    # low-q and high-q intensity integration
    dq = q[1:] - q[:-1]
    I_trap = (I[1:]+I[:-1])/2
    I_integral = np.sum(dq*I_trap)
    dq_lowq = q[idx_lowq][1:] - q[idx_lowq][:-1]
    I_trap_lowq = (I[idx_lowq][1:]+I[idx_lowq][:-1])/2
    I_lowq_integral = np.sum(dq_lowq*I_trap_lowq)
    dq_highq = q[idx_highq][1:] - q[idx_highq][:-1]
    I_trap_highq = (I[idx_highq][1:]+I[idx_highq][:-1])/2
    I_highq_integral = np.sum(dq_highq*I_trap_highq)
    # I_max relative intensity analysis
    low_q_ratio = I_lowq_integral / I_integral 
    high_q_ratio = I_highq_integral / I_integral
    Imax_over_Imean = Imax/I_mean
    Imax_over_Ilowq = Imax/I_lowq_mean
    Imax_over_Ihighq = Imax/I_highq_mean

    ### fluctuation analysis
    # array of the difference between neighboring points:
    nn_diff = logI_nz[1:]-logI_nz[:-1]
    # keep indices where the sign of this difference changes.
    # also keep first index
    nn_diff_prod = nn_diff[1:]*nn_diff[:-1]
    idx_keep = np.hstack((np.array([True]),nn_diff_prod<0))
    fluc = np.sum(np.abs(nn_diff[idx_keep]))
    log_fluctuation = fluc/logI_max

    ### bin-integrated log(intensity) analysis
    nbins = 100
    qbinmax = float(1.)
    qbinstep = qbinmax/nbins
    q_bin_edges = np.arange(qbinstep,qbinmax+qbinstep,qbinstep)
    q_bin_strengths = np.zeros(q_bin_edges.shape) 
    binfloor = 0
    for ibin,binmax in zip(range(nbins),q_bin_edges):
        binidx = ((q>=binfloor) & (q<binmax))
        if any(binidx):
            qbin = q[ binidx ]
            Ibin = I[ binidx ]
            dqbin = qbin[1:]-qbin[:-1]
            Ibin = (Ibin[1:]+Ibin[:-1])/2
            q_bin_strengths[ibin] = np.sum(Ibin * dqbin) / I_integral 
        binfloor = binmax
    d = OrderedDict()
    d['q_Imax'] = q_Imax
    d['Imax_over_Imean'] = Imax_over_Imean
    d['Imax_over_Ilowq'] = Imax_over_Ilowq 
    d['Imax_over_Ihighq'] = Imax_over_Ihighq 
    d['Imax_sharpness'] = Imax_sharpness
    d['low_q_ratio'] = low_q_ratio 
    d['high_q_ratio'] = high_q_ratio 
    d['q_bin_edges'] = q_bin_edges
    d['log_fluctuation'] = log_fluctuation
    d['q_bin_strengths'] = q_bin_strengths 
    return d

def parameterize_spectrum(q,I,flags,fixed_params={}):
    """
    Determine a parameterization for a scattering equation,
    beginning with the measured spectrum (q,I) 
    and a dict of population flags. 
    Returns a dict containing the input population flags
    along with initial guesses for the scattering equation parameters
    corresponding to the flagged populations.
    """
    fix_keys = fixed_params.keys()
    d = OrderedDict()
    if flags['bad_data']:
        # stop
        return d 
    else:
        # Get a number for I(q=0)
        if flags['form_factor_scattering']:
            # If form factor scattering, fit 3rd order, use q<0.06. 
            idx_lowq = (q<0.06)
            # Disregard lowest-q values if they are far from the mean, 
            # as these points are likely dominated by experimental error.
            Imean_lowq = np.mean(I[idx_lowq])
            Istd_lowq = np.std(I[idx_lowq])
            idx_good = ((I[idx_lowq] < Imean_lowq+Istd_lowq) & (I[idx_lowq] > Imean_lowq-Istd_lowq))
            I_at_0 = fit_I0(q[idx_lowq][idx_good],I[idx_lowq][idx_good],3)
        elif flags['diffraction_peaks']:
            # If diffraction without form factor scattering, 
            # fit 2nd order, use q<0.06. 
            idx_lowq = (q<0.06)
            I_at_0 = fit_I0(q[idx_lowq],I[idx_lowq],3)
        elif flags['precursor_scattering']:
            # If only precursor scattering, fit third order for entire q-range 
            I_at_0 = fit_I0(q,I,3)
        d['I_at_0'] = I_at_0

    if flags['diffraction_peaks']:
        d['ERROR_MESSAGE']='diffraction peak parameterization not yet supported'
        return d

    if flags['form_factor_scattering']:
        # TODO: insert cases for non-spherical form factors
        #if flags['form_factor_id'] == 'sphere':
            if ('r0_sphere' in fix_keys and 'sigma_sphere' in fix_keys):
                r0_sphere = fixed_params['r0_sphere']
                sigma_sphere = fixed_params['sigma_sphere']
            else:
                # get at least one of r0_sphere or sigma_sphere from spherical_normal_heuristics()
                r0_sphere, sigma_sphere = spherical_normal_heuristics(q,I,I_at_0=I_at_0)
                if 'r0_sphere' in fix_keys:
                    r0_sphere = fixed_params['r0_sphere']
                if 'sigma_sphere' in fix_keys:
                    sigma_sphere = fixed_params['sigma_sphere']
            d['r0_sphere'] = r0_sphere
            d['sigma_sphere'] = sigma_sphere
    
    if flags['precursor_scattering']: 
        if 'r0_precursor' in fix_keys:
            r0_pre = fixed_params['r0_precursor']
        else:
            # TODO: This should employ a Guinier-Porod or similar fit
            # TODO: This approach will have to respect whatever other populations are flagged. 
            r0_pre = precursor_heuristics(q,I,I_at_0=I_at_0)
        d['r0_precursor'] = r0_pre 

    I_floor = np.ones(len(q))
    # include other terms conditionally
    if flags['precursor_scattering']: 
        # TODO: This should be a Guinier-Porod or similar fit
        I_pre = compute_spherical_normal_saxs(q,r0_pre,0)
    if flags['form_factor_scattering']:
        #if flags['form_factor_id'] == 'sphere':
        # TODO: form factors other than sphere
        I_form = compute_spherical_normal_saxs(q,r0_sphere,sigma_sphere)
    #if flags['diffraction_peaks']:
    #   I_structure = .....

    # Run a quick least-squares to get initial guesses for intensity prefactors
    if flags['precursor_scattering'] and flags['form_factor_scattering']:
        x_init = [I_at_0,0.0,0.0]
        x_bounds = [(0.0,None),(0.0,None),(0.0,None)]
        Ifunc = lambda x: x[0]*I_floor + x[1]*I_pre + x[2]*I_form 
    elif flags['precursor_scattering']:
        x_init = [I_at_0,0.0]
        x_bounds = [(0.0,None),(0.0,None)]
        Ifunc = lambda x: x[0]*I_floor + x[1]*I_pre 
    elif flags['form_factor_scattering']:
        x_init = [I_at_0,0.0]
        x_bounds = [(0.0,None),(0.0,None)]
        Ifunc = lambda x: x[0]*I_floor + x[1]*I_form 
    if flags['precursor_scattering'] or flags['form_factor_scattering']:
        I_nz = np.invert((I<=0))
        I_error = lambda x: np.sum( (np.log(Ifunc(x))[I_nz] - np.log(I[I_nz]))**2 )
        res = scipimin(I_error,x_init,bounds=x_bounds,
        constraints=[{'type':'eq','fun':lambda x:np.sum(x)-I_at_0}]) 
        x_res = res.x
        I0_floor = x_res[0]
        if flags['precursor_scattering'] and flags['form_factor_scattering']:
            I0_pre = x_res[1] 
            I0_sphere = x_res[2]
            d['I0_precursor'] = I0_pre 
            d['I0_sphere'] = I0_sphere 
        elif flags['precursor_scattering']:
            I0_pre = x_res[1]
            d['I0_precursor'] = I0_pre 
        elif flags['form_factor_scattering']:
            I0_form = x_res[1]
            d['I0_sphere'] = I0_form 
        d['I0_floor'] = I0_floor 

    #TODO: add parameters for diffraction peaks

    I_guess = compute_saxs(q,flags,d)
    q_I_guess = np.array([q,I_guess]).T
    nz = ((I>0)&(I_guess>0))
    logI_nz = np.log(I[nz])
    logIguess_nz = np.log(I_guess[nz])
    Imean = np.mean(logI_nz)
    Istd = np.std(logI_nz)
    logI_nz_s = (logI_nz - Imean) / Istd
    logIguess_nz_s = (logIguess_nz - Imean) / Istd
    d['R2log_guess'] = compute_Rsquared(logI_nz,logIguess_nz)
    d['chi2log_guess'] = compute_chi2(logI_nz_s,logIguess_nz_s)
    return d

def fit_spectrum(q,I,objfun,flags,params,fit_params,constraints=[]):
    """
    Fit a saxs spectrum (I(q) vs q) to the theoretical spectrum 
    for one or several scattering populations.
    Input objfun (string) specifies objective function to use in optimization.
    Inputs flags (dict) and params (dict) describe flagged scatterer populations
    and initial guesses for the corresponding parameters for the scattering equation.
    Input fit_params (list of strings) indicate the parameters that will be optimized. 
    Input constraints (list of strings) to specify constraints.
    
    Supported objective functions: 
    (1) 'chi2': sum of difference squared across entire q range. 
    (2) 'chi2log': sum of difference of logarithm, squared, across entire q range. 
    (3) 'chi2norm': sum of difference divided by measured value, squared, aross entire q range. 
    (4) 'low_q_chi2': sum of difference squared in only the lowest half of measured q range. 
    (5) 'low_q_chi2log': sum of difference of logarithm, squared, in lowest half of measured q range. 
    (6) 'pearson': pearson correlation between measured and modeled spectra. 
    (7) 'pearson_log': pearson correlation between logarithms of measured and modeled spectra.
    (8) 'low_q_pearson': pearson correlation between measured and modeled spectra. 
    (9) 'low_q_pearson_log': pearson correlation between logarithms of measured and modeled spectra. 

    Supported constraints: 
    (1) 'fix_I0': keeps I(q=0) fixed to the value specified in the input params.

    TODO: document the objective functions, etc.
    """
    pre_flag = flags['precursor_scattering']
    form_flag = flags['form_factor_scattering']
    structure_flag = flags['diffraction_peaks']

    fit_params = copy.deepcopy(fit_params)
    # trim non-flagged populations out of fit_params:
    # fit as few of the requested fit_params as possible
    if not pre_flag:
        if 'I0_precursor' in fit_params:
            fit_params.pop(fit_params.index('I0_precursor')) 
        if 'r0_precursor' in fit_params:
            fit_params.pop(fit_params.index('r0_precursor')) 
    if not form_flag:
        if 'I0_sphere' in fit_params:
            fit_params.pop(fit_params.index('I0_sphere')) 
        if 'r0_sphere' in fit_params:
            fit_params.pop(fit_params.index('r0_sphere')) 
        if 'sigma_sphere' in fit_params:
            fit_params.pop(fit_params.index('sigma_sphere')) 
    #if not structure_flag:
    #    if 'I0_structure' in fit_params:
    #        fit_params.pop(fit_params.index('I0_structure')) 
    #    if 'q0_structure' in fit_params:
    #        fit_params.pop(fit_params.index('q0_structure')) 
    #    if 'sigma_structure' in fit_params:
    #        fit_params.pop(fit_params.index('sigma_structure')) 

    c = []
    if 'fix_I0' in constraints: 
        I_keys = []
        if 'I0_floor' in fit_params:
            I_keys.append('I0_floor')
        if 'I0_precursor' in fit_params:
            I_keys.append('I0_precursor')
        if 'I0_sphere' in fit_params:
            I_keys.append('I0_sphere')
        #if 'I0_structure' in fit_params:
        #    I_keys.append('I0_structure')
        if len(I_keys) == 0:
            # constraint inherently satisfied: do nothing.
            pass
        elif len(I_keys) == 1:
            # satisfy constraint by removing this key from fit_params. 
            fit_params.pop(fit_params.index(I_keys[0])) 
        else:
            # find the indices of the relevant fit_params and form a constraint function.
            iargs = []
            Icons = 0
            for ik,k in zip(range(len(fit_params)),fit_params):
                if k in I_keys:
                    iargs.append(ik)
                    Icons += params[k]
            cfun = lambda x: sum([x[i] for i in iargs]) - Icons 
            c_fixI0 = {'type':'eq','fun':cfun}
            c.append(c_fixI0)

    x_init = [] 
    x_bounds = [] 
    for k in fit_params:
        x_init.append(params[k])
        if k in ['r0_precursor','r0_sphere']:
            x_bounds.append((1E-3,None))
        elif k in ['I0_precursor','I0_sphere','I0_floor']:
            x_bounds.append((0.0,None))
        elif k in ['sigma_sphere']:
            x_bounds.append((0.0,0.5))

    d_opt = copy.deepcopy(params) 
    x_opt = []
    # Only proceed if there is still work to do.
    if any(x_init):
        saxs_fun = lambda q,x,d: compute_saxs_with_substitutions(q,flags,d,fit_params,x)
        I_nz = (I>0)
        n_q = len(q)
        idx_lowq = (q<0.4)
        if objfun == 'chi2':
            fit_obj = lambda x: compute_chi2( saxs_fun(q,x,params) , I )
        elif objfun == 'chi2log':
            fit_obj = lambda x: compute_chi2( np.log(saxs_fun(q[I_nz],x,params)) , np.log(I[I_nz]) )
        elif objfun == 'chi2norm':
            fit_obj = lambda x: compute_chi2( saxs_fun(q[I_nz],x,params) , I[I_nz] , weights=float(1)/I[I_nz] )
        elif objfun == 'low_q_chi2':
            fit_obj = lambda x: compute_chi2( saxs_fun(q[idx_lowq],x,params) , I[idx_lowq] )
        elif objfun == 'pearson':
            fit_obj = lambda x: -1*compute_pearson( saxs_fun(q,x,params) , I )
        elif objfun == 'low_q_pearson':
            fit_obj = lambda x: -1*compute_pearson( saxs_fun(q[idx_lowq],x,params) , I[idx_lowq] )
        elif objfun == 'low_q_chi2log':
            fit_obj = lambda x: compute_chi2( np.log(saxs_fun(q[I_nz][idx_lowq[I_nz]],x,params)) , np.log(I[I_nz][idx_lowq[I_nz]]) ) 
        elif objfun == 'pearson_log':
            fit_obj = lambda x: -1*compute_pearson( np.log(saxs_fun(q[I_nz],x,params)) , np.log(I[I_nz]) ) 
        elif objfun == 'low_q_pearson_log':
            fit_obj = lambda x: -1*compute_pearson( np.log(saxs_fun(q[I_nz][idx_lowq[I_nz]],x,params)) , np.log(I[I_nz][idx_lowq[I_nz]]) ) 
        else:
            msg = 'objective function {} not supported'.format(objfun)
            raise ValueError(msg)
        d_opt['objective_before'] = fit_obj(x_init)
        #try:
        res = scipimin(fit_obj,x_init,bounds=x_bounds,constraints=c)
        #except:
        x_opt = res.x
        d_opt['objective_after'] = fit_obj(x_opt)
        if d_opt['objective_after'] > d_opt['objective_before']:
            print('WARNING: optimization has increased the objective function. why?')
            print('x_init: {}'.format(x_init))
            print('obj_init: {}'.format(d_opt['objective_before']))
            print('x_opt: {}'.format(x_opt))
            print('obj_opt: {}'.format(d_opt['objective_after']))
            x_opt = x_init
        for k,xk in zip(fit_params,x_opt):
            d_opt[k] = xk
    return d_opt    

def compute_spherical_normal_saxs(q,r0,sigma):
    """
    Given q, a mean radius r0, 
    and the fractional standard deviation of radius sigma,
    compute the saxs spectrum assuming spherical particles 
    with normal size distribution.
    The returned intensity is normalized 
    such that I(q=0) is equal to 1.
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

def precursor_heuristics(q,I,I_at_0=None):
    """
    Makes an educated guess for the radius of a small scatterer
    that would produce the input q, I(q).
    Result is bounded between 0.1 and 10 Angstroms.
    """
    # TODO: This should employ a Guinier-Porod or similar fit.
    n_q = len(q)
    # optimize the log pearson correlation in the upper half of the q domain
    nz = (I[n_q/2:]>0)
    fit_obj = lambda r: -1*compute_pearson(np.log(compute_spherical_normal_saxs(q[n_q/2:],r,0)[nz]),np.log(I[n_q/2:][nz]))
    #res = scipimin(fit_ojb,[0.1],bounds=[(0,0.3)]) 
    res = scipimin(fit_obj,[5],bounds=[(1E-3,10)])
    r_opt = res.x[0]
    return r_opt

def spherical_normal_heuristics(q,I,I_at_0=None):
    """
    This algorithm was developed and 
    originally contributed by Amanda Fournier.    

    Performs some heuristic measurements on the input spectrum,
    in order to make educated guesses 
    for the parameters of a size distribution
    (mean and standard deviation of radius)
    for a population of spherical scatterers.

    TODO: Document algorithm here.
    """
    if I_at_0 is None:
        I_at_0 = fit_I0(q,I)
    m = saxs_Iq4_metrics(q,I)
    width_metric = m['pI_qwidth']/m['q_at_Iqqqq_min1']
    intensity_metric = m['I_at_Iqqqq_min1']/I_at_0
    #######
    #
    # POLYNOMIALS FITTED FOR q0+/-10%,
    # where q0 is the argmin of a parabola
    # that is fit around the first minimum of I*q**4.
    # The function spherical_normal_heuristics_setup()
    # (in this same module) can be used to generate these polynomials.
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
    res = scipimin(heuristics_error,[0.1],bounds=[(0,0.3)]) 
    sigma_over_r = res.x[0]
    qr0_focus = np.polyval(p_qr0_focus,sigma_over_r)
    # qr0_focus = x1  ==>  r0 = x1 / q1
    r0 = qr0_focus/m['q_at_Iqqqq_min1']
    #sigma_r = sigma_over_r * r0 
    return r0,sigma_over_r

def saxs_Iq4_metrics(q,I):
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
        raise Exception(ex_msg)
    #######
    # Heuristics 2: Characterize I*q**4 around idxmin1, 
    # by locally fitting a standardized polynomial.
    idx_around_min1 = (q>0.9*q[idxmin1]) & (q<1.1*q[idxmin1])
    q_min1_mean = np.mean(q[idx_around_min1])
    q_min1_std = np.std(q[idx_around_min1])
    q_min1_s = (q[idx_around_min1]-q_min1_mean)/q_min1_std
    Iqqqq_min1_mean = np.mean(Iqqqq[idx_around_min1])
    Iqqqq_min1_std = np.std(Iqqqq[idx_around_min1])
    Iqqqq_min1_s = (Iqqqq[idx_around_min1]-Iqqqq_min1_mean)/Iqqqq_min1_std
    p_min1 = np.polyfit(q_min1_s,Iqqqq_min1_s,2,None,False,np.ones(len(q_min1_s)),False)
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
    # Heuristics 2b: Characterize I(q) near min1 of I*q^4.
    I_min1_mean = np.mean(I[idx_around_min1])
    I_min1_std = np.std(I[idx_around_min1])
    I_min1_s = (I[idx_around_min1]-I_min1_mean)/I_min1_std
    pI_min1 = np.polyfit(q_min1_s,I_min1_s,2,None,False,np.ones(len(q_min1_s)),False)
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
    r0_vals = np.arange(10,41,10,dtype=float)              #Angstrom
    for ir,r0 in zip(range(len(r0_vals)),r0_vals):
        q = np.arange(0.001/r0,float(10)/r0,0.001/r0)       #1/Angstrom
        sigma_r_vals = np.arange(0*r0,0.21*r0,0.01*r0)      #Angstrom
        for isig,sigma_r in zip(range(len(sigma_r_vals)),sigma_r_vals):
            I = compute_spherical_normal_saxs(q,r0,sigma_r/r0) 
            I_at_0 = compute_spherical_normal_saxs(0,r0,sigma_r/r0) 
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

