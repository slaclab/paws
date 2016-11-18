import numpy as np
from scipy import interp
#from matplotlib import pyplot as plt
from os.path import join
from os import remove
try:
    import cPickle as pickle
except ImportError:
    import pickle

from slacxop import Operation
import optools

reference_loc = join('slacx','slacxcore','operations','dmz','references','polydispersity_guess_references.pickle')
global references
references = {}

class GenerateSphericalDiffractionQ(Operation):
    """Generate a SAXS diffraction pattern for spherical nanoparticles.

    Uses r0 in real units and gives q in real units."""

    def __init__(self):
        input_names = ['r0', 'sigma_r_over_r0', 'intensity_at_zero_q', 'qmin', 'qmax', 'qstep']
        output_names = ['q', 'I']
        super(GenerateSphericalDiffractionQ, self).__init__(input_names, output_names)
        self.input_doc['r0'] = 'mean particle radius'
        self.input_doc['sigma_r_over_r0'] = 'width of distribution in r divided by r0'
        self.input_doc['intensity_at_zero_q'] = 'intensity at q = 0'
        self.input_doc['qmin'] = 'lower bound of q range of interest'
        self.input_doc['qmax'] = 'upper bound of q range of interest'
        self.input_doc['qstep'] = 'step size in q range of interest'
        self.input_src['r0'] = optools.wf_input
        self.input_src['sigma_r_over_r0'] = optools.wf_input
        self.input_src['intensity_at_zero_q'] = optools.wf_input
        self.input_src['qmin'] = optools.user_input
        self.input_src['qmax'] = optools.user_input
        self.input_src['qstep'] = optools.user_input
        self.input_type['qmin'] = optools.float_type
        self.input_type['qmax'] = optools.float_type
        self.input_type['qstep'] = optools.float_type
        self.output_doc['q'] = '1d ndarray; wave vector values'
        self.output_doc['I'] = '1d ndarray; intensity values'
        # source & type
        self.input_src['r0'] = optools.user_input
        self.input_src['sigma_r_over_r0'] = optools.user_input
        self.input_src['intensity_at_zero_q'] = optools.user_input
        self.input_src['qmin'] = optools.user_input
        self.input_src['qmax'] = optools.user_input
        self.input_src['qstep'] = optools.user_input
        self.input_type['r0'] = optools.float_type
        self.input_type['sigma_r_over_r0'] = optools.float_type
        self.input_type['intensity_at_zero_q'] = optools.float_type
        self.input_type['qmin'] = optools.float_type
        self.input_type['qmax'] = optools.float_type
        self.input_type['qstep'] = optools.float_type
        self.categories = ['1D DATA PROCESSING.GENERATE SAXS PATTERNS']

    def run(self):
        self.outputs['q'] = gen_q_vector(self.inputs['qmin'], self.inputs['qmax'], self.inputs['qstep'])
        self.outputs['I'] = \
            generate_spherical_diffraction(self.inputs['r0'], self.inputs['sigma_r_over_r0'],
                                           self.inputs['intensity_at_zero_q'], self.outputs['q'])


class GenerateSphericalDiffraction(Operation):
    """Generate a SAXS diffraction pattern for spherical nanoparticles.

    Uses r0 in real units and gives q in real units."""

    def __init__(self):
        input_names = ['r0', 'sigma_r_over_r0', 'intensity_at_zero_q', 'q_vector']
        output_names = ['I']
        super(GenerateSphericalDiffraction, self).__init__(input_names, output_names)
        self.input_doc['r0'] = 'mean particle radius'
        self.input_doc['sigma_r_over_r0'] = 'width of distribution in r divided by r0'
        self.input_doc['intensity_at_zero_q'] = 'intensity at q = 0'
        self.input_doc['q_vector'] = 'q values of interest'
        self.input_src['r0'] = optools.wf_input
        self.input_src['sigma_r_over_r0'] = optools.wf_input
        self.input_src['intensity_at_zero_q'] = optools.wf_input
        self.input_src['q_vector'] = optools.wf_input
        self.output_doc['I'] = '1d ndarray; intensity values'
        # source & type
        self.input_src['r0'] = optools.user_input
        self.input_src['sigma_r_over_r0'] = optools.user_input
        self.input_src['intensity_at_zero_q'] = optools.user_input
        self.input_src['q_vector'] = optools.wf_input
        self.input_type['r0'] = optools.float_type
        self.input_type['sigma_r_over_r0'] = optools.float_type
        self.input_type['intensity_at_zero_q'] = optools.float_type
        self.categories = ['1D DATA PROCESSING.GENERATE SAXS PATTERNS']

    def run(self):
        self.outputs['I'] = \
            generate_spherical_diffraction(self.inputs['r0'], self.inputs['sigma_r_over_r0'],
                                           self.inputs['intensity_at_zero_q'], self.inputs['q_vector'])

