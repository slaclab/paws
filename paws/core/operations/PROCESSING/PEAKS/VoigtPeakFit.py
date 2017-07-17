import numpy as np
from matplotlib.figure import Figure
from scipy.special import wofz
from scipy.optimize import minimize as scimin

from ... import Operation as op
from ...Operation import Operation

class VoigtPeakFit(Operation):
    """
    Fit a set of x and y values to a Voigt distribution.
    Solves the best-fitting hwhm (half width at half max) 
    of the gaussian and lorentzian distributions and shared distribution center.
    Takes as input a guess for the distribution center and hwhm.
    Range of fit is determined by weighting the objective 
    by a Hann window centered at the distribution center,
    with a window width of the distribution's estimated full width at half max.
    """

    def __init__(self):
        input_names = ['x','y','xguess','hwhm']
        output_names = ['y_voigt','xpk','ypk','hwhm_g','hwhm_l','prefactor','plot']
        super(VoigtPeakFit,self).__init__(input_names, output_names)
        self.input_doc['x'] = '1d array of x values (domain)'
        self.input_doc['y'] = '1d array of y values (amplitudes)'
        self.input_doc['xguess'] = 'initial guess for the center of the voigt profile'
        self.input_doc['hwhm'] = 'initial guess for the half width at half max of the voigt profile'
        self.input_src['x'] = op.wf_input
        self.input_src['y'] = op.wf_input
        self.input_src['xguess'] = op.wf_input
        self.input_src['hwhm'] = op.wf_input
        self.input_type['x'] = op.ref_type
        self.input_type['y'] = op.ref_type
        self.input_type['xguess'] = op.int_type
        self.input_type['hwhm'] = op.float_type
        self.output_doc['y_voigt'] = 'the optimized voigt profile'
        self.output_doc['xguess'] = 'optimized voigt profile distribution center'
        self.output_doc['ypk'] = 'optimized voigt profile peak amplitude'
        self.output_doc['hwhm_g'] = 'optimized voigt profile gaussian component hwhm'
        self.output_doc['hwhm_l'] = 'optimized voigt profile lorentzian component hwhm'
        self.output_doc['prefactor'] = 'optimized voigt profile multiplicative prefactor'
        self.output_doc['plot'] = 'matplotlib Figure for inspecting the fit results'

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        xpk = self.inputs['xguess']
        hwhm = self.inputs['hwhm']
        # get y value nearest xpk guess, use it to guess a scaling factor
        ypk = y[np.argmin((x-xpk)**2)]
        scl = ypk / self.voigt(0, hwhm, hwhm)
        xpk, hwhm_g, hwhm_l, scl = self.solve_voigt(x,y,xpk,hwhm,hwhm,scl)
        mpl_fig = Figure(figsize=(100,100))
        ax = mpl_fig.add_subplot(111)
        ax.plot(x,y)
        y_voigt = self.voigt(x,hwhm_g,hwhm_l)
        ax.plot(x,y_voigt,'r')
        self.outputs['y_voigt'] = y_voigt
        self.outputs['xpk'] = xpk
        self.outputs['hwhm_g'] = hwhm_g
        self.outputs['hwhm_l'] = hwhm_l
        self.outputs['prefactor'] = scl
        self.outputs['plot'] = mpl_fig

    @staticmethod
    def solve_voigt(x, y, xc, hwhm_g, hwhm_l, scl):
        """iteratively minimize an objective to fit x, y curve to a voigt profile"""
        res = scimin(partial(self.hann_voigt_fit,x,y),(xc,hwhm_g,hwhm_l,scl))

    @staticmethod
    def hann_voigt_fit(x, y, xc, hwhm_g, hwhm_l, scl):
        # estimate hwhm of voigt
        # hwhm estimation params from https://en.wikipedia.org/wiki/Voigt_profile
        phi = hwhm_l / hwhm_g
        c0 = 2.0056; c1 = 1.0593 
        hwhm_voigt = hwhm_g * (1 - c0*c1 + np.sqrt(phi**2 + 2*c1*phi +c0**2*c1**2))
        # x,y values in the window region
        i_win = np.array([i for i in range(len(y)) if x[i] > xc-hwhm_voigt and x[i] < xc+hwhm_voigt])
        y_win = np.array([y[i] for i in i_win])
        x_win = np.array([x[i] for i in i_win])
        n_win = len(i_win)
        # window weights
        w_win = 0.5 * (1 - np.cos(2*np.pi*np.arange(n_win)/(n_win-1)) )
        # voigt profile in window, scaled by scl
        y_voigt = scl*self.voigt(x_win-xc,hwhm_g,hwhm_l)
        return np.sum(w_win * (y_voigt - y_win)**2)

    @staticmethod
    def gaussian(x, hwhm_g):
        """
        gaussian distribution at points x, 
        center 0, half width at half max hwhm_g
        """
        return np.sqrt(np.log(2)/np.pi) / hwhm_g * np.exp(-(x/hwhm_g)**2 * np.log(2))

    @staticmethod
    def lorentzian(x, hwhm_l):
        """
        lorentzian distribution at points x, 
        center 0, half width at half max hwhm_l
        """
        return hwhm_l / np.pi / (x**2+hwhm_l**2)

    @staticmethod
    def voigt(x, hwhm_g, hwhm_l):
        """
        voigt distribution resulting from convolution 
        of a gaussian with hwhm hwhm_g 
        and a lorentzian with hwhm hwhm_l
        """
        sigma = hwhm_g / np.sqrt(2 * np.log(2))
        return np.real(wofz((x+1j*hwhm_l)/sigma/np.sqrt(2))) / sigma / np.sqrt(2*np.pi)
