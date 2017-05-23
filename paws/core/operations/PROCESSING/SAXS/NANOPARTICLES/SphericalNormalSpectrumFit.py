import numpy as np

from scipy.optimize import curve_fit

from ....Operation import Operation
from .... import optools
from ....DMZ import saxstools

class SphericalNormalSpectrumFit(Operation):
    """
    Use a SAXS spectrum (I(q) vs. q),
    for spherical nanoparticles with a normal size distribution,
    to find the mean and standard deviation of particle sizes
    by minimizing an objective function that compares
    the measured spectrum against the theoretical result 
    for those distribution parameters.
    TODO: document the algorithm here.

    Output a return code and diagnostics as needed.
    In case of success, report the size distribution parameters
    and the approximate scattered intensity at q=0.
    Also return the corresponding theoretical result for I(q),
    alongside a renormalized measured spectrum, for visual comparison.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q','I','method','inital_guess','dI']
        output_names = ['return_code','results','q_I_norm','q_I_guess']
        super(SphericalNormalHeuristics, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['method'] = str('String indicating choice of optimization method. Options: '
        + '(1) full_spectrum_chi2- sum of difference squared across entire q range. '
        + '(2) full_spectrum_chi2log (TODO)- sum of difference of logarithm, squared, across entire q range. '
        + '(3) low_q_chi2 (TODO)- sum of difference squared in only the lowest 20% of measured q range. '
        + '(4) low_q_chi2log (TODO)- sum of difference of logarithm, squared, in lowest 20% of measured q range. '
        + '(5) pearson (TODO)- pearson correlation between measured and theoretical spectra. '
        + '(6) pearson_log (TODO)- pearson correlation between logarithms of measured and theoretical spectra.') 
        self.input_doc['initial_guess'] = str('dict of initial guesses for size distribution parameters. '
        + 'Dict keys (strings): "r_mean", "sigma_r", "I_at_0". Units: Angstrom, Angstrom, counts.')
        self.input_doc['dI'] = '1d array of error estimates of intensity values (optional- input None to ignore)'
        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'Possible values: -1=error, 0=not fittable, 1=fittable')
        self.output_doc['results'] = str('dictionary containing results '
        + 'for mean size, standard deviation, and I(q=0). '
        + 'Dict keys (strings): "r_mean", "sigma_r", "I_at_0". '
        + 'Units: Angstrom, Angstrom, counts.')
        self.output_doc['q_I_norm'] = 'The input q,I(q) spectrum normalized so that I(q=0) is near 1'
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the theoretical intensity spectrum '
        + 'for the r_mean, sigma_r, and I_at_0 values in the results output') 
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['method'] = optools.text_input
        self.input_src['initial_guess'] = optools.wf_input
        self.input_src['dI'] = optools.no_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['method'] = optools.str_type
        self.input_type['inital_guess'] = optools.ref_type
        self.inputs['method'] = 'full_spectrum_chi2' 

    def run(self):
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        self.outputs['return_code'] = -1
        
        m = self.inputs['method']
        if m in ['full_spectrum_chi2']:
            try:
                d_opt = self.spectrum_fit(q,I,m,dI)
            except Exception as ex:
                self.outputs['return_code'] = -1
                self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'message':d_opt['message']} 
                raise ex
        else:
            raise ValueError('Chosen optimization method {} is not supported.'.format(m))

        if not d_opt['return_code'] == 1:
            self.outputs['return_code'] = 0 
            msg = '[{}] feature optimization by {} failed. message: {}'.format(__name__,m,d_opt['message'])
            self.outputs['results'] = {'message':msg}
        else:        
            r0 = d_opt['r_mean']
            sigma_r = d_opt['sigma_r']
            I_at_0 = d_opt['I_at_0']
            self.outputs['results'] = {'r_mean':r0,'sigma_r':sigma_r,'I_at_0':I_at_0} 
            self.outputs['q_I_norm'] = q_I_norm 
            self.outputs['q_I_guess'] = q_I_guess 
            self.outputs['return_code'] = 1

    @staticmethod
    def spectrum_fit(q,I,method,dI=None):
        try:
            # Results are reported in a dict 
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
            d['return_code'] == 1
            return d
        except Exception as ex:
            d['return_code'] = -1
            d['message'] = ex.message
            return d






