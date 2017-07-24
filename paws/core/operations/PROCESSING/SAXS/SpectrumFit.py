import numpy as np
import copy

from scipy.optimize import curve_fit

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class SpectrumFit(Operation):
    """
    Use a measured SAXS spectrum (I(q) vs. q),
    to optimize the parameters of a theoretical SAXS spectrum
    for one or several populations of scatterers. 
    Works by minimizing an objective function that compares
    the measured spectrum against the theoretical result.
    TODO: document the algorithm here.

    Input arrays of q and I(q), 
    a string indicating choice of objective function, 
    a dict of features describing the spectrum,
    and a list of strings indicating which keys in the dict 
    should be used as optimization parameters.
    The input features dict includes initial fit parameters
    as well as the flags indicating which populations to include.
    The features dict is of the same format as
    SpectrumProfiler and SpectrumParameterization outputs.

    Outputs a return code and the features dict,
    with entries updated for the optimized parameters.
    Also returns the theoretical result for I(q),
    and a renormalized measured spectrum for visual comparison.
    """

    def __init__(self):
        input_names = ['q','I','features','fit_params','objfun']
        output_names = ['features','q_I_opt']
        super(SpectrumFit, self).__init__(input_names, output_names)

        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['features'] = str('dict of features describing the input spectrum and scatterer populations. '
        + 'Keys of this dict are the same as the SpectrumParameterization.outputs.features dict.')
        self.input_doc['fit_params'] = str('List of strings indicating which parameters to optimize. '
        + 'Each of these strings should also be a key of the input features dict.')
        self.input_doc['objfun'] = str('String indicating choice of objective function for optimization. '
        + 'See documentation of saxstools.saxs_fit() for supported objective functions.')
        #self.input_doc['constraints'] = str('List of strings indicating optimization constraints. '
        #+ 'See documentation of saxstools.fit_saxs() for supported constraints.')

        self.output_doc['features'] = str('dict of features copied from inputs, '
        + 'with entries optimized for all keys specified in fit_params. '
        + 'Adds the following keys: \n' 
        + 'R2log_fit: Coefficient of determination between the measured and optimized spectra. ' 
        + 'chi2log_fit: Sum of difference squared between standardized logarithms '
        + 'of measured and optimized spectra. Standardized by the measured spectrum. ') 
        self.output_doc['q_I_opt'] = str('n-by-2 array of q and the theoretical intensity spectrum, '
        + 'normalized so that I(q=0) is near 1.') 

        self.input_src['q'] = opmod.wf_input
        self.input_src['I'] = opmod.wf_input
        self.input_src['objfun'] = opmod.text_input
        self.input_src['fit_params'] = opmod.text_input
        self.input_src['features'] = opmod.wf_input
        self.input_type['q'] = opmod.ref_type
        self.input_type['I'] = opmod.ref_type
        self.input_type['objfun'] = opmod.str_type
        self.input_type['fit_params'] = opmod.str_type
        self.input_type['features'] = opmod.ref_type
        # TODO: establish a good default here.
        self.inputs['objfun'] = 'chi2log' 

    def run(self):
        f = copy.deepcopy(self.inputs['features'])
        if not any([f['precursor_flag'],f['form_flag'],f['structure_flag']]):
            self.outputs['features'] = f
            return
        if f['bad_data_flag']: 
            self.outputs['features'] = f
            return
        if f['structure_flag']:
            f['ERROR_MESSAGE'] = '[{}] structure factor fitting not yet supported'.format(__name__)
            self.outputs['features'] = f
            return
        q, I = self.inputs['q'], self.inputs['I']
        m = self.inputs['objfun']
        p = self.inputs['fit_params']

        # Set up constraints as needed
        c = []
        if f['form_flag'] or f['structure_flag']:
            c = ['fix_I0']

        # Fitting happens here
        #print 'fitting {}'.format(p)
        #print 'init: {}'.format([f[k] for k in p])
        d_opt = saxstools.saxs_fit(q,I,m,f,p,c)
        #print 'final: {}'.format([d_opt[k] for k in p])

        f.update(d_opt)
        I_opt = saxstools.compute_saxs(q,f)

        nz = ((I>0)&(I_opt>0))
        logI_nz = np.log(I[nz])
        logIopt_nz = np.log(I_opt[nz])
        Imean = np.mean(logI_nz)
        Istd = np.std(logI_nz)
        logI_nz_s = (logI_nz - Imean) / Istd
        logIopt_nz_s = (logIopt_nz - Imean) / Istd
        f['R2log_fit'] = saxstools.compute_Rsquared(np.log(I[nz]),np.log(I_opt[nz]))
        f['chi2log_fit'] = saxstools.compute_chi2(logI_nz_s,logIopt_nz_s)

        q_I_opt = np.array([q,I_opt]).T
        self.outputs['features'] = f 
        self.outputs['q_I_opt'] = q_I_opt

