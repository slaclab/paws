import numpy as np

from scipy.optimize import curve_fit

from ....Operation import Operation
from .... import optools
from .. import saxstools

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
        input_names = ['q','I','method','fit_params','ok_flag','dI']
        output_names = ['return_code','results','q_I_norm','q_I_guess']
        super(SphericalNormalSpectrumFit, self).__init__(input_names, output_names)

        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['method'] = str('String indicating choice of optimization method. Options: '
        + '(1) full_spectrum_chi2- sum of difference squared across entire q range. '
        + '(2) full_spectrum_chi2log- sum of difference of logarithm, squared, across entire q range. '
        + '(3) low_q_chi2- sum of difference squared in only the lowest half of measured q range. '
        + '(4) low_q_chi2log- sum of difference of logarithm, squared, in lowest half of measured q range. '
        + '(5) pearson- pearson correlation between measured and modeled spectra. '
        + '(6) pearson_log- pearson correlation between logarithms of measured and modeled spectra.'
        + '(7) low_q_pearson- pearson correlation between measured and modeled spectra. '
        + '(8) low_q_pearson_log- pearson correlation between logarithms of measured and modeled spectra.') 
        self.input_doc['fit_params'] = str('dict of inputs for fitting, including initial guess parameters and I(q=0). '
        + 'Should be a dict with the following keys (as strings): "r_mean", "sigma_r", "I_at_0". '
        + 'Expected units of the values, respectively: Angstrom, Angstrom, counts.')
        self.input_doc['ok_flag'] = str('Boolean indicating whether or not this optimization should be attempted. '
        + 'This is useful for skipping the optimization based on the results of previous operations.')
        self.input_doc['dI'] = '1d array of error estimates of intensity values (optional- input None to ignore)'
        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'Possible values: 0=success, 1=error, 2=warning')
        self.output_doc['results'] = str('dictionary containing results '
        + 'for mean size, standard deviation, and I(q=0). '
        + 'Dict keys (strings): "r_mean", "sigma_r", "I_at_0". '
        + 'Units: Angstrom, Angstrom, counts.')
        self.output_doc['q_I_norm'] = 'The input q,I(q) spectrum normalized so that I(q=0) is near 1'
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the theoretical intensity spectrum '
        + 'for the r_mean, sigma_r, and I_at_0 values in the results output') 

        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['method'] = optools.text_input
        self.input_src['fit_params'] = optools.wf_input
        self.input_src['ok_flag'] = optools.wf_input
        self.input_src['dI'] = optools.no_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['method'] = optools.str_type
        self.input_type['fit_params'] = optools.ref_type
        self.input_type['ok_flag'] = optools.ref_type
        # TODO: establish a good default here.
        #self.inputs['method'] = 'full_spectrum_chi2log' 

    def run(self):
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        if self.inputs['ok_flag']:
            q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
            m = self.inputs['method']
            params = self.inputs['fit_params']
            x_init = [params['r_mean'],params['sigma_r']]
            try:
                d_opt = saxstools.saxs_spherical_normal_fit(q,I,params['I_at_0'],m,x_init,dI)
            except Exception as ex:
                self.outputs['return_code'] = 1
                msg = str('[{}] optimization by {} failed '
                + 'while attempting to fit spectrum. message: '
                + '{}'.format(__name__,m,ex.message))
                self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'message':ex.message} 
                raise ex
            r0 = d_opt['r_mean']
            sigma_r = d_opt['sigma_r']
            I_at_0 = d_opt['I_at_0']
            self.outputs['results'] = {'r_mean':r0,'sigma_r':sigma_r,'I_at_0':I_at_0} 
            self.outputs['q_I_norm'] = q_I_norm 
            self.outputs['q_I_guess'] = q_I_guess 
            self.outputs['return_code'] = 1
        else:        
            self.outputs['results'] = {'r_mean':0,'sigma_r':0,'I_at_0':0,'message':'ok_flag was set to False- optimization skipped'} 

