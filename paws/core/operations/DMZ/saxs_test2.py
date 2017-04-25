from os.path import join
from os import listdir

import numpy as np
from scipy import interp

from matplotlib import pyplot as plt
#import pdb; pdb.set_trace()

meganame = "/Users/Amanda/Desktop/Travails/Programming/ImageProcessing/SampleData/Liheng/megaSAXSspreadsheet/megaSAXSspreadsheet.csv"

def load_mega():
    speclist = []
    for ii in range(6):
        a, b, c = 4*ii, 4*ii+1, 4*ii+2
        q, I, dI = np.loadtxt(meganame, dtype=float, delimiter=',', skiprows=2, converters={a:blanktoNaN, b:blanktoNaN, c:blanktoNaN}, usecols=(a, b, c), unpack=True)
        goods = ~np.isnan(q)
        q, I, dI = q[goods], I[goods], dI[goods]
        speclist.append([q, I, dI])
    q, I, dI = np.loadtxt(meganame, dtype=float, delimiter=',', skiprows=2, usecols=(24, 25, 26), unpack=True)
    speclist.append([q, I, dI])
    return speclist

def blanktoNaN(floatstring):
    try:
        return float(floatstring)
    except ValueError:
        return np.nan

def load_csv(path):
    q, I = np.loadtxt(path, dtype=float, delimiter=',', skiprows=1, unpack=True)
    return q, I


def guess(q, I, dI=None):
    qFirstDip, heightFirstDip, sigmaScaledFirstDip, heightAtZero, dips, shoulders, \
    detailed_flags = take_polydispersity_metrics(q, I, dI)
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
    fractional_variation, _, best_xy = guess_nearest_point_on_nonmonotonic_trace_normalized([x0, y0], [x, y],
                                                                                            factor)
    # guess the mean size
    xFirstDip = interp(fractional_variation, references['factorVals'], references['xFirstDip'])
    mean_size = xFirstDip / qFirstDip
    Imodel = generate_spherical_diffraction(q, heightAtZero, mean_size, fractional_variation)
    I_adjustment = I.sum() / Imodel.sum()
    heightAtZero = heightAtZero * I_adjustment
    Imodel = Imodel*I_adjustment
    # more checks
    # is highest value early? is qFirstDip late?
    if np.argmax(I) > int(0.3*I.size):
        detailed_flags['late_intensity_max'] = True
    if np.where(q<qFirstDip)[0][-1] < int(0.1*q.size):
        detailed_flags['early_qFirstDip'] = True
    # are there vaguely zinger-like or dead pixel-like features?
    curv = (I[2:] - 2*I[1:-1] + I[:-2])
    var = (curv**2).mean()**0.5
    if (curv < -5*var).any():
        detailed_flags['zinger_like_feature'] = True
    if (curv > 5*var).any():
        detailed_flags['dead_pixel_like_feature'] = True
    # vaguely figure-of-merit-like numbers
    detailed_flags['root_mean_square_diff'] = ((Imodel - I)**2).mean()**0.5
    logsafe = ~(np.isnan(I) | (I < 0))
    detailed_flags['logarithmic_root_mean_square_diff'] = np.e**(((np.log((Imodel - I)[logsafe]))**2).mean()**0.5)
    if dI is not None:
        detailed_flags['weighted_root_mean_square_diff'] = (((Imodel - I)/dI)**2).mean()**0.5
        logsafe = ~(np.isnan(I) | (I < 0) | np.isnan(dI) | (I <= dI))
        logdI = np.log(((I + dI)/I)[logsafe])
        detailed_flags['logarithmic_weighted_root_mean_square_diff'] = np.e**(((np.log(np.abs(Imodel - I)[logsafe]) / logdI)**2).mean()**0.5)
    return heightAtZero, mean_size, fractional_variation


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

def take_polydispersity_metrics(q, I, dI=None):
    detailed_flags = {}
    # find extrema
    dips = local_minima_detector(I*q**4)
    shoulders = local_maxima_detector(I*q**4)
    # Clean out end points and weak maxima
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
    return qFirstDip, heightFirstDip, widthFirstDip, heightAtZero, dips, shoulders, detailed_flags

