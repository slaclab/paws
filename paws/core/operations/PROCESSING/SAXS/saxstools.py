from __future__ import print_function
import numpy as np
from scipy.optimize import minimize as scipimin
from collections import OrderedDict

def compute_saxs(q,params):
    """
    Given q and a dict of parameters,
    compute the saxs spectrum.
    Supported parameters are the same as 
    SaxsParameterization Operation outputs,
    and should include at least the following keys:
    I_at_0, precursor_flag, form_flag, structure_flag.

    TODO: Document the equation.
    """
    pre_flag = params['precursor_flag']
    f_flag = params['form_flag']
    s_flag = params['structure_flag']
    if not any([pre_flag,f_flag,s_flag]):
        I = np.ones(len(q))*params['I_at_0']
    else:
        I = np.zeros(len(q))
        if params['precursor_flag']:
            I0_pre = params['I0_pre']
            r0_pre = params['r0_pre']
            I_pre = compute_spherical_normal_saxs(q,r0_pre,0)
            I = I + params['I_at_0']*I0_pre*I_pre
        if params['form_flag']:
            I0_sph = params['I0_sphere']
            r0_sph = params['r0_sphere']
            sigma_sph = params['sigma_sphere']
            I_sph = compute_spherical_normal_saxs(q,r0_sph,sigma_sph)
            I = I + params['I_at_0']*I0_sph*I_sph
        #if params['structure_flag']:
        #    I0_pk = params['I0_pk']
        #    I_pk = compute_peaks()
    return I

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
    if sigma == 0:
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
    Makes an educated guess as to the 'radius' of a small scatterer
    that would produce the input q, I(q).
    """
    n_q = len(q)
    # optimize the pearson correlation in the upper half of the q domain
    fit_obj = lambda r: -1*compute_pearson(compute_spherical_normal_saxs(q[n_q/2:],r,0),I[n_q/2:])
    res = scipimin(heuristics_error,[0.1],bounds=[(0,0.3)]) 
    r_opt = scipimin(fit_obj,[5],bounds=[(0,10)])
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
    if not res.success:
        self.outputs['return_code'] = 2 
        msg = str('[{}] function minimization failed during '
        + 'form factor parameter extraction.'.format(__name__))
        self.outputs['features']['message'] = msg
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
    dominated by a dilute form factor term.
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

def saxs_fit(q,I,method,features,x_keys):
    """
    Fit a saxs spectrum (I(q) vs q) to the theoretical spectrum 
    for one or several scattering populations.
    Input features (dict) describes spectrum and scatterer populations.
    Input x_keys (list of strings) should all be keys in the features dict.
    These x_keys indicate which variables in the features dict should be optimized.
    TODO: document the objective functions, etc.

    Supported methods (input as strings): 
    full_spectrum_chi2- least squares fit to entire spectrum
    full_spectrum_chi2log- least squares fit to logarithm of entire spectrum
    TODO: fill in rest of objective options
    """
    pre_flag = features['precursor_flag']
    form_flag = features['form_flag']
    structure_flag = features['structure_flag']
    n_q = len(q)
    precursor_saxs = lambda q,x: np.zeros(len(q))
    form_saxs = lambda q,x: np.zeros(len(q))
    #structure_saxs = lambda q,x: np.zeros(len(q))
    xdict = OrderedDict()
    bdict = OrderedDict()
    ndim_pre = 0
    ndim_form = 0
    if pre_flag:
        if 'r0_pre' in x_keys:
            xdict['r0_pre'] = features['r0_pre']
            bdict['r0_pre'] = [0,None] 
            ndim_pre = 1
            precursor_saxs = lambda q,x: compute_spherical_normal_saxs(q,x[0],0)
        else:
            precursor_saxs = lambda q,x: compute_spherical_normal_saxs(q,features['r0_pre'],0)
    if form_flag:
        if 'r0_sphere' in x_keys and 'sigma_sphere' in x_keys:
            xdict['r0_sphere'] = features['r0_sphere']
            xdict['sigma_sphere'] = features['sigma_sphere']
            bdict['r0_sphere'] = [0.0,None] 
            bdict['sigma_sphere'] = [0.0,0.3] 
            ndim_form = 2
            form_saxs = lambda q,x: compute_spherical_normal_saxs(q,x[0],x[1])
        elif 'r0_sphere' in x_keys:
            xdict['r0_sphere'] = features['r0_sphere']
            bdict['r0_sphere'] = [0.0,None] 
            ndim_form = 1
            form_saxs = lambda q,x: compute_spherical_normal_saxs(q,x[0],features['sigma_sphere'])
        elif 'sigma_sphere' in x_keys:
            xdict['sigma_sphere'] = features['sigma_sphere']
            bdict['sigma_sphere'] = [0.0,0.3] 
            ndim_form = 1
            form_saxs = lambda q,x: compute_spherical_normal_saxs(q,features['r0_sphere'],x[0])
        else:
            form_saxs = lambda q,x: compute_spherical_normal_saxs(q,features['r0_sphere'],features['sigma_sphere'])
    I_at_0 = features['I_at_0']
    if ( (pre_flag and 'I0_pre' in x_keys) 
    and (form_flag and 'I0_sphere' in x_keys) ):
        xdict['I0_pre'] = features['I0_pre']
        xdict['I0_sphere'] = features['I0_sphere']
        bdict['I0_pre'] = [0.0,1.0]
        bdict['I0_sphere'] = [0.0,1.0] 
        # objective function with I(q=0) fixed:
        full_saxs = lambda q,x: I_at_0 * (
        (x[-2]/np.sum(x[-2:]))*precursor_saxs(q,x[:ndim_pre]) + 
        (x[-1]/np.sum(x[-2:]))*form_saxs(q,x[ndim_pre:ndim_pre+ndim_form]) )
    elif pre_flag and 'I0_pre' in x_keys:
        xdict['I0_pre'] = features['I0_pre']
        bdict['I0_pre'] = [0.0,1.0] 
        # objective function with I(q=0) variable:
        full_saxs = lambda q,x: I_at_0 * (
        x[-1]*precursor_saxs(q,x[:ndim_pre]) + 
        features['I0_sphere']*form_saxs(q,x[ndim_pre:ndim_pre+ndim_form]) )
    elif form_flag and 'I0_sphere' in x_keys:
        xdict['I0_sphere'] = features['I0_sphere']
        bdict['I0_sphere'] = [0.0,1.0] 
        # objective function with I(q=0) fixed:
        full_saxs = lambda q,x: I_at_0 * (
        (features['I0_pre']/(x[-1]+features['I0_pre']))*precursor_saxs(q,x[:ndim_pre]) + 
        (x[-1]/(x[-1]+features['I0_pre']))*form_saxs(q,x[ndim_pre:ndim_pre+ndim_form]) )
    else:
        # objective function with all intensity terms fixed:
        full_saxs = lambda q,x: I_at_0 * (
        (x[-2]/np.sum(x[-2:]))*precursor_saxs(q,x[:ndim_pre]) + 
        (x[-1]/np.sum(x[-2:]))*form_saxs(q,x[ndim_pre:ndim_pre+ndim_form]) )
    
    x_init = xdict.values()
    x_bounds = bdict.values()
    
    I_nz = (I>0)
    if method == 'full_spectrum_chi2':
        fit_obj = lambda x: np.sum( (full_saxs(q,x) - I)**2 )
    elif method == 'low_q_chi2':
        fit_obj = lambda x: np.sum( (full_saxs(q[:n_q/2],x) - I[:n_q/2])**2 )
    elif method == 'pearson':
        fit_obj = lambda x: -1*compute_pearson(full_saxs(q,x), I)
    elif method == 'low_q_pearson':
        fit_obj = lambda x: -1*compute_pearson(full_saxs(q[:n_q/2],x), I[:n_q/2]) 
    elif method == 'full_spectrum_chi2log':
        fit_obj = lambda x: np.sum( (np.log(full_saxs(q[I_nz],x)) - np.log(I[I_nz]))**2 )
    elif method == 'low_q_chi2log':
        fit_obj = lambda x: np.sum( (np.log(full_saxs(q[I_nz][:n_q/2],x)) - np.log(I[I_nz][:n_q/2]))**2 )
    elif method == 'pearson_log':
        fit_obj = lambda x: -1*compute_pearson(np.log(full_saxs(q[I_nz],x)), np.log(I[I_nz])) 
    elif method == 'low_q_pearson_log':
        fit_obj = lambda x: -1*compute_pearson(np.log(full_saxs(q[I_nz][n_q/2],x)), np.log(I[I_nz][:n_q/2])) 
    else:
        msg = 'fitting method {} not supported'.format(method)
        raise ValueError(msg)
    res = scipimin(fit_obj,x_init,bounds=x_bounds)
    x_opt = res.x
    #import pdb; pdb.set_trace()
    d_opt = OrderedDict()
    for k,xk in zip(xdict.keys(),x_opt):
        d_opt[k] = xk
    d_opt['objective_before'] = fit_obj(x_init)
    d_opt['objective_after'] = fit_obj(x_opt)
    return d_opt    
    #print('init: {}'.format(fit_obj(x_init)))
    #print('opt: {}'.format(fit_obj(x_opt)))
    #I_opt = I_at_0*compute_spherical_normal_saxs(q,x_opt[0],x_opt[1])
    #I_init = I_at_0*compute_spherical_normal_saxs(q,x_init[0],x_init[1])
    #from matplotlib import pyplot as plt
    #plt.figure(3)
    #plt.semilogy(q,I)
    #plt.semilogy(q,I_init,'r')
    #plt.semilogy(q,I_opt,'g:')
    #plt.show()
    #except Exception as ex:
    #    d['return_code'] = -1
    #    d['message'] = ex.message
    #    return d

def compute_pearson(y1,y2):
    y1mean = np.mean(y1)
    y2mean = np.mean(y2)
    y1std = np.std(y1)
    y2std = np.std(y2)
    return np.sum((y1-y1mean)*(y2-y2mean))/(np.sqrt(np.sum((y1-y1mean)**2))*np.sqrt(np.sum((y2-y2mean)**2)))

def fit_I0(q,I):
    """
    Find an estimate for I(q=0) by polynomial fitting.
    Inputs q and I are the spectrum.
    Fitting is performed on the lowest 10% of the q-domain.
    """
    qmax_fit = q[0]+float(q[-1]-q[0])*0.1
    idx_lowq = (q<qmax_fit)
    I_lowq_mean = np.mean(I[idx_lowq])
    I_lowq_std = np.std(I[idx_lowq])
    lowq_mean = np.mean(q[idx_lowq])
    lowq_std = np.std(q[idx_lowq])
    I_lowq_s = (I[idx_lowq]-I_lowq_mean)/I_lowq_std
    lowq_s = (q[idx_lowq]-lowq_mean)/lowq_std
    p_lowq = lowq_spectrum_polyfit(lowq_s,I_lowq_s,-1*lowq_mean/lowq_std,4) 
    I_at_0 = np.polyval(p_lowq,-1*lowq_mean/lowq_std)*I_lowq_std+I_lowq_mean
    return I_at_0

def lowq_spectrum_polyfit(qs,Is,qs_0,order,weights=None):
    """
    Perform a polynomial fitting 
    of the low-q region of the spectrum
    with dI/dq(q=0) constrained to be zero.
    This is performed by forming a Lagrangian 
    from a quadratic cost function 
    and the Lagrange-multiplied constraint function.
    
    TODO: Explicitly document cost function, constraints, Lagrangian.

    Inputs qs and Is are not standardized in this function,
    so they should be standardized beforehand 
    if standardized fitting is desired.
    At the provided constraint point, qs_0, 
    the returned polynomial will have zero slope.
    """
    Ap = np.zeros( (order+1,order+1),dtype=float )
    b = np.zeros(order+1,dtype=float)
    # TODO: vectorize the construction of Ap
    for i in range(0,order):
        for j in range(0,order):
            Ap[i,j] = np.sum( qs**j * qs**i )
        Ap[i,order] = -1*i*qs_0**(i-1)
    for j in range(0,order):
        Ap[order,j] = j*qs_0**(j-1)
        b[j] = np.sum(Is*qs**j)
    p_fit = np.linalg.solve(Ap,b) 
    p_fit = p_fit[:-1]  # throw away Lagrange multiplier term 
    p_fit = p_fit[::-1] # reverse coefs to get np.polyfit format
    #from matplotlib import pyplot as plt
    #plt.figure(3)
    #plt.plot(qs,Is)
    #plt.plot(qs,np.polyval(p_fit,qs))
    #plt.plot(np.arange(qs_0,qs[-1],qs[-1]/100),np.polyval(p_fit,np.arange(qs_0,qs[-1],qs[-1]/100)))
    #plt.plot(qs_0,np.polyval(p_fit,qs_0),'ro')
    #plt.show()
    return p_fit
 
def spherical_normal_heuristics_setup():
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

def local_maxima_detector(y):
    """ 
    Finds local maxima in ordered data y.

    :param y: 1d numpy float array
    :return maxima: 1d numpy bool array

    *maxima* is *True* at a local maximum, *False* otherwise.

    This function makes no attempt to reject spurious maxima of any sort.
    """
    length = y.size
    greater_than_follower = np.zeros(length, dtype=bool)
    greater_than_leader = np.zeros(length, dtype=bool)
    greater_than_follower[:-1] = np.greater(y[:-1], y[1:])
    greater_than_leader[1:] = np.greater(y[1:], y[:-1])
    maxima = np.logical_and(greater_than_follower, greater_than_leader)
    # End points
    maxima[0] = greater_than_follower[0]
    maxima[-1] = greater_than_leader[-1]
    return maxima

def local_minima_detector(y):
    """
    Finds local minima in ordered data *y*.

    :param y: 1d numpy float array
    :return minima: 1d numpy bool array

    *minima* is *True* at a local minimum, *False* otherwise.

    This function makes no attempt to reject spurious minima of any sort.
    """
    return local_maxima_detector(-y)

