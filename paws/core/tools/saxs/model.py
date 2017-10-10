"""Module of functions for modeling SAXS spectra.
"""

def compute_saxs(q,flags,params):
    """
    Given q, a dict of population flags,
    and a dict of scattering equation parameters,
    compute the saxs spectrum.

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
            I0_pre = params['I0_precursor']
            r0_pre = params['r0_precursor']
            G_pre = params['G_precursor']
            # Precursor as a monodisperse spherical form factor:
            I_pre = spherical_normal_saxs(q,r0_pre,0)
            # TODO: Finish implementing Guinier-Porod here, or similar 
            # TODO: implement G_pre as a (fixed?) parameter
            # Precursor as a Guinier-Porod equation for a small sphere:
            #I_pre = guinier_porod(q,G_pre,4,np.sqrt(3./5)*r0_pre)
            I += I0_pre*I_pre
        if f_flag:
            I0_sph = params['I0_sphere']
            r0_sph = params['r0_sphere']
            sigma_sph = params['sigma_sphere']
            I_sph = spherical_normal_saxs(q,r0_sph,sigma_sph)
            I += I0_sph*I_sph
    return I

def spherical_normal_saxs(q,r0,sigma):
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

def guinier_porod(q,guinier_factor,porod_exponent,r_g):
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
        I[idx_guinier] = guinier_factor * np.exp(-1./3*q**2*r_g**2)
    # Porod equation:
    if any(idx_porod):
        I[idx_porod] = porod_factor * 1./(q**porod_exponent)