def logsafe_zip(x, y):
    bad = (x <= 0) | (y <= 0) | np.isnan(y)
    x, y = x[~bad], y[~bad]
    x_y = np.zeros((x.size, 2))
    x_y[:, 0] = x
    x_y[:, 1] = y
    return x_y

# Functions about algebraic solutions

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

def generate_spherical_diffraction(q, i0, r0, poly):
    x = q * r0
    i = i0 * blur(x, poly)
    return i

def blur(x, factor):
    if factor == 0:
        return (3. * (np.sin(x) - x * np.cos(x)) * x**-3)**2
    factorCenter = 1
    factorMin = max(factorCenter-5*factor, 0.001)
    factorMax = factorCenter+5*factor
    factorStep = factor*0.02
    if np.mod((factorMax - factorMin), factorStep) == 0:
        factorMax += 0.5*factorStep
    factorVals = np.arange(factorMin, factorMax, factorStep)
    # normalized gaussian:
    # ((sigma * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((x - x0)/sigma)**2)
    rhoVals = ((factor * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((factorVals - 1.)/factor)**2)
    deltaFactor = factorVals[1] - factorVals[0]
    ysum = np.zeros(x.shape)
    for ii in range(len(factorVals)):
        effective_x = x / factorVals[ii]
        # spherical monodisperse diffraction:
        # (3. * (np.sin(x) - x * np.cos(x)) * x**-3)**2
        y = (3. * (np.sin(effective_x) - effective_x * np.cos(effective_x)) * effective_x**-3)**2
        ysum += rhoVals[ii]*y*deltaFactor
    return ysum

# Funtions specifically about detecting SAXS properties

def generate_references():
    x = np.arange(1.0, 15, 0.01)
    polylist = np.arange(1., 51., 0.5) * 0.01
    x1s = []
    i1s = []
    dxs = []
    i0s = []
    for poly in polylist:
        intensity = blur(x, poly)
        xFirstDip, heightFirstDip, widthFirstDip, heightAtZero, _,_,_ = take_polydispersity_metrics(x, intensity)
        x1s.append(xFirstDip)
        i1s.append(heightFirstDip)
        dxs.append(widthFirstDip)
        i0s.append(heightAtZero)
    references = {'factorVals' : polylist,
                  'xFirstDip' : np.array(x1s),
                  'widthFirstDip' : np.array(dxs),
                  'heightFirstDip' : np.array(i1s),
                  'heightAtZero' : np.array(i0s)}
    return references

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

#q, I, dI, dq = np.loadtxt(path, dtype=float, delimiter=',', unpack=True)

speclist = load_mega()
for jj in range(len(speclist)):
    ii = speclist[jj]
    q, I, dI = ii[0], ii[1], ii[2]
    fig, ax = plt.subplots()
    ax.plot(q,I,color='k',lw=2)
    heightAtZero, mean_size, fractional_variation = guess(q, I, dI)
    Imodel = generate_spherical_diffraction(q, heightAtZero, mean_size, fractional_variation)
    ax.plot(q,Imodel,color='b',lw=1)
    plt.xscale('log')
    plt.yscale('log')
print 'done'

loc = "/Users/Amanda/Data20161118/R1"
csvlist = [join(loc,ii) for ii in listdir(loc) if (ii[-4:] == '.csv')]
#for jj in range(len(csvlist)):
for jj in range(20):
    q, I = load_csv(csvlist[jj])
    fig, ax = plt.subplots()
    ax.plot(q,I,color='k',lw=2)
    heightAtZero, mean_size, fractional_variation = guess(q, I, dI)
    Imodel = generate_spherical_diffraction(q, heightAtZero, mean_size, fractional_variation)
    ax.plot(q,Imodel,color='b',lw=1)
    plt.xscale('log')
    plt.yscale('log')
print 'done'