'''
class GenerateSphericalDiffractionX(Operation):
    """Generate a SAXS diffraction pattern for spherical nanoparticles.

    Generates pattern in units x = r0 * q, with the assumption that x0 = r0 * q0 = 1."""

    def __init__(self):
        input_names = ['sigma_x_over_x0', 'intensity_at_zero_q', 'xmin', 'xmax', 'xstep']
        output_names = ['x', 'I']
        super(GenerateSphericalDiffractionX, self).__init__(input_names, output_names)
        self.input_doc['sigma_r_over_r0'] = 'width of distribution in r divided by r0'
        self.input_doc['intensity_at_zero_q'] = 'intensity at q = 0'
        self.input_doc['xmin'] = 'lower bound of x range of interest'
        self.input_doc['xmax'] = 'upper bound of x range of interest'
        self.input_doc['xstep'] = 'step size in x range of interest'
        self.input_src['sigma_x_over_x0'] = optools.user_input
        self.input_src['intensity_at_zero_q'] = optools.user_input
        self.input_src['xmin'] = optools.user_input
        self.input_src['xmax'] = optools.user_input
        self.input_src['xstep'] = optools.user_input
        self.input_type['sigma_x_over_x0'] = optools.float_type
        self.input_type['intensity_at_zero_q'] = optools.float_type
        self.input_type['xmin'] = optools.float_type
        self.input_type['xmax'] = optools.float_type
        self.input_type['xstep'] = optools.float_type
        self.output_doc['x'] = '1d ndarray; wave vector values'
        self.output_doc['I'] = '1d ndarray; intensity values'
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['q'], self.outputs['I'] = \
            generate_spherical_diffraction(self.inputs['r0'], self.inputs['sigma_x_over_x0'],
                                           self.inputs['intensity_at_zero_q'], self.inputs['qmin'], self.inputs['qmax'],
                                           self.inputs['qstep'])
'''

