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
    for fitting a SAXS spectrum
    to theoretical scattering models. 
    TODO: document scattering models.

    A precursor is modeled by a dilute, monodisperse spherical form factor.
    TODO: Implement Guinier-Porod.
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
        input_names = ['q', 'I', 'flags', 'fixed_params', 'fixed_param_values']
        output_names = ['params','q_I_guess']
        super(SpectrumParameterization, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['flags'] = 'dict of population flags- currently supported: '\
        '"bad_data", "precursor_scattering", "form_factor_scattering", "diffraction_peaks"'
        self.input_doc['fixed_params'] = 'list of strings indicating which parameters '\
        'should be fixed to specified values- these correspond one-to-one with fixed_param_values.'
        self.input_doc['fixed_param_values'] = 'list of values to which the corresponding fixed_params will be set.'

        self.output_doc['params'] = 'dict of scattering equation parameters: '\
        '"I_at_0": Intensity at q=0, by fitting the low-q region to a polynomial with dI/dq(q=0)=0; '\
        '"r0_pre": precursor term radius (Angstrom); '\
        '"I0_pre": precursor intensity scaling factor; '\
        '"r0_form": mean characteristic size (Angstrom) of form factor population; '\
        '"sigma_form": fractional standard deviation of characteristic size of form factor population; '\
        '"I0_form": form factor scattering intensity scaling factor; '\
        '"q0_structure": q value (1/Angstrom) for location of fundamental structure factor peak; '\
        '"I0_structure": structure factor intensity scaling factor; '\
        '"sigma_structure": width parameter for Pseudo-Voigt diffraction peak profile; '\
        '"R2log_guess": Coefficient of determination between logarithms of measured and parameterized spectra; '\
        '"chi2log_guess": Sum of difference squared between standardized logarithms '\
        'of measured and parameterized spectra, where both spectra are standardized '\
        'by the mean and std of the measured spectrum' 
        self.output_doc['q_I_guess'] = 'n-by-2 array of q and the intensity spectrum '\
        'corresponding to the returned scattering equation parameters'

        self.input_type['q'] = opmod.workflow_item
        self.input_type['I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.inputs['fixed_params'] = []
        self.inputs['fixed_param_values'] = []

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        f = self.inputs['flags'] 
        if q is None or I is None or f is None:
            return
        fix_keys = self.inputs['fixed_params']
        fix_vals = self.inputs['fixed_param_values']
        p_fix = {}
        for k,v in zip(fix_keys,fix_vals):
            p_fix[k] = v

        p_new = saxstools.parameterize_spectrum(q,I,f,p_fix)

        I_guess = saxstools.compute_saxs(q,f,p_new)

        q_I_guess = np.array([q,I_guess]).T
        self.outputs['params'] = p_new
        self.outputs['q_I_guess'] = q_I_guess 




