import numpy as np
from scipy import interp

from ...Operation import Operation
from ... import optools

class NPSAXSSizeGuess(Operation):
    """
    Use a SAXS spectrum (I(q) vs. q) to 
    guess the mean and standard deviation of particle sizes
    under the assumption of spherical nanoparticles
    with a Gaussian size distribution.
    TODO: document the algorithm here.
    Output the mean and standard deviation of particle radius,
    and the scattered intensity at q=0.

    Assumes the data have already been background subtracted, 
    smoothed, and otherwise cleaned.
    """

    def __init__(self):
        # TODO: deprecate debug_info
        input_names = ['q', 'I', 'dI']
        output_names = ['return_code','results','I_guess','debug_info']
        super(NPSAXSSizeGuess, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = '1d array of error estimates of intensity values (optional- input None to ignore)'
        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'values: -1=error, 0=not fittable, 1=fittable')
        self.output_doc['results'] = str('dictionary containing heuristic guesses for '
        + 'the mean size, standard deviation, and the inferred value of I(q=0). '
        + 'Dict keys (strings): "r_mean", "sigma_r", "I_at_0". Units: Angstrom, Angstrom, counts.')
        self.output_doc['debug_info'] = 'dict of information for debugging' 
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['dI'] = optools.ref_type

    def run(self):
        try:
            q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
            # If the maximum intensity is not somewhere up front, throw the flag
            # Any other ok_flag filters should be added here.
            if not np.argmax(I) in range(10):
                ok_flag = False
            else:
                ok_flag = True
            if not ok_flag: 
                self.outputs['return_code'] = 0
            else:
                ### the real work begins here ###

                ### these lines of code used to be take_polydispersity_metrics()
                dips = local_minima_detector(I*q**4)
                shoulders = local_maxima_detector(I*q**4)
                dips, shoulders = clean_extrema(dips, shoulders, I*q**4)
                # identify likely first "real" dip
                qFirstDip, heightFirstDip, scaledQuadCoefficients = first_dip(q, I, dips, shoulders, dI)
                # determine width scale
                qWidthIndex = np.where((I > heightFirstDip * 5.) & (q < qFirstDip))[0][-1]
                widthFirstDip = qFirstDip - q[qWidthIndex]
                # fit quadratic to low q to estimate amplitude at zero
                qlim = max(q[6], (qFirstDip - q[0]) / 2.)
                if qlim > 0.75 * qFirstDip:
                    detailed_flags['poor_low_q_sampling'] = True
                    print "Low-q sampling seems to be poor and will likely affect estimate quality."
                low_q = (q < qlim)
                if dI is None:
                    heightAtZero = arbitrary_order_solution(2, q[low_q], I[low_q], None)[0]
                else:
                    heightAtZero = arbitrary_order_solution(2, q[low_q], I[low_q], dI[low_q])[0]


                #qFirstDip, heightFirstDip, sigmaScaledFirstDip, heightAtZero, dips, shoulders, \
                #detailed_flags = take_polydispersity_metrics(q, I, dI)

        
        except ex:
            msg = 'An exception was raised during execution. Error message: {}'.format(ex.message) 
            dbg_info = {'err_msg':msg}
            self.outputs['debug_info'] = dbg_info
            self.outputs['return_code'] = -1




        # convert to unitless metrics
        x0 = sigmaScaledFirstDip / qFirstDip
        y0 = heightFirstDip / heightAtZero
        # compare metrics to reference
        try:
            factor = references['factorVals']
        except NameError:
            references = generate_references()
            factor = references['factorVals']
        x = references['widthFirstDip'] / references['xFirstDip']
        y = references['heightFirstDip'] / references['heightAtZero']
        fractional_variation, _, best_xy = guess_nearest_point_on_nonmonotonic_trace_normalized([x0, y0], [x, y], factor)
        # guess the mean size
        xFirstDip = interp(fractional_variation, references['factorVals'], references['xFirstDip'])
        mean_size = xFirstDip / qFirstDip
        Imodel = generate_spherical_diffraction(q, heightAtZero, mean_size, fractional_variation)
        I_adjustment = I.sum() / Imodel.sum()
        heightAtZero = heightAtZero * I_adjustment
        # more checks
        # is highest value early? is qFirstDip late?
        if np.argmax(I) > int(0.3 * I.size):
            detailed_flags['late_intensity_max'] = True
        if np.where(q < qFirstDip)[0][-1] < int(0.1 * q.size):
            detailed_flags['early_qFirstDip'] = True
        # are there vaguely zinger-like or dead pixel-like features?
        curv = (I[2:] - 2 * I[1:-1] + I[:-2])
        var = (curv ** 2).mean() ** 0.5
        if (curv < -5 * var).any():
            detailed_flags['zinger_like_feature'] = True
        if (curv > 5 * var).any():
            detailed_flags['dead_pixel_like_feature'] = True
        # vaguely figure-of-merit-like numbers
        detailed_flags['root_mean_square_diff'] = ((Imodel - I) ** 2).mean() ** 0.5
        logsafe = ~(np.isnan(I) | (I < 0))
        detailed_flags['logarithmic_root_mean_square_diff'] = np.e ** (
        ((np.log((Imodel - I)[logsafe])) ** 2).mean() ** 0.5)
        if dI is not None:
            detailed_flags['weighted_root_mean_square_diff'] = (((Imodel - I) / dI) ** 2).mean() ** 0.5
            logsafe = ~(np.isnan(I) | (I < 0) | np.isnan(dI) | (I <= dI))
            logdI = np.log(((I + dI) / I)[logsafe])
            detailed_flags['logarithmic_weighted_root_mean_square_diff'] = np.e ** (
            ((np.log(np.abs(Imodel - I)[logsafe]) / logdI) ** 2).mean() ** 0.5)

        self.outputs['detailed_flags'] = detailed_flags
        self.outputs['additional_information'] = {'qFirstDip':qFirstDip, 'sigmaScaledFirstDip':sigmaScaledFirstDip,
                                  'heightFirstDip':heightFirstDip, 'dips':dips, 'shoulders':shoulders}
        self.outputs['parameter_guesses'] = {'fractional_variation':fractional_variation, 'mean_size':mean_size, 'amplitude_at_zero':heightAtZero}
        self.outputs['I_guess'] = generate_spherical_diffraction(q, heightAtZero, mean_size, fractional_variation)
        self.outputs['q_I_guess'] = logsafe_zip(q, self.outputs['I_guess'])
        # if any of the detailed flags are bad set good_flag to False
        self.outputs['good_flag'] = True
        for ii in self.outputs['detailed_flags']:
            if self.outputs['detailed_flags'][ii] == False:
                self.outputs['good_flag'] = False

