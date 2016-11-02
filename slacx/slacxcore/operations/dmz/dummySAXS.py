xmin = 0.1
xmax = 50
xstep = 0.1

# unblep

def fullFunction(x):
    y = ((np.sin(x) - x * np.cos(x)) * x**-3)**2
    return y

def numerator(x):
    y = np.sin(x) - x * np.cos(x)
    return y

def lowQConstantApprox(x):
    y = x*0 + 1/9.
    return y

def lowQQuadraticApprox(x):
    y = -(x**2)/45. + 1/9.
    return y

def highQCosApprox(x):
    y = np.cos(x)**2 * x**-4
    return y

def highQPowerLawApprox(x):
    y = 0.5 * x**-4
    return y

def highQEnvelope(x):
    y = x**-4
    return y

def gauss(x, x0, sigma):
    y = ((sigma* (2*np.pi)**0.5)**-1 )*np.exp(-((x - x0)/(2*sigma))**2)
    return y

def generateRhoFactor(factor):
    factorCenter = 1
    factorMin = max(factorCenter-5*factor, 0.001)
    factorMax = factorCenter+5*factor
    factorVals = np.arange(factorMin, factorMax, factor*0.1)
    rhoVals = gauss(factorVals, factorCenter, factor)
    return factorVals, rhoVals

def factorStretched(x, factor):
    falseX = x / factor
    y = fullFunction(falseX)
    return y

def blur(x, factor):
    factorVals, rhoVals = generateRhoFactor(factor)
    deltaFactor = factorVals[1] - factorVals[0]
    ysum = np.zeros(x.shape)
    for ii in range(len(factorVals)):
        y = factorStretched(x, factorVals[ii])
        ysum += rhoVals[ii]*y*deltaFactor
    #print rhoVals.sum()
    #ymean = ysum/rhoVals.sum()
    return ysum # ymean

