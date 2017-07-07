import numpy as np
import copy

from scipy.optimize import curve_fit

from ...Operation import Operation
from ... import optools
from . import saxstools

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
        output_names = ['return_code','features','q_I_opt']
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

        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'Possible values: 0=success, 1=error, 2=warning')
        self.output_doc['features'] = str('dict of features copied from inputs, '
        + 'with entries optimized for all keys specified in fit_params.')
        self.output_doc['q_I_opt'] = str('n-by-2 array of q and the theoretical intensity spectrum, '
        + 'normalized so that I(q=0) is near 1.') 

        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['objfun'] = optools.text_input
        self.input_src['fit_params'] = optools.text_input
        self.input_src['features'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['objfun'] = optools.str_type
        self.input_type['fit_params'] = optools.str_type
        self.input_type['features'] = optools.ref_type
        # TODO: establish a good default here.
        self.inputs['objfun'] = 'full_spectrum_chi2log' 

    def run(self):
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        q, I = self.inputs['q'], self.inputs['I']
        m = self.inputs['objfun']
        p = self.inputs['fit_params']
        f = copy.deepcopy(self.inputs['features'])
        if f['bad_data_flag']:
            # sabotage
            self.outputs['return_code'] = 2
            f['FIT_ERROR'] = '[{}] found bad_data flag, aborting'.format(__name__)
            self.outputs['features'] = f
            return
        c = []
        if f['form_flag'] or f['structure_flag']:
            c = ['fix_I0']
        #c = self.inputs['constraints'] 
        #try:
        #print f
        d_opt = saxstools.saxs_fit(q,I,m,f,p,c)
        f.update(d_opt)
        #print d_opt
            #for k in p:
            #    f[k] = d_opt[k]
        #except Exception as ex:
        #    msg = str('[{}] optimization by {} failed '
        #    + 'while attempting to fit spectrum. message: '
        #    + '{}'.format(__name__,m,ex.message))
        #    raise ex

        I_opt = saxstools.compute_saxs(q,f)
        q_I_opt = np.array([q,I_opt]).T

        self.outputs['features'] = f 
        self.outputs['q_I_opt'] = q_I_opt
        self.outputs['return_code'] = 0