def logsafe_zip(x, y):
    bad = (x <= 0) | (y <= 0) | np.isnan(y)
    x, y = x[~bad], y[~bad]
    x_y = np.zeros((x.size, 2))
    x_y[:, 0] = x
    x_y[:, 1] = y
    return x_y

def first_dip(q, I, dips, shoulders, dI=None):
    y = I*q**4
    # Get a vague idea of the scale of the intensity vector
    n = max(int(0.5 * y.size**0.5), 7)
    # trend True if initially increasing, False otherwise
    trend = ((y[1:n+1] - y[:n]).mean() > 0)
    if trend:
        # the 1st minimum after the 1st maximum
        firstmax = np.where(shoulders)[0][0]
        mincandidates = (np.arange(y.size) > firstmax)
        firstmin = np.where(dips & mincandidates)[0][0]
    else:
        # the 1st minimum
        firstmin = np.where(dips)[0][0]

    q1 = q[firstmin]
    minq = q1*0.9
    maxq = q1*1.1
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
    if dI is None:
        coefficients = arbitrary_order_solution(2, q[selection], (I*q**4)[selection], None)
    else:
        coefficients = arbitrary_order_solution(2, q[selection], (I*q**4)[selection], dI[selection])
    qbest =  -0.5*coefficients[1]/coefficients[2]
    Ibest = polynomial_value(coefficients, qbest)*qbest**-4
    return qbest, Ibest, coefficients  #?

def arbitrary_order_solution(order, x, y, dy=None):
    '''Solves for a polynomial "fit" of arbitrary order.'''
    if dy is None:
        dy = np.ones(y.shape, dtype=float)
    # Formulate the equation to be solved for polynomial coefficients
    if ((x.shape != y.shape) or (y.shape != dy.shape)):
        raise ValueError('Arguments *x*, *y*, and *dy* must all have the same shape.')
    size = x.size
    index = np.arange(order+1)
    # (n, 1, 1) a dummy vector to be summed over index zero
    # (m, 1) a vertical vector
    # (1, m) a horizontal vector
    vector = (y.reshape(size,1,1) * x.reshape(size,1,1) ** index.reshape(order+1,1) * dy.reshape(size,1,1)).sum(axis=0)
    index_block = index.reshape(1,order+1) + index.reshape(order+1,1)
    matrix = (x.reshape(size,1,1) ** index_block * dy.reshape(size,1,1)).sum(axis=0)
    # Solve equation
    inverse = np.linalg.pinv(matrix)
    coefficients = np.matmul(inverse, vector)
    coefficients = coefficients.flatten()
    return coefficients

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