class GenerateReferences(Operation):
    """Generate metrics used for guessing diffraction pattern properties.

    DOES NOT STORE.  IS NOT AUTOMATICALLY AVAILABLE TO OTHER OPERATIONS.

    Use OverwriteReferences to store the resulting dictionary, if desired."""

    def __init__(self):
        input_names = ['xmin', 'xmax', 'xstep', 'factormin', 'factormax', 'factorstep']
        output_names = ['references']
        super(GenerateReferences, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['xmin'] = 'lowest computed value of x; nuisance parameter'
        self.input_doc['xmax'] = 'highest computed value of x; nuisance parameter'
        self.input_doc['xstep'] = 'step size in x; nuisance parameter'
        self.input_doc['factormin'] = 'lowest computed value of factor'
        self.input_doc['factormax'] = 'highest computed value of factor'
        self.input_doc['factorstep'] = 'step size in factor'
        self.output_doc['references'] = 'dictionary of useful values'
        # Source and type
        self.input_src['xmin'] = optools.user_input
        self.input_src['xmax'] = optools.user_input
        self.input_src['xstep'] = optools.user_input
        self.input_src['factormin'] = optools.user_input
        self.input_src['factormax'] = optools.user_input
        self.input_src['factorstep'] = optools.user_input
        self.input_type['xmin'] = optools.float_type
        self.input_type['xmax'] = optools.float_type
        self.input_type['xstep'] = optools.float_type
        self.input_type['factormin'] = optools.float_type
        self.input_type['factormax'] = optools.float_type
        self.input_type['factorstep'] = optools.float_type
        self.categories = ['1D DATA PROCESSING.GENERATE SAXS PATTERNS']

    def run(self):
        x = gen_q_vector(self.inputs['xmin'], self.inputs['xmax'], self.inputs['xstep'])
        factorVals = gen_q_vector(self.inputs['factormin'], self.inputs['factormax'], self.inputs['factorstep'])
        references = generate_references(x, factorVals)
        self.outputs['references'] = references

class OverwriteReferences(Operation):
    """Store previously generated metrics used for guessing diffraction pattern properties.

    USE WITH CAUTION as it will OVERWRITE any existing reference file."""

    def __init__(self):
        input_names = ['references']
        output_names = []
        super(OverwriteReferences, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['references'] = 'dictionary of useful values generated by GenerateReferences'
        # Source and type
        self.input_src['references'] = optools.wf_input
        self.categories = ['OUTPUT']

    def run(self):
        remove(reference_loc)
        dump_references(self.inputs['references'])


class GuessPolydispersityWeighted(Operation):
    """Guess the polydispersity of spherical diffraction pattern.

    Assumes the data have already been background subtracted, smoothed, and otherwise cleaned."""

    def __init__(self):
        input_names = ['q','I','dI']
        output_names = ['fractional_variation','first_dip_q']
        super(GuessPolydispersityWeighted, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d ndarray; wave vector values'
        self.input_doc['I'] = '1d ndarray; intensity values'
        self.input_doc['dI'] = '1d ndarray; error estimate of intensity values'
        self.output_doc['fractional_variation'] = 'normal distribution sigma divided by mean size'
        self.output_doc['first_dip_q'] = 'location in q of the first dip'
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.categories = ['1D DATA PROCESSING.SAXS INTERPRETATION']

    def run(self):
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        fractional_variation, first_dip_q = guess_polydispersity(q, I, dI)
        self.outputs['fractional_variation'], self.outputs['first_dip_q'] = fractional_variation, first_dip_q


class GuessSize(Operation):
        """Guess the mean size of spherical diffraction pattern.

        Assumes the data have already been background subtracted, smoothed, and otherwise cleaned.

        Requires foreknowledge of the fractional variation in size."""

        def __init__(self):
            input_names = ['fractional_variation', 'first_dip_q']
            output_names = ['mean_size']
            super(GuessSize, self).__init__(input_names, output_names)
            # Documentation
            self.input_doc['fractional_variation'] = 'normal distribution sigma divided by mean size'
            self.input_doc['first_dip_q'] = 'location in q of the first dip'
            self.output_doc['mean_size'] = 'mean size of particles'
            # Source and type
            self.input_src['fractional_variation'] = optools.wf_input
            self.input_src['first_dip_q'] = optools.wf_input
            self.categories = ['1D DATA PROCESSING.SAXS INTERPRETATION']

        def run(self):
            fractional_variation, first_dip_q = self.outputs['fractional_variation'], self.outputs['first_dip_q']
            mean_size = guess_size(fractional_variation, first_dip_q)
            self.outputs['mean_size'] = mean_size

class GuessPropertiesWeighted(Operation):
    """Guess the polydispersity, mean size, and amplitude of spherical diffraction pattern.

    Assumes the data have already been background subtracted, smoothed, and otherwise cleaned."""

    def __init__(self):
        input_names = ['q', 'I', 'dI']
        output_names = ['fractional_variation', 'mean_size', 'amplitude_at_zero']
        super(GuessPropertiesWeighted, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d ndarray; wave vector values'
        self.input_doc['I'] = '1d ndarray; intensity values'
        self.input_doc['dI'] = '1d ndarray; error estimate of intensity values'
        self.output_doc['fractional_variation'] = 'normal distribution sigma divided by mean size'
        self.output_doc['mean_size'] = 'mean size of particles'
        self.output_doc['amplitude_at_zero'] = 'projected scattering amplitude at q=0'
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.categories = ['1D DATA PROCESSING.SAXS INTERPRETATION']

    def run(self):
        print "Starting"
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        print "Guessing polydispersity"
        fractional_variation, first_dip_q = guess_polydispersity(q, I, dI)
        print "Guessing size"
        mean_size = guess_size(fractional_variation, first_dip_q)
        print "Guessing amplitude at zero"
        amplitude_at_zero = polydispersity_metric_heightAtZero(first_dip_q, q, I, dI)
        #dips, shoulders = choose_dips_and_shoulders(q, I, dI)
        print "Returning"
        self.outputs['fractional_variation'], self.outputs['mean_size'], self.outputs['amplitude_at_zero'] = \
            fractional_variation, mean_size, amplitude_at_zero

def generate_references(x, factorVals):
    #y0 = fullFunction(x)
    num_tests = len(factorVals)
    xFirstDip = np.zeros(num_tests)
    sigmaFirstDip = np.zeros(num_tests)
    heightFirstDip = np.zeros(num_tests)
    heightAtZero = np.zeros(num_tests)
    #powerLawAll = np.zeros((num_tests, 2))
    #powerLawInitial = np.zeros((num_tests, 2))
    #depthFirstDip = np.zeros(num_tests)
    #y_x4_inf = np.zeros(num_tests)
    #lowQApprox = np.zeros((num_tests, 2))
    for ii in range(num_tests):
        factor = factorVals[ii]
        y = blur(x, factor)
        dips, shoulders = choose_dips_and_shoulders(x, y)
        xFirstDip[ii], scaledQuadCoefficients = polydispersity_metric_qFirstDip(x, y, dips)
        heightFirstDip[ii] = polydispersity_metric_heightFirstDip(scaledQuadCoefficients, xFirstDip[ii])
        sigmaFirstDip[ii] = polydispersity_metric_sigmaFirstDip(x, y, dips, shoulders, xFirstDip[ii], heightFirstDip[ii])
        heightAtZero[ii] = polydispersity_metric_heightAtZero(xFirstDip[ii], x, y)
    references = prep_for_pickle(factorVals, xFirstDip, sigmaFirstDip, heightFirstDip, heightAtZero)
    print "generate_references returning"
    return references

def prep_for_pickle(factorVals, xFirstDip, sigmaFirstDip, heightFirstDip, heightAtZero):
    references = {}
    references['factorVals'] = factorVals
    references['xFirstDip'] = xFirstDip
    references['heightFirstDip'] = heightFirstDip
    references['sigmaFirstDip'] = sigmaFirstDip
    references['heightAtZero'] = heightAtZero
    #references['powerLaw'] = powerLaw
    return references

# xFirstDip, heightFirstDip, sigmaFirstDip, heightAtZero # , powerLawAll, powerLawInitial

# I/O functions

def load_references():
    with open(reference_loc, 'rb') as handle:
        references = pickle.load(handle)
    return references

def dump_references(references):
    with open(reference_loc, 'wb') as handle:
        pickle.dump(references, handle)

# Functions about algebraic solutions

def arbitrary_order_solution(order, x, y, dy=np.zeros(1)):
    '''Solves for a polynomial "fit" of arbitrary order.'''
    if not dy.any():
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
    powers = np.arange(coefficients.size)
    y = ((x ** powers) * coefficients).sum()
    return y

def vertical(array1d):
    '''Turn 1d array into 2d vertical vector.'''
    array1d = array1d.reshape((array1d.size, 1))
    return array1d

def horizontal(array1d):
    '''Turn 1d array into 2d horizontal vector.'''
    array1d = array1d.reshape((1, array1d.size))
    return array1d

def dummy(array1d):
    '''Turn 1d array into dummy-index vector for 2d matrix computation.

    Sum over the dummy index by taking *object.sum(axis=0)*.'''
    array1d = array1d.reshape((array1d.size, 1 , 1))
    return array1d

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
    index = np.arange(order+1)
    vector = (dummy(y) * dummy(x) ** vertical(index) * dummy(error)).sum(axis=0)
    index_block = horizontal(index) + vertical(index)
    matrix = (dummy(x) ** index_block * dummy(error)).sum(axis=0)
    return matrix, vector

def power_law_solution(x, y, dy=np.zeros(1)):
    '''Solves for a power law by solving for a linear fit in log-log space.'''
    # Note that if dy is zeros, logdy will also be zeros, triggering default behavior in arbitrary_order_solution also.
    if not dy.any():
        dy = np.ones(y.shape, dtype=float)
    logx = np.log(x)
    logy = np.log(y)
    logdy = np.log(dy)
    logLinearCoefficients = arbitrary_order_solution(1, logx, logy, logdy)
    prefactor = np.exp(logLinearCoefficients[0])
    exponent = logLinearCoefficients[1]
    powerCoefficients = np.array([prefactor, exponent])
    return powerCoefficients

# Functions about simulating SAXS patterns

def gen_q_vector(qmin, qmax, qstep):
    '''An inclusive-range version of np.arange.'''
    if np.mod((qmax - qmin), qstep) == 0:
        qmax = qmax + qstep
    q = np.arange(qmin, qmax, qstep)
    return q

def generate_spherical_diffraction(r0, poly, i0, q):
    x = q * r0
    i = i0 * blur(x, poly)
    return i

def fullFunction(x):
    y = ((np.sin(x) - x * np.cos(x)) * x**-3)**2
    return y

def gauss(x, x0, sigma):
    y = ((sigma * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((x - x0)/sigma)**2)
    return y

def generateRhoFactor(factor):
    '''

    :param factor: float
    :return:

    factor should be 0.1 for a sigma 10% of size
    '''
    factorCenter = 1
    factorMin = max(factorCenter-5*factor, 0.02)
    factorMax = factorCenter+5*factor
    factorVals = np.arange(factorMin, factorMax, factor*0.02)
    rhoVals = gauss(factorVals, factorCenter, factor)
    return factorVals, rhoVals

def factorStretched(x, factor):
    effective_x = x / factor
    y = fullFunction(effective_x)
    return y

def blur(x, factor):
    factorVals, rhoVals = generateRhoFactor(factor)
    deltaFactor = factorVals[1] - factorVals[0]
    ysum = np.zeros(x.shape)
    for ii in range(len(factorVals)):
        y = factorStretched(x, factorVals[ii])
        ysum += rhoVals[ii]*y*deltaFactor
    return ysum

# Funtions specifically about detecting SAXS properties

def guess_polydispersity(q, I, dI=np.zeros(1)):
#    global references
    if not dI.any():
        dI = np.ones(I.shape, dtype=float)
    print "finding dips and shoulders"
    dips, shoulders = choose_dips_and_shoulders(q, I, dI)
    print "finding 1st dip q"
    x1, scaledDipCoefficients = polydispersity_metric_qFirstDip(q, I, dips, dI)
    print "finding 1st dip I"
    y1 = polydispersity_metric_heightFirstDip(scaledDipCoefficients, x1)
    print "finding 1st dip width"
    x2 = polydispersity_metric_sigmaFirstDip(q, I, dips, shoulders, x1, y1)
    print "finding height at zero"
    y2 = polydispersity_metric_heightAtZero(x1, q, I, dI)
    x0 = x1 / x2
    y0 = y1 / y2
    print "summoning references"
    if len(references) == 0:
        print "loading references"
        references = load_references()
        print "references loaded"
    x = references['xFirstDip'] / references['sigmaFirstDip']
    y = references['heightFirstDip'] / references['heightAtZero']
    factor = references['factorVals']
    print "comparing to references"
    fractional_variation = guess_nearest_point_on_nonmonotonic_trace_normalized([x0, y0], [x, y], factor)
    return fractional_variation, x1

def choose_dips_and_shoulders(q, I, dI=np.zeros(1)):
    '''Find the location of dips (low points) and shoulders (high points).'''
    if not dI.any():
        dI = np.ones(I.shape, dtype=float)
    scaled_I = I * q ** 4 / dI
    dips = local_minima_detector(scaled_I)
    shoulders = local_maxima_detector(scaled_I)
    dips, shoulders = clean_extrema(dips, shoulders)
    return dips, shoulders

def clean_extrema(dips, shoulders):
    # Forbid rapid oscillation
    dips_above = dips[1:].copy()
    dips_below = dips[:-1].copy()
    shoulders_above = shoulders[1:].copy()
    shoulders_below = shoulders[:-1].copy()
    dips[:-1] = dips[:-1] & (~shoulders_above)
    dips[1:] = dips[1:] & (~shoulders_below)
    shoulders[:-1] = shoulders[:-1] & (~dips_above)
    shoulders[1:] = shoulders[1:] & (~dips_below)
    # Mark endpoints False
    dips[0:10] = False
    dips[-1] = False
    shoulders[0] = False
    shoulders[-1] = False
    return dips, shoulders

def guess_size(fractional_variation, first_dip_q):
#    global references
    if len(references) == 0:
        references = load_references()
    xFirstDip, factorVals = references['xFirstDip'], references['factorVals']
    first_dip_x = interp(fractional_variation, factorVals, xFirstDip)
    mean_size = first_dip_x / first_dip_q
    return mean_size

def polydispersity_metric_heightFirstDip(scaledQuadCoefficients, xdip):
    ydip = polynomial_value(scaledQuadCoefficients, xdip) * (xdip**-4)
    return ydip

def polydispersity_metric_heightAtZero(qFirstDip, q, I, dI=np.zeros(1)):
    if not dI.any():
        dI = np.ones(I.shape, dtype=float)
    low_q = (q < 0.75*qFirstDip)
    coefficients = arbitrary_order_solution(5, q[low_q], I[low_q], dI[low_q])
    heightAtZero = coefficients[0]
    return heightAtZero

def polydispersity_metric_qFirstDip(q, I, dips, dI=np.zeros(1)):
    '''Finds the location in *q* of the first dip.'''
    if not dI.any():
        dI = np.ones(I.shape, dtype=float)
    pad = 3
    firstDipIndex = np.where(dips)[0][0]
    lolim = firstDipIndex - pad
    hilim = firstDipIndex + pad
    scaled_I = I * q**4 / dI
    scaledQuadCoefficients = arbitrary_order_solution(2, q[lolim:hilim], scaled_I[lolim:hilim])
    xFirstDip = quadratic_extremum(scaledQuadCoefficients)
    return xFirstDip, scaledQuadCoefficients

def polydispersity_metric_sigmaFirstDip(q, I, dips, shoulders, qFirstDip, heightFirstDip, dI=np.zeros(1)):
    if not dI.any():
        dI = np.ones(I.shape, dtype=float)
    powerCoefficients = power_law_solution(q[shoulders], I[shoulders], dI[shoulders])
    powerLawAtDip = powerCoefficients[0] * (qFirstDip ** powerCoefficients[1])
    dipDepth = powerLawAtDip - heightFirstDip
    pad = 3
    firstDipIndex = np.where(dips)[0][0]
    lolim = firstDipIndex - pad
    hilim = firstDipIndex + pad
    quadCoefficients = arbitrary_order_solution(2, q[lolim:hilim], I[lolim:hilim], dI[lolim:hilim])
    dipCurvature = 2 * quadCoefficients[2]
    _, sigma = gauss_guess(dipDepth, dipCurvature)
    return sigma

# Other functions

def gauss_guess(signalMagnitude, signalCurvature):
    '''
    Guesses a gaussian intensity and width from signal magnitude and curvature.

    :param signalMagnitude: number-like with units of magnitude
    :param signalCurvature: number-like with units of magnitude per distance squared
    :return intensity, sigma:

    The solution given is not fitted; it is a first estimate to be used in fitting.
    '''
    sigma = (signalMagnitude / signalCurvature) ** 0.5
    intensity = signalMagnitude * sigma * (2 * np.pi) ** 0.5
    return intensity, sigma

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
    minima = local_maxima_detector(-y)
    return minima

'''
def guess_nearest_point_on_single_monotonic_trace(x0, x, y):
    ybest = interp(x0, x, y)
    return ybest

def guess_nearest_point_on_dual_monotonic_trace(x0, y0, x, y, variable):
    vbestx = guess_nearest_point_on_single_monotonic_trace(x0, x, variable)
    vbesty = guess_nearest_point_on_single_monotonic_trace(y0, y, variable)
    vbest = 0.5*(vbestx + vbesty)
    return vbest
'''

def guess_nearest_point_on_nonmonotonic_trace_normalized(loclist, tracelist, coordinate):
    '''Finds the nearest point to location *loclist* on a trace *tracelist*.

    *loclist* and *tracelist* are lists of the same length and type.
    Elements of *loclist* are floats; elements of *tracelist* are arrays of the same shape as *coordinate*.
    *coordinate* is the independent variable along which *tracelist* is varying.

    *tracelist* must have good sampling to start with or the algorithm will likely fail.'''
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
        coefficients = arbitrary_order_solution(2,coordinate[lolim:hilim],distances[lolim:hilim])
        best_coordinates[ii] = quadratic_extremum(coefficients)
        best_distances[ii] = polynomial_value(coefficients, best_coordinates[ii])
    best_distance = best_distances.min()
    best_coordinate = best_coordinates[np.where(best_distances == best_distance)[0][0]]
    return best_coordinate, best_distance
