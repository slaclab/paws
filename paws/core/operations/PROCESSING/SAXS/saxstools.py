from __future__ import print_function
import numpy as np
from scipy.optimize import minimize as scipimin

def compute_spherical_normal_saxs(q,r0,sigma_r):
    """
    Given q, a mean radius r0, and a standard deviation of radius sigma_r,
    compute the saxs spectrum assuming spherical particles 
    with normal size distribution.
    The returned intensity is normalized 
    such that I(q=0) is equal to 1.
    """
    q_zero = (q == 0)
    q_nz = np.invert(q_zero) 
    I = np.zeros(q.shape)
    I_zero = 0
    if sigma_r == 0:
        x = q*r0
        V_r0 = float(4)/3*np.pi*r0**3
        I[q_nz] = V_r0**2 * (3.*(np.sin(x[q_nz])-x[q_nz]*np.cos(x[q_nz]))*x[q_nz]**-3)**2
        I_zero = V_r0**2 
    else:
        dr = sigma_r*0.02
        rmin = np.max([r0-5*sigma_r,dr])
        rmax = r0+5*sigma_r
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

def saxs_spherical_normal_heuristics(q,I,dI=None):
    """
    This algorithm was developed and 
    originally contributed by Amanda Fournier.    

    Assuming the input spectrum resembles the SAXS spectrum
    of a dilute solution of spherical nanoparticles
    with a normal (Gaussian) size distribution,
    this operation uses characteristics of the spectrum
    to infer the mean and standard deviation of particle radius. 

    TODO: document the algorithm here.
    """
    d = {}
    if not dI:
        # uniform weights
        wt = np.ones(q.shape)   
    else:
        # inverse error weights, 1/dI, 
        # appropriate if dI represents
        # Gaussian uncertainty with sigma=dI
        wt = 1./dI
    #######
    # Heuristics step 1: Find the first local max
    # and subsequent local minimum of I*q**4 
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
    # Heuristics 2: Characterize I*q**4 around idxmin1, 
    # by locally fitting a standardized polynomial.
    idx_around_min1 = (q>0.9*q[idxmin1]) & (q<1.1*q[idxmin1])
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
    # Heuristics 2b: Characterize I(q) near min1 of I*q^4.
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
    # Heuristics 3: Estimate I(q=0) by polynomial fitting,
    # in the region below the first max of I*q^4.
    idx_lowq = range(idxmax1)
    I_lowq_mean = np.mean(I[idx_lowq])
    I_lowq_std = np.std(I[idx_lowq])
    lowq_mean = np.mean(q[idx_lowq])
    lowq_std = np.std(q[idx_lowq])
    I_lowq_s = (I[idx_lowq]-I_lowq_mean)/I_lowq_std
    lowq_s = (q[idx_lowq]-lowq_mean)/lowq_std
    #p_lowq = np.polyfit(lowq_s,I_lowq_s,2,None,False,wt[idx_lowq],False) 
    p_lowq = fit_lowq_spectrum(lowq_s,I_lowq_s,-1*lowq_mean/lowq_std,4,wt[idx_lowq]) 
    d['I_at_0'] = np.polyval(p_lowq,-1*lowq_mean/lowq_std)*I_lowq_std+I_lowq_mean
    return d
    #except Exception as ex:
    #    d['message'] = ex.message
    #    return d

def saxs_spherical_normal_fit(q,I,I_at_0,method,x_init,dI=None):
    """
    Fit a saxs spectrum (I(q) vs q) to the theoretical spectrum 
    for dilute spherical nanoparticles with normal size distribution.
    Fit parameters are average radius (r_mean), 
    and standard deviation of radius (sigma_r). 
    The intensity at q=0 (I_at_0) is held fixed.
    The initial estimate of x (x_init) should be 
    an array of the form [r_mean, sigma_r].

    Supported methods (input as strings): 
    full_spectrum_chi2- least squares fit to entire spectrum
    full_spectrum_chi2log- least squares fit to logarithm of entire spectrum
    """
    #try:
    d = {}
    d['message'] = ''
    if not dI:
        # uniform weights
        wt = np.ones(q.shape)   
    else:
        # inverse error weights, 1/dI, 
        # appropriate if dI represents
        # Gaussian uncertainty with sigma=dI
        wt = 1./dI
    if method == 'full_spectrum_chi2':
        fit_obj = lambda x: np.sum( (compute_spherical_normal_saxs(q,x[0],x[1]) - I/I_at_0)**2 )
    elif method == 'low_q_chi2':
        fit_obj = lambda x: np.sum( (compute_spherical_normal_saxs(q[:len(q)/2],x[0],x[1]) - I[:len(q)/2]/I_at_0)**2 )
    elif method == 'pearson':
        fit_obj = lambda x: -1*compute_pearson( I, compute_spherical_normal_saxs(q,x[0],x[1]) ) 
    elif method == 'low_q_pearson':
        fit_obj = lambda x: -1*compute_pearson( I[:len(q)/2], compute_spherical_normal_saxs(q[:len(q)/2],x[0],x[1]) ) 
    elif method == 'full_spectrum_chi2log':
        I_nz = np.invert((I==0))
        fit_obj = lambda x: np.sum( (np.log(compute_spherical_normal_saxs(q[I_nz],x[0],x[1])) - np.log(I[I_nz]/I_at_0))**2 )
    elif method == 'low_q_chi2log':
        I_nz = np.invert((I==0)) 
        fit_obj = lambda x: np.sum( (np.log(compute_spherical_normal_saxs(q[I_nz][:len(q)/2],x[0],x[1])) - np.log(I[I_nz][:len(q)/2]/I_at_0))**2 )
    elif method == 'pearson_log':
        I_nz = np.invert((I==0)) 
        fit_obj = lambda x: -1*compute_pearson( np.log(I[I_nz]), np.log(compute_spherical_normal_saxs(q[I_nz],x[0],x[1])) ) 
    elif method == 'low_q_pearson_log':
        I_nz = np.invert((I==0)) 
        fit_obj = lambda x: -1*compute_pearson( np.log(I[I_nz][:len(q)/2]), np.log(compute_spherical_normal_saxs(q[I_nz][:len(q)/2],x[0],x[1])) ) 
    else:
        msg = 'fitting method {} not supported'.format(method)
        raise ValueError(msg)
    res = scipimin(fit_obj,x_init)
    x_opt = res.x
    d['r_mean'] = x_opt[0]
    d['sigma_r'] = x_opt[1]
    return d
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

def fit_lowq_spectrum(qs,Is,qs_0,order,weights=None):
    """
    Perform a polynomial fitting of the low-q region of the scattering spectrum.
    Constraints are imposed to guarantee sane behavior at q=0.
    Specifically, dI/dq(q=0) is constrained to be zero.
    This is performed by forming a Lagrangian in polynomial coefficient space,
    from a quadratic cost function and the constraint function(s).
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
    p_fit = p_fit[:-1]  # throw away constraint term
    p_fit = p_fit[::-1] # reverse coefs to get np.polyfit format
    #from matplotlib import pyplot as plt
    #plt.figure(3)
    #plt.plot(qs,Is)
    #plt.plot(qs,np.polyval(p_fit,qs))
    #plt.plot(np.arange(qs_0,qs[-1],qs[-1]/100),np.polyval(p_fit,np.arange(qs_0,qs[-1],qs[-1]/100)))
    #plt.plot(qs_0,np.polyval(p_fit,qs_0),'ro')
    #plt.show()
    return p_fit
 

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