# Functions about simulating SAXS patterns

def generate_spherical_diffraction(q, i0, r0, frac_std_r):
    # frac_std_r is std(r)/r0
    x = q * r0
    i = i0 * blur(x, frac_std_r)
    return i

def blur(x, frac_std_r):
    # frac_std_r is std(r)/r0
    # x is the domain, in this case q*r0
    # fractional_poly is std(r0)/r0 
    if fractional_poly == 0:
        # monodisperse spherical pattern
        return (3.*(np.sin(x)-x*np.cos(x))*x**-3)**2
    # else, we are generating a 'blur'red spectrum on a distribution of sizes
    # 'factor' is the factor by which the mean size is scaled,
    # for each of the monodisperse spectra that get summed together
    # to generate the blurred one.
    I_blurred = np.zeros(shape(x))
        

    return np.sum([],axis=0)

    factorCenter = 1
    factorMin = max(factorCenter-5*factor, 0.001)
    factorMax = factorCenter+5*factor
    factorStep = factor*0.02
    if np.mod((factorMax - factorMin), factorStep) == 0:
        factorMax += 0.5*factorStep
    factorVals = np.arange(factorMin, factorMax, factorStep)
    deltaFactor = factorVals[1] - factorVals[0]
    # normalized gaussian:
    # ((sigma * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((x - x0)/sigma)**2)
    rhoVals = ((factor * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((factorVals - 1.)/factor)**2)
    ysum = np.zeros(x.shape)
    for ii in range(len(factorVals)):
        effective_x = x / factorVals[ii]
        # spherical monodisperse diffraction:
        # (3. * (np.sin(x) - x * np.cos(x)) * x**-3)**2
        y = (3. * (np.sin(effective_x) - effective_x * np.cos(effective_x)) * effective_x**-3)**2
        ysum += rhoVals[ii]*y*deltaFactor
    return ysum

# Functions specifically about detecting SAXS properties

def clean_extrema(dips, shoulders, y):
    #y = I*q**4
    # Get a vague idea of the scale of the intensity vector
    n = max(int(0.5 * y.size**0.5), 7)
    dn = int(0.5 * n)
    # Reject weaksauce local maxima and minima
    refdips = dips.copy()
    for ii in np.where(refdips)[0]:
        i1 = max((ii-dn), 0)
        i2 = min((ii+dn), y.size)
        if y[ii] != np.min(y[i1:i2]):
            dips[ii] = False
    refshoulders = shoulders.copy()
    for ii in np.where(refshoulders)[0]:
        i1 = max((ii-dn), 0)
        i2 = min((ii+dn), y.size)
        if y[ii] != np.max(y[i1:i2]):
            shoulders[ii] = False
    return dips, shoulders

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
        best_coordinates[ii] = -0.5 * distance_coefficients[1] / distance_coefficients[2]
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

# generate references that will be used by this operation

references = generate_references()

#def take_polydispersity_metrics(q, I, dI=None):
#    detailed_flags = {}
#    # find extrema
#    dips = local_minima_detector(I*q**4)
#    shoulders = local_maxima_detector(I*q**4)
#    # Clean out end points and weak maxima
#    dips, shoulders = clean_extrema(dips, shoulders, I*q**4)
#    # identify likely first "real" dip
#    qFirstDip, heightFirstDip, scaledQuadCoefficients = first_dip(q, I, dips, shoulders, dI)
#    # determine width scale
#    qWidthIndex = np.where((I > heightFirstDip * 5.) & (q < qFirstDip))[0][-1]
#    widthFirstDip = qFirstDip - q[qWidthIndex]
#
#    # fit quadratic to low q to estimate amplitude at zero
#    qlim = max(q[6], (qFirstDip - q[0]) / 2.)
#    if qlim > 0.75 * qFirstDip:
#        detailed_flags['poor_low_q_sampling'] = True
#        print "Low-q sampling seems to be poor and will likely affect estimate quality."
#    low_q = (q < qlim)
#    if dI is None:
#        heightAtZero = arbitrary_order_solution(2, q[low_q], I[low_q], None)[0]
#    else:
#        heightAtZero = arbitrary_order_solution(2, q[low_q], I[low_q], dI[low_q])[0]
#    return qFirstDip, heightFirstDip, widthFirstDip, heightAtZero, dips, shoulders, detailed_flags

# Functions about algebraic solutions






