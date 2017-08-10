from collections import OrderedDict

import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class SpectrumParameterization(Operation):
    """
    The algorithm for guessing parameters
    for the size distributions of spherical nanoparticles 
    was developed and originally contributed by Amanda Fournier.    

    This operation uses a SAXS spectrum (I(q) vs. q), 
    along with some profiling information,
    to guess a set of parameters
    for fitting the SAXS spectrum
    to theoretical scattering models. 
    TODO: document scattering models.

    A precursor is modeled by a dilute, monodisperse spherical form factor.
    A spherical nanoparticle population is modeled by
    a discrete sum over a probability distribution
    of dilute, monodisperse spherical form factors. 
    A crystalline arrangement is modeled by 
    a sum of pseudo-Voigt peaks.

    Outputs a return code and heuristic guesses for SAXS model parameters. 
    Also outputs the theoretical result for I(q) with the guessed parameters.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q', 'I', 'features', 'fixed_params', 'fixed_param_values']
        output_names = ['features','q_I_guess']
        super(SpectrumParameterization, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['features'] = str('dict of outputs from spectrum profiler operation. \n'
        + 'This operation makes use of the following keys: \n'
        + 'precursor_flag: Boolean for whether or not to include '
        + 'monodisperse spherical precursor parameters '
        + '(2 parameters: precursor radius and intensity scaling factor). \n'
        + 'form_flag: Boolean for whether or not to include '
        + 'normally-distributed spherical form factor parameters '
        + '(3 parameters: mean radius, standard deviation of radius, intensity scaling factor). \n'
        + 'structure_flag: Boolean for whether or not to include '
        + 'a set of Pseudo-Voigt diffraction peak parameters '
        + '(3 parameters: principal peak location, peak width, intensity scaling factor). \n'
        + 'form_id: string indicating the form factor '
        + '(options: sphere). \n'
        + 'structure_id: string indicating the structure to use in setting the diffraction peaks '
        + '(options: currently none, eventually fcc, hcp, bcc, etc).')
        self.input_doc['fixed_params'] = str('list of strings indicating which parameters '
        + 'should be fixed to specified values- these correspond one-to-one with fixed_param_values.')
        self.input_doc['fixed_param_values'] = 'list of values to which the corresponding fixed_params will be set.'

        self.output_doc['features'] = str('dict of features, same as input features, ' 
        + 'but updated with parameters for the flagged populations. ' 
        + 'Dict keys and descriptions: \n' 
        + 'I_at_0: Intensity at q=0, by fitting the low-q region to a polynomial with dI/dq(q=0)=0. \n' 
        + 'r0_pre: precursor term radius (Angstrom). \n'
        + 'I0_pre: precursor intensity scaling factor. \n'
        + 'r0_form: mean characteristic size (Angstrom) of form factor population. \n'
        + 'sigma_form: fractional standard deviation of characteristic size of form factor population \n'
        + 'I0_form: form factor scattering intensity scaling factor \n'
        + 'q0_structure: q value (1/Angstrom) for location of fundamental structure factor peak \n' 
        + 'I0_structure: structure factor intensity scaling factor \n'
        + 'sigma_structure: width parameter for Pseudo-Voigt diffraction peak profile \n' 
        + 'R2log_guess: Coefficient of determination between logarithms of measured and parameterized spectra \n' 
        + 'chi2log_guess: Sum of difference squared between standardized logarithms '
        + 'of measured and parameterized spectra. '
        + 'Both spectra are standardized by the mean and std of the measured spectrum. ') 
        self.output_doc['q_I_guess'] = str('n-by-2 array of q and the intensity spectrum '
        + 'corresponding to the population parameters in the features dict.')

        self.input_src['q'] = opmod.wf_input
        self.input_src['I'] = opmod.wf_input
        self.input_src['features'] = opmod.wf_input
        self.input_type['q'] = opmod.ref_type
        self.input_type['I'] = opmod.ref_type
        self.input_type['features'] = opmod.ref_type

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        p = self.inputs['features'] 

        fix_keys = self.inputs['fixed_params']
        fix_vals = self.inputs['fixed_param_values']
        p_fix = {}
        for k,v in zip(fix_keys,fix_vals):
            p_fix[k] = v

        p_new = saxstools.parameterize_spectrum(q,I,p,p_fix)

        try:
            I_guess = saxstools.compute_saxs(q,p_new)
        except Exception as ex:
            import pdb; pdb.set_trace()

        q_I_guess = np.array([q,I_guess]).T
        self.outputs['features'] = p_new
        self.outputs['q_I_guess'] = q_I_guess 




