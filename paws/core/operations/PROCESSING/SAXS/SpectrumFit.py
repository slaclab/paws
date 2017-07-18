import numpy as np
import copy

from scipy.optimize import curve_fit

from ... import Operation as op
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
        + 'with entries optimized for all keys specified in fit_params.')
        self.output_doc['q_I_opt'] = str('n-by-2 array of q and the theoretical intensity spectrum, '
        + 'normalized so that I(q=0) is near 1.') 

        self.input_src['q'] = op.wf_input
        self.input_src['I'] = op.wf_input
        self.input_src['objfun'] = op.text_input
        self.input_src['fit_params'] = op.text_input
        self.input_src['features'] = op.wf_input
        self.input_type['q'] = op.ref_type
        self.input_type['I'] = op.ref_type
        self.input_type['objfun'] = op.str_type
        self.input_type['fit_params'] = op.str_type
        self.input_type['features'] = op.ref_type
        # TODO: establish a good default here.
        self.inputs['objfun'] = 'full_spectrum_chi2log' 

    def run(self):
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
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
        d_opt = saxstools.saxs_fit(q,I,m,f,p,c)

        f.update(d_opt)
        I_opt = saxstools.compute_saxs(q,f)
        q_I_opt = np.array([q,I_opt]).T
        self.outputs['features'] = f 
        self.outputs['q_I_opt'] = q_I_opt

