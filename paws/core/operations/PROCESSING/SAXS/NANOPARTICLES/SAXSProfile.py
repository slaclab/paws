import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ....Operation import Operation
from .... import optools
from .. import saxstools

class SAXSProfile(Operation):
    """
    This operation profiles a SAXS spectrum (I(q) vs. q)
    to determine some characteristics of the sample.
    Based on some measures of the overall shape of the spectrum,
    the spectrum is tested for scattering from precursors 
    (approximated as small dilute monodisperse spheres),
    scattering from spherical nanoparticles 
    (dilute spheres with a normal size distribution),
    diffraction peaks
    (Voigt-like profiles due to crystalline arrangements),
    or some combination of the three.
    TODO: document algorithm here.

    Output a return code
    and a dictionary of the results.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q', 'I', 'dI']
        output_names = ['return_code','results']
        super(SAXSProfile, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = 'optional- 1d array of intensity uncertainty values I(q)'
        self.output_doc['return_code'] = str('integer indicating '
        + 'whether or not the profiling finished. '
        + 'Possible values: 0=success, 1=error (raised an Exception), '
        + '2=warning (input data has unexpected characteristics).')
        self.output_doc['results'] = str('dict profiling the input spectrum. '
        + 'Includes various numerical measures of the overall spectral profile. '
        + 'Dict keys and descriptions: '
        + 'linear_pearson: Pearson correlation between input spectrum and a linear profile. '
        + 'cosine_pearson: Pearson correlation between input spectrum and a quarter-cycle cosine. '
        + 'invq_pearson: Pearson correlaton between input spectrum and an inverse (1/q) profile. '
        + 'Imax_over_Imean: Ratio of maximum intensity to full-spectrum mean intensity. '
        + 'bin_strengths: Fractions of the intensity in 10 equally spaced bins over the q range.')
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.no_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        dI = self.inputs['dI']
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        d_r = {}
        ###check correlations of input vs. some known trends...
        n_q = len(q)
        lin_corr = saxstools.compute_pearson(I,np.linspace(0,1,n_q))
        cos_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1])))
        invq_corr = saxstools.compute_pearson(I,q**-1)
        Imax_over_Imean = np.max(I)/np.mean(I)
        qmin, qmax = q[0], q[-1]
        qrange = qmax-qmin
        bin_strengths = np.zeros(10)
        for i in range(10):
            qmini, qmaxi = qmin+i*qrange/10,qmin+(i+1)*qrange/10
            idxi = [q>=qmini & q<qmaxi]
            idxi_shift = [0]+idxi[:-1]
            dqi = q[ idxi ] - q[ idxi_shift ]
            Ii = I[ idxi ]
            bin_strengths[i] = np.sum(Ii * dqi)
        d_r.update({'linear_corr':lin_corr})
        d_r.update({'cos_corr':cos_corr})
        d_r.update({'invq_corr':invq_corr})
        d_r.update({'Imax_over_Imean':Imax_over_Imean})
        d_r.update({'bin_strengths':bin_strengths})
        self.outputs['results'] = d_r 
        self.outputs['return_code'] = 0

