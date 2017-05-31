import numpy as np

from scipy.optimize import curve_fit

from ...Operation import Operation
from ... import optools

class OptimizeSphericalDiffractionFit(Operation):
    """From an initial guess, optimize r0, I0, and fractional_variation."""

    # q, I, dI, qlim, guesses, log=False, clip=False, errors=False, baseline=False
    def __init__(self):
        input_names = ['q', 'I', 'dI', 'parameter_guesses','noise_floor','log_log_fit','exclude_high_q',
                       'error_weighting','q_upper_limit']
        output_names = ['fitted_parameters','I_fit','q_I_fit_logsafe','goodness_metrics']
        super(OptimizeSphericalDiffractionFit, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d ndarray; wave vector values'
        self.input_doc['I'] = '1d ndarray; intensity values'
        self.input_doc['dI'] = '1d ndarray; intensity error estimate'
        self.input_doc['parameter_guesses'] = 'dictionary with keywords amplitude_at_zero, mean_size, and fractional_variation'
        self.input_doc['amplitude_at_zero'] = 'estimate of intensity at q=0'
        self.input_doc['mean_size'] = 'estimate of mean particle size'
        self.input_doc['fractional_variation'] = 'estimate of normal distribution sigma divided by mean size'
        self.input_doc['noise_floor'] = 'allow a fitted noise floor?'
        self.output_doc['fitted_parameters'] = 'dictionary with keywords amplitude_at_zero, mean_size, ' \
                                               'fractional_variation, and noise_magnitude'
        self.output_doc['I_fit'] = 'fitted intensity result'
        self.output_doc['q_I_fit_logsafe'] = 'fitted intensity result, zipped with q, logsafe ' \
                                             '(for display purposes; some points may be omitted)'
        self.output_doc['goodness_metrics'] = 'dictionary of various goodness-of-fit metrics'
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.input_src['parameter_guesses'] = optools.wf_input
        self.input_src['noise_floor'] = optools.text_input
        self.input_src['log_log_fit'] = optools.text_input
        self.input_src['exclude_high_q'] = optools.text_input
        self.input_src['error_weighting'] = optools.text_input
        self.input_src['q_upper_limit'] = optools.text_input
        self.input_type['noise_floor'] = optools.bool_type
        self.input_type['log_log_fit'] = optools.bool_type
        self.input_type['exclude_high_q'] = optools.bool_type
        self.input_type['error_weighting'] = optools.bool_type
        self.input_type['q_upper_limit'] = optools.float_type
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['dI'] = optools.ref_type
        self.input_type['parameter_guesses'] = optools.ref_type
        # defaults
        self.inputs['noise_floor'] = False
        self.inputs['log_log_fit'] = True
        self.inputs['exclude_high_q'] = True
        self.inputs['error_weighting'] = False
        self.inputs['q_upper_limit'] = 0.25

    def run(self):
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        guess_dict = self.inputs['parameter_guesses']
        log, clip, errors, baseline = self.inputs['log_log_fit'], self.inputs['exclude_high_q'], \
                                      self.inputs['error_weighting'], self.inputs['noise_floor']
        qlim = self.inputs['q_upper_limit']
        amplitude_at_zero, mean_size, fractional_variation = guess_dict['amplitude_at_zero'], guess_dict['mean_size'], \
                                                             guess_dict['fractional_variation']
        noise_magnitude = guess_noise_floor(q, I, mean_size)
        # computational validity checks
        valid = (~np.isnan(I)) & (~np.isinf(I)) & (I > 0)
        if (dI is not None) and errors:
            valid = valid & (~np.isnan(dI)) & (~np.isinf(dI)) & (dI > 0)
        if clip:
            valid = valid & (q <= qlim)
        x = q[valid]
        y = I[valid]
        if (dI is not None) and errors:
            dy = dI[valid]
        else:
            dy = None
        if log:
            y = safe_log(I[valid])
            if (dI is not None) and errors:
                # A reasonable proxy for log error
                dy = safe_log(I[valid] + dI[valid]) - safe_log(I[valid])
                # An alternative follows, prone to issues if (dI > I).any()
                # dI_val = 0.5 * (np.log(I_val + dI_val) - np.log(I_val - dI_val))
        # reasonable bounds; initial value list
        if baseline:
            bounds = ([amplitude_at_zero * 0.5, mean_size * 0.5, fractional_variation * 0.1, 0],
                      [amplitude_at_zero / 0.5, mean_size / 0.5, fractional_variation / 0.1, np.median(I)])
            init = [amplitude_at_zero, mean_size, fractional_variation, noise_magnitude]
        else:
            bounds = ([amplitude_at_zero * 0.5, mean_size * 0.5, fractional_variation * 0.1],
                      [amplitude_at_zero / 0.5, mean_size / 0.5, fractional_variation / 0.1])
            init = [amplitude_at_zero, mean_size, fractional_variation]
        # define function being fit to data
        if log:
            if baseline:
                def func(q, i0, r0, poly, noise):
                    return safe_log(generate_spherical_diffraction(q, i0, r0, poly) + noise)
            else:
                def func(q, i0, r0, poly):
                    return safe_log(generate_spherical_diffraction(q, i0, r0, poly))
        else:
            if baseline:
                def func(q, i0, r0, poly, noise):
                    return (generate_spherical_diffraction(q, i0, r0, poly) + noise)
            else:
                def func(q, i0, r0, poly):
                    return generate_spherical_diffraction(q, i0, r0, poly)
        # fit
        popt, pcov = curve_fit(func, x, y, init, dy, bounds=bounds)
        # unpack
        amplitude_at_zero, mean_size, fractional_variation = popt[0:3]
        if baseline:
            noise_magnitude = popt[3]
        else:
            noise_magnitude = None
        # feedback
        I_fit = amplitude_at_zero * blur(q * mean_size, fractional_variation)
        if noise_magnitude is not None:
            I_fit = I_fit + noise_magnitude
        chi_abs = chi_squared(I, I_fit)
        if dI is not None:
            chi_rel = chi_squared(I, I_fit, dI)
        else:
            chi_rel = None
        self.outputs['fitted_parameters'] = {'amplitude_at_zero':amplitude_at_zero, 'mean_size':mean_size,
                                             'fractional_variation':fractional_variation,
                                             'noise_magnitude':noise_magnitude}
        self.outputs['I_fit'] = I_fit
        self.outputs['q_I_fit_logsafe'] = logsafe_zip(q, I_fit)
        self.outputs['goodness_metrics'] = {'chi_absolute':chi_abs, 'chi_relative':chi_rel}


def safe_log(y):
    bads = (y <= 0) | (np.isnan(y))
    logy = np.log(y)
    logy[bads] = np.min(logy[~bads])
    return logy

def logsafe_zip(x, y):
    bad = (x <= 0) | (y <= 0) | np.isnan(y)
    x, y = x[~bad], y[~bad]
    x_y = np.zeros((x.size, 2))
    x_y[:, 0] = x
    x_y[:, 1] = y
    return x_y

def chi_squared(y1, y2, sigma=None):
    bads = (np.isnan(y1)) | (np.isnan(y2))
    if sigma is not None:
        bads = bads | (sigma == 0)
    else:
        sigma = np.ones(y1.shape)
    n = (~bads).sum()
    chi_2 = np.sum((y1[~bads] - y2[~bads])**2 * sigma[~bads]**-2) / (n - 1)
    return chi_2

def inclusive_arange(min, max, step):
    '''An inclusive-range version of np.arange.'''
    if np.mod((max - min), step) == 0:
        max += 0.5*step
    return np.arange(min, max, step)

def generate_spherical_diffraction(q, i0, r0, poly):
    x = q * r0
    i = i0 * blur(x, poly)
    return i

def generateRhoFactor(factor):
    '''
    Generate a guassian distribution of number densities (rho).

    :param factor: float
    :return:

    factor should be 0.1 for a sigma 10% of size
    '''
    factorCenter = 1
    factorMin = max(factorCenter-5*factor, 0.001)
    factorMax = factorCenter+5*factor
    factorVals = inclusive_arange(factorMin, factorMax, factor*0.02)
    # normalized gaussian:
    # ((sigma * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((x - x0)/sigma)**2)
    rhoVals = ((factor * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((factorVals - 1.)/factor)**2)
    return factorVals, rhoVals

def blur(x, factor):
    if factor == 0:
        return (3. * (np.sin(x) - x * np.cos(x)) * x**-3)**2
    factorVals, rhoVals = generateRhoFactor(factor)
    deltaFactor = factorVals[1] - factorVals[0]
    ysum = np.zeros(x.shape)
    for ii in range(len(factorVals)):
        effective_x = x / factorVals[ii]
        # spherical monodisperse diffraction:
        # (3. * (np.sin(x) - x * np.cos(x)) * x**-3)**2
        y = (3. * (np.sin(effective_x) - effective_x * np.cos(effective_x)) * effective_x**-3)**2
        ysum += rhoVals[ii]*y*deltaFactor
    return ysum

def guess_noise_floor(q, I, r0):
    qmin = q[0]
    qmax = q[-1]
    # we want q >> q1, ideally
    # the first dip is at 4.5 <~ x <~ 6, where x = q * r0.  We use pessimistic/strict option.
    qscale1 = 6/r0
    # and we know the worst signal to noise is at high q
    # so check the last tenth
    qscale2 = qmin + 0.9 * (qmax - qmin)
    if qscale2 < (qscale1 * 2): # just a sanity check, no real function
        print "Your data do not appear to be sampled to high q.  This is probably not a problem."
    selection = (q > qscale2)
    if selection.sum() < 10: # making sure there's a decent number of points in the sample
        print "Your data do not appear to be particularly well sampled.  This might be a problem."
        selection = np.zeros(q.size)
        selection[-10:] = True
    #noise = np.var(I[selection])
    noise = np.mean(I[selection])
    return noise

