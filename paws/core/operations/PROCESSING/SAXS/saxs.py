from os.path import join
#from os import remove

import numpy as np
from scipy import interp

#from scipy.optimize import curve_fit

from ...Operation import Operation
from ... import optools

class GuessProperties(Operation):
    """Guess the polydispersity, mean size, and amplitude of spherical diffraction pattern.

    Assumes the data have already been background subtracted, smoothed, and otherwise cleaned."""

    def __init__(self):
        input_names = ['q', 'I', 'dI']
        output_names = ['parameter_guesses','good_flag','detailed_flags','I_guess','q_I_guess','additional_information']
        super(GuessProperties, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d ndarray; wave vector values'
        self.input_doc['I'] = '1d ndarray; intensity values'
        self.input_doc['dI'] = '1d ndarray; error estimate of intensity values; input None if no dI exists'
        self.output_doc['parameter_guesses'] = 'dictionary containing guessed parameters mean_size, amplitude_at_zero, and fractional_variation'
        self.output_doc['additional_information'] = 'dictionary of information primarily useful for debug purposes' #'qFirstDip','heightFirstDip','sigmaScaledFirstDip','heightAtZero',dips, shoulders
        self.output_doc['good_flag'] = 'presently a placeholder boolean'
        self.output_doc['detailed_flags'] = 'presently a placeholder dictionary'
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['dI'] = optools.ref_type


    def run(self):
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']

        # find extrema
        dips = local_minima_detector(I*q**4)
        shoulders = local_maxima_detector(I*q**4)
        # Clean out end points and weak maxima
        dips, shoulders = clean_extrema(dips, shoulders, I*q**4)

        qFirstDip, heightFirstDip, scaledQuadCoefficients = first_dip(q, I, dips, dI)
        sigmaScaledFirstDip = polydispersity_metric_sigmaScaledFirstDip(q, I, dips, shoulders, qFirstDip, heightFirstDip)
        heightAtZero = polydispersity_metric_heightAtZero(qFirstDip, q, I, dI)

        x0 = qFirstDip / sigmaScaledFirstDip
        y0 = heightFirstDip / heightAtZero
        try:
            references = load_references(reference_loc)
        except:
            print no_reference_message
        x = references['xFirstDip'] / references['sigmaScaledFirstDip']
        y = references['heightFirstDip'] / references['heightAtZero']
        factor = references['factorVals']
        fractional_variation, _, best_xy = guess_nearest_point_on_nonmonotonic_trace_normalized([x0, y0], [x, y],
                                                                                                    factor)

        self.outputs['additional_information'] = {'qFirstDip':qFirstDip, 'sigmaScaledFirstDip':sigmaScaledFirstDip,
                                  'heightFirstDip':heightFirstDip, 'dips':dips, 'shoulders':shoulders}
        mean_size = guess_size(fractional_variation, qFirstDip)
        amplitude_at_zero = polydispersity_metric_heightAtZero(qFirstDip, q, I, dI)
        amplitude_at_zero, mean_size, fractional_variation = refine_guess(q, I, amplitude_at_zero, mean_size, fractional_variation, qFirstDip, heightFirstDip)
        self.outputs['parameter_guesses'] = {'fractional_variation':fractional_variation, 'mean_size':mean_size, 'amplitude_at_zero':amplitude_at_zero}
        self.outputs['I_guess'] = generate_spherical_diffraction(q, amplitude_at_zero, mean_size, fractional_variation)
        self.outputs['q_I_guess'] = logsafe_zip(q, self.outputs['I_guess'])
        self.outputs['detailed_flags'] = {} ## PLACEHOLDER
        # if any of the detailed flags are bad set good_flag to False
        self.outputs['good_flag'] = True  ## PLACEHOLDER
        for ii in self.outputs['detailed_flags']:
            if self.outputs['detailed_flags'][ii] == False:
                self.outputs['good_flag'] = False



'''
def guess_polydispersity(q, I, dI=None):
#    global references
    if dI is None:
        dI = np.ones(I.shape, dtype=float)
    dips, shoulders = choose_dips_and_shoulders(q, I, dI)
    qFirstDip, heightFirstDip, sigmaScaledFirstDip, heightAtZero = take_polydispersity_metrics(q, I, dI)
    x0 = qFirstDip / sigmaScaledFirstDip
    y0 = heightFirstDip / heightAtZero
    try:
        references = load_references(reference_loc)
    except:
        print no_reference_message
    x = references['xFirstDip'] / references['sigmaScaledFirstDip']
    y = references['heightFirstDip'] / references['heightAtZero']
    factor = references['factorVals']
    fractional_variation, _, best_xy = guess_nearest_point_on_nonmonotonic_trace_normalized([x0, y0], [x, y], factor)
    return fractional_variation, qFirstDip, heightFirstDip, sigmaScaledFirstDip, heightAtZero, dips, shoulders

def choose_dips_and_shoulders(q, I, dI=None):
    "Find the location of dips (low points) and shoulders (high points)."
    if dI is None:
        dI = np.ones(I.shape, dtype=float)
    dips = local_minima_detector(I)
    shoulders = local_maxima_detector(I)
    # Clean out end points and wussy maxima
    dips, shoulders = clean_extrema(dips, shoulders, I)
    return dips, shoulders

def take_polydispersity_metrics(x, y, dy=None):
    if dy is None:
        dy = np.ones(y.shape)
    dips, shoulders = choose_dips_and_shoulders(x, y, dy)
    xFirstDip, heightFirstDip, scaledQuadCoefficients = first_dip(x, y, dips, dy)
    sigmaScaledFirstDip = polydispersity_metric_sigmaScaledFirstDip(x, y, dips, shoulders, xFirstDip, heightFirstDip)
    heightAtZero = polydispersity_metric_heightAtZero(xFirstDip, x, y, dy)
    return xFirstDip, heightFirstDip[0], sigmaScaledFirstDip[0], heightAtZero


def first_dip(q, I, dips, dI=None):
    if dI is None:
        dI = np.ones(I.shape, dtype=float)
    # if the first two "dips" are very close together, they are both marking the first dip
    # because I can't eliminate all spurious extrema with such a simple test
    dip_locs = np.where(dips)[0]
    # Catch the case of operation on noiseless data with few local minima
    if dip_locs.size < 3:
        case = 'smooth as butter'
        q1 = q[dip_locs[0]]
        scale = q1
    # Real data cases
    else:
        q1, q2, q3 = q[dip_locs[:3]]
        mult = 4
        smult = 1.5
        # q1, q2 close compared to q2, q3 and compared to 0, q1
        if ((q2 - q1)*mult < (q3 - q2)) & ((q2 - q1)*mult < q1):
            case = 'two'
            scale = 0.5 * q3
        # (q2 - q1)*1.5 approximately equal to q1
        elif ((q2 - q1)*1.5*smult > q1) & ((q2 - q1)*1.5 < q1*smult):
            case = 'one'
            scale = 0.5 * q2
        else:
            case = 'mystery'
            scale = q1
#    print "Detected case: %s." % case
    if case == 'two':
        minq = q1 - scale*0.1
        maxq = q2 + scale*0.1
    else:
        minq = q1 - scale*0.1
        maxq = q1 + scale*0.1
    selection = ((q < maxq) & (q > minq))
    # make sure selection is large enough to get a useful sampling
    if selection.sum() < 9:
        print "Your sampling in q seems to be sparse and will likely affect the quality of the estimate."
    for ii in range(9):
        if selection.sum() >= 9:
            break
        selection[1:] = selection[1:] | selection[:-1]
        selection[:-1] = selection[1:] | selection[:-1]
    # fit local quadratic
    coefficients = arbitrary_order_solution(2, q[selection], I[selection], dI[selection])
    # extremum_location = -0.5*coefficients[1]/coefficients[2]
    qbest = quadratic_extremum(coefficients)
    Ibest = polynomial_value(coefficients, qbest)
    return qbest, Ibest, coefficients

def take_polydispersity_metrics(x, y, dy=None):  # IMPROVEMENTS MADE
    if dy is None:
        dy = np.ones(y.shape)
    dips, shoulders = choose_dips_and_shoulders(x, y*x**4, dy)
    xFirstDip, heightFirstDip, scaledQuadCoefficients = first_dip(x, y, dips, dy)
    sigmaScaledFirstDip = polydispersity_metric_sigmaScaledFirstDip(x, y, dips, shoulders, xFirstDip, heightFirstDip)
    heightAtZero = polydispersity_metric_heightAtZero(xFirstDip, x, y, dy)
    return xFirstDip, heightFirstDip, sigmaScaledFirstDip[0], heightAtZero


'''


def first_dip(q, I, dips, dI=None):  # IMPROVEMENTS MADE
    if dI is None:
        dI = np.ones(I.shape, dtype=float)
    # if the first two "dips" are very close together, they are both marking the first dip
    # because I can't eliminate all spurious extrema with such a simple test
    dip_locs = np.where(dips)[0]
    # Catch the case of operation on noiseless data with few local minima
    if dip_locs.size < 3:
        case = 'smooth as butter'
        q1 = q[dip_locs[0]]
        scale = q1
    # Real data cases
    else:
        q1, q2, q3 = q[dip_locs[:3]]
        mult = 4
        smult = 1.5
        # q1, q2 close compared to q2, q3 and compared to 0, q1
        if ((q2 - q1)*mult < (q3 - q2)) & ((q2 - q1)*mult < q1):
            case = 'two'
            scale = 0.5 * q3
        # (q2 - q1)*1.5 approximately equal to q1
        elif ((q2 - q1)*1.5*smult > q1) & ((q2 - q1)*1.5 < q1*smult):
            case = 'one'
            scale = 0.5 * q2
        else:
            case = 'mystery'
            scale = q1
#    print "Detected case: %s." % case
    if case == 'two':
        minq = q1 - scale*0.1
        maxq = q2 + scale*0.1
    else:
        minq = q1 - scale*0.1
        maxq = q1 + scale*0.1
    selection = ((q < maxq) & (q > minq))
    # make sure selection is large enough to get a useful sampling
    if selection.sum() < 9:
        print "Your sampling in q seems to be sparse and will likely affect the quality of the estimate."
    for ii in range(9):
        if selection.sum() >= 9:
            break
        selection[1:] = selection[1:] | selection[:-1]
        selection[:-1] = selection[1:] | selection[:-1]
    # fit local quadratic
    coefficients = arbitrary_order_solution(2, q[selection], (I*q**4)[selection], dI[selection])
    # extremum_location = -0.5*coefficients[1]/coefficients[2]
    qbest = quadratic_extremum(coefficients)
    Ibest = polynomial_value(coefficients, qbest)*qbest**-4
    return qbest, Ibest, coefficients


def polydispersity_metric_sigmaScaledFirstDip(q, I, dips, shoulders, qFirstDip, heightFirstDip, dI=None):
    if dI is None:
        dI = np.ones(I.shape, dtype=float)
    scaled_I = I * q ** 4
    scaled_dI = dI * q ** 4
    powerCoefficients = power_law_solution(q[shoulders], I[shoulders], dI[shoulders])
    powerLawAtDip = powerCoefficients[0] * (qFirstDip ** powerCoefficients[1])
    scaledDipDepth = (powerLawAtDip - heightFirstDip) * (qFirstDip ** 4)
    pad = 3
    firstDipIndex = np.where(dips)[0][0]
    lolim = firstDipIndex - pad
    hilim = firstDipIndex + pad
    quadCoefficients = arbitrary_order_solution(2, q[lolim:hilim], scaled_I[lolim:hilim], scaled_dI[lolim:hilim])
    scaledDipCurvature = 2 * quadCoefficients[2]
    _, sigma = gauss_guess(scaledDipDepth, scaledDipCurvature)
    return sigma


def gauss_guess(signalMagnitude, signalCurvature):
    '''
    Guesses a gaussian intensity and width from signal magnitude and curvature.

    :param signalMagnitude: number-like with units of magnitude
    :param signalCurvature: number-like with units of magnitude per distance squared
    :return intensity, sigma:

    The solution given is not fitted; it is a first estimate to be used in fitting.
    '''
    signalMagnitude = np.fabs(signalMagnitude)
    signalCurvature = np.fabs(signalCurvature)
    sigma = (signalMagnitude / signalCurvature) ** 0.5
    intensity = signalMagnitude * sigma * (2 * np.pi) ** 0.5
    return intensity, sigma


def logsafe_zip(x, y):
    bad = (x <= 0) | (y <= 0) | np.isnan(y)
    x, y = x[~bad], y[~bad]
    x_y = np.zeros((x.size, 2))
    x_y[:, 0] = x
    x_y[:, 1] = y
    return x_y


# I/O functions

def load_references(reference_loc):
    try:
        x = np.loadtxt(reference_loc, delimiter=',')
        references = {'factorVals': x[:, 0],
                      'heightAtZero': x[:, 1],
                      'heightFirstDip': x[:, 2],
                      'xFirstDip': x[:, 3],
                      'sigmaScaledFirstDip': x[:, 4]
                      }
    except IOError:
        print '''Your references file (%s)
        appears to be missing.  Re-download or re-generate it.''' % reference_loc
    return references

# Functions about algebraic solutions

def arbitrary_order_solution(order, x, y, dy=None):
    '''Solves for a polynomial "fit" of arbitrary order.'''
    if dy is None:
        dy = np.ones(y.shape, dtype=float)
    # Formulate the equation to be solved for polynomial coefficients
    matrix, vector = make_poly_matrices(x, y, dy, order)
    # Solve equation
    inverse = np.linalg.pinv(matrix)
    coefficients = np.matmul(inverse, vector)
    coefficients = coefficients.flatten()
    return coefficients

def quadratic_extremum(coefficients):
    '''Finds the location in independent coordinate of the extremum of a quadratic equation.'''
    extremum_location = -0.5*coefficients[1]/coefficients[2]
    return extremum_location

def polynomial_value(coefficients, x):
    '''Finds the value of a polynomial at a location.'''
    csize = coefficients.size
    powers = np.arange(csize)
    try:
        xsize = x.size # distinguish sequence x from numeric x
        # (1, m) a horizontal vector
        powers = powers.reshape(1, csize)
        coefficients = coefficients.reshape(1, csize)
        x = x.reshape(xsize, 1)
        y = ((x ** powers) * coefficients).sum(axis=1)
        y = y.flatten()
    except AttributeError:
        y = ((x ** powers) * coefficients).sum()
    if y.size != 1:
        print "Whoa there cowpoke!  WTF?"
    y = y[0]
    return y

def make_poly_matrices(x, y, error, order):
    '''Make the matrices necessary to solve a polynomial fit of order *order*.

    :param x: 1d array representing independent variable
    :param y: 1d array representing dependent variable
    :param error: 1d array representing uncertainty in *y*
    :param order: integer order of polynomial fit
    :return matrix, vector: MC=V, where M is *matrix*, V is *vector*,
        and C is the polynomial coefficients to be solved for.
        *matrix* is an array of shape (order+1, order+1).
        *vector* is an array of shape (order+1, 1).
    '''
    if not error.any():
        error = np.ones(y.shape, dtype=float)
    if ((x.shape != y.shape) or (y.shape != error.shape)):
        raise ValueError('Arguments *x*, *y*, and *error* must all have the same shape.')
    size = x.size
    index = np.arange(order+1)
    # (n, 1, 1) a dummy vector to be summed over index zero
    # (m, 1) a vertical vector
    # (1, m) a horizontal vector
    vector = (y.reshape(size,1,1) * x.reshape(size,1,1) ** index.reshape(order+1,1) * error.reshape(size,1,1)).sum(axis=0)
    index_block = index.reshape(1,order+1) + index.reshape(order+1,1)
    matrix = (x.reshape(size,1,1) ** index_block * error.reshape(size,1,1)).sum(axis=0)
    return matrix, vector

def power_law_solution(x, y, dy=None):
    '''Solves for a power law by solving for a linear fit in log-log space.'''
    # Note that if dy is zeros, logdy will also be zeros, triggering default behavior in arbitrary_order_solution also.
    if dy is None:
        dy = np.ones(y.shape, dtype=float)
    logdy = np.log(y + dy) - np.log(y)
    logLogSoln = arbitrary_order_solution(1, np.log(x), np.log(y), logdy)
    # powerCoefficients = [prefactor, exponent]
    powerCoefficients = np.array([np.exp(logLogSoln[0]), logLogSoln[1]])
    return powerCoefficients

# Functions about simulating SAXS patterns

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

'''
def generate_references(x, factorVals):
    num_tests = len(factorVals)
    xFirstDip = np.zeros(num_tests)
    sigmaScaledFirstDip = np.zeros(num_tests)
    heightFirstDip = np.zeros(num_tests)
    heightAtZero = np.zeros(num_tests)
    for ii in range(num_tests):
        factor = factorVals[ii]
        y = blur(x, factor)
        xFirstDip[ii], heightFirstDip[ii], sigmaScaledFirstDip[ii], heightAtZero[ii] = take_polydispersity_metrics(x, y)
    references = consolidate_references(factorVals, xFirstDip, sigmaScaledFirstDip, heightFirstDip, heightAtZero)
    return references

def consolidate_references(factorVals, xFirstDip, sigmaScaledFirstDip, heightFirstDip, heightAtZero):
    references = {}
    references['factorVals'] = factorVals
    references['xFirstDip'] = xFirstDip
    references['heightFirstDip'] = heightFirstDip
    references['sigmaScaledFirstDip'] = sigmaScaledFirstDip
    references['heightAtZero'] = heightAtZero
    return references

def save_references(references, reference_loc):
    n = references['factorVals'].size
    x = [[references['factorVals'][ii], references['heightAtZero'][ii], references['heightFirstDip'][ii],
          references['xFirstDip'][ii], references['sigmaScaledFirstDip'][ii]] for ii in range(n)]
    x = np.array(x, dtype=float)
    np.savetxt(reference_loc, x, delimiter=', ',
               header='factorVals, heightAtZero, heightFirstDip, xFirstDip, sigmaScaledFirstDip')

'''

# Funtions specifically about detecting SAXS properties

def refine_guess(q, I, I0, r0, frac, q1, I1):
    Imodel = generate_spherical_diffraction(q, I0, r0, frac)
    I_adjustment = I.sum() / Imodel.sum()
    new_I0 = I0 * I_adjustment
    #Imodel *= I_adjustment
    #first_dip_index = np.where(local_minima_detector(Imodel))[0][0]
    #model_q1 = q[first_dip_index]
    #model_I1 = I[first_dip_index]
    try:
        references = load_references(reference_loc)
    except:
        print no_reference_message
    x = references['factorVals']
    y1 = references['heightFirstDip']/references['heightAtZero']
    y2 = references['xFirstDip']
    if ~(x[1:] > x[:-1]).all():
        print '''The factorVals entry in the guesser's reference file is not strictly increasing.
        This is a serious problem likely to result in horrible crashes and/or incorrect results.'''
    new_frac = float(interp(I1/new_I0, y1, x))
    #Imodel = generate_spherical_diffraction(q, new_I0, r0, new_frac)
    # want new r0
    new_x0 = interp(new_frac, x, y2)
    new_r0 = float(new_x0/q1)
    return new_I0, new_r0, new_frac

def clean_extrema(dips, shoulders, y):
    # Mark endpoints False
    dips[0:10] = False
    dips[-1] = False
    shoulders[0] = False
    shoulders[-1] = False
    # Reject weaksauce local maxima and minima
    extrema = dips | shoulders
    extrema_indices = np.where(extrema)[0]
    for ii in range(len(extrema_indices) - 3):
        four_indices = extrema_indices[ii:ii+4]
        is_dip = dips[extrema_indices[ii]]
        if is_dip:
            weak = upwards_weaksauce_identifier(four_indices, y)
        else:
            weak = downwards_weaksauce_identifier(four_indices, y)
        if weak:
            extrema[four_indices[1]] = False
            extrema[four_indices[2]] = False
    # Apply mask to shoulders & dips
    dips = dips * extrema
    shoulders = shoulders * extrema
    return dips, shoulders

def upwards_weaksauce_identifier(four_indices, y):
    a, b, c, d = four_indices
    if (y[a] < y[c]) & (y[b] < y[d]):
        weak = True
    else:
        weak = False
    return weak

def downwards_weaksauce_identifier(four_indices, y):
    return upwards_weaksauce_identifier(four_indices, -y)

def guess_size(fractional_variation, first_dip_q):
#    global references
    try:
        references = load_references(reference_loc)
    except:
        print no_reference_message
    #xFirstDip, factorVals = references['xFirstDip'], references['factorVals']
    first_dip_x = interp(fractional_variation, references['factorVals'], references['xFirstDip'])
    mean_size = first_dip_x / first_dip_q
    return mean_size

def polydispersity_metric_heightAtZero(qFirstDip, q, I, dI=None):
    if dI is None:
        dI = np.ones(I.shape, dtype=float)
    qlim = max(q[6], (qFirstDip - q[0])/2.)
    if qlim > 0.75*qFirstDip:
        print "Low-q sampling is poor and will likely affect estimate quality."
    low_q = (q < qlim)
    coefficients = arbitrary_order_solution(4, q[low_q], I[low_q], dI[low_q])
    heightAtZero = coefficients[0]
    return heightAtZero

# Other functions

def local_maxima_detector(y):
    '''
    Finds local maxima in ordered data y.

    :param y: 1d numpy float array
    :return maxima: 1d numpy bool array

    *maxima* is *True* at a local maximum, *False* otherwise.

    This function makes no attempt to reject spurious maxima of various sorts.
    That task is left to other functions.
    '''
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
    '''
    Finds local minima in ordered data *y*.

    :param y: 1d numpy float array
    :return minima: 1d numpy bool array

    *minima* is *True* at a local minimum, *False* otherwise.

    This function makes no attempt to reject spurious minima of various sorts.
    That task is left to other functions.
    '''
    return local_maxima_detector(-y)

def guess_nearest_point_on_nonmonotonic_trace_normalized(loclist, tracelist, coordinate):
    '''Finds the nearest point to location *loclist* on a trace *tracelist*.

    Uses normalized distances, i.e., the significance of each dimension is made equivalent.

    *loclist* and *tracelist* are lists of the same length and type.
    Elements of *loclist* are floats; elements of *tracelist* are arrays of the same shape as *coordinate*.
    *coordinate* is the independent variable along which *tracelist* is varying.

    *tracelist* must have decent sampling to start with or the algorithm will likely fail.'''
    tracesize = coordinate.size
    spacesize = len(loclist)
    distances = np.zeros(tracesize, dtype=float)
    for ii in range(spacesize):
        yii = tracelist[ii]
        meanii = yii.mean()
        varii = (((yii - meanii)**2).mean())**0.5
        normyii = (yii - meanii)/varii
        y0 = loclist[ii]
        normy0 = (y0 - meanii)/varii
        diffsquare = (normyii - normy0)**2
        distances = distances + diffsquare
    distances = distances**0.5
    best_indices = np.where(local_minima_detector(distances))[0]
    # At this point we've just found good neighborhoods to investigate
    # So we compare those neighborhoods
    n_candidates = best_indices.size
    best_coordinates = np.zeros(n_candidates)
    best_distances = np.zeros(n_candidates)
    for ii in range(n_candidates):
        best_index = best_indices[ii]
        # Assume distances is a fairly (but not perfectly) smooth function of coordinate
        lolim = best_index-2
        hilim = best_index+3
        if lolim < 0:
            lolim = None
        if hilim >= tracesize:
            hilim = None
        distance_coefficients = arbitrary_order_solution(2,coordinate[lolim:hilim],distances[lolim:hilim])
        best_coordinates[ii] = quadratic_extremum(distance_coefficients)
        best_distances[ii] = polynomial_value(distance_coefficients, best_coordinates[ii])
    # Identify the approximate/probable actual best point...
    best_distance = best_distances.min()
    best_coordinate = best_coordinates[np.where(best_distances == best_distance)[0][0]]
    # ...including the location of that point in space.
    best_location = np.zeros(spacesize)
    for jj in range(spacesize):
        coorddiff = np.fabs(best_coordinate - coordinate)
        best_index = np.where(coorddiff == coorddiff.min())[0][0]
        lolim = best_index-2
        hilim = best_index+3
        if lolim < 0:
            lolim = None
        if hilim >= tracesize:
            hilim = None
        xjj = tracelist[jj]
        xjj_coefficients = arbitrary_order_solution(2, coordinate[lolim:hilim], xjj[lolim:hilim])
        best_xjj = polynomial_value(xjj_coefficients, best_coordinate)
        best_location[jj] = best_xjj
    return best_coordinate, best_distance, best_location #, distances

no_reference_message = '''No reference file exists.  Use the GenerateReferences operation once to generate
an appropriate file; the file will be saved and need not be generated again.'''

reference_loc = join('paws','core','operations','DMZ','references','polydispersity_guess_references.csv.gz')
try:
    references = load_references(reference_loc)
except:
    print "Something other than an IOerror seems to have gone wrong."

'''
import numpy as np
import os.path
reference_folder = join('paws','core','operations','DMZ','references')
reference_loc = join('paws','core','operations','DMZ','references','polydispersity_guess_references.csv.gz')
os.path.exists(reference_folder)
os.path.exists(reference_loc)
fake = reference_loc + 'lol'
os.path.exists(fake)
load_references(reference_loc)
'''