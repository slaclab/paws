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
        input_names = ['q', 'I']
        output_names = ['return_code','results']
        super(SAXSProfile, self).__init__(input_names, output_names)
        
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.output_doc['return_code'] = str('integer indicating '
        + 'whether or not the heuristics finished. '
        + 'Possible values: 0=success, 1=error (raised an Exception), '
        + '2=warning (input data has unfamiliar characteristics).')
        self.output_doc['results'] = str('dict profiling the input spectrum. '
        + 'Includes correlations between the spectrum and various trends, '
        + 'and fractional strengths of the species thought to be present. '
        + 'Correlations are between -1 and 1. '
        + 'Strengths are between 0 and 1, and should sum to 1. '
        + 'Dict keys (strings): "linear_corr", "cosine_corr", "invq_corr", '
        + '"precursor_strength", "spherical_np_strength", "diffraction_strength".')
       
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0
        self.outputs['return_code'] = 1
        # d_r = dict of results
        d_r = {}
        ###check correlations of input vs. some known trends...
        n_q = len(q)
        lin_corr = saxstools.compute_pearson(I,np.linspace(0,1,n_q))
        cos_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1])))
        invq_corr = saxstools.compute_pearson(I,q**-1)
        precursor_flag = (cos_corr > 0.6 or cos_corr > 0.9*invq_corr)
        spherical_np_flag = (invq_corr > 0.9 or invq_corr > cos_corr)
        diffraction_flag = False
        d_r.update({'linear_corr':lin_corr})
        d_r.update({'cos_corr':cos_corr})
        d_r.update({'invq_corr':invq_corr})
        ok_flag = True
        if climb_corr > 0.2:
            ok_flag = False
            flag_msg = str('Spectrum is excessively flat or increasing in q.')
        elif not any([precursor_flag,spherical_np_flag,diffraction_flag]):
            ok_flag = False
            flag_msg = str('Spectrum has unfamiliar characteristics.')
        #######
        # Any other up-front filters should be added here.
        #######
        if not ok_flag: 
            self.outputs['return_code'] = 2
            d_r.update({'message':flag_msg})
            self.outputs['results'] = d_r
        else:
            precursor_strength = 0
            spherical_np_strength = 0
            diffraction_strength = 0
            if precursor_flag:
                pre_str = np.min([0,2*(cos_corr-0.5)])
            if spherical_np_flag:
                sph_str = np.min([0,invq_corr])
            if diffraction_flag:
                diff_str = 1                  
            total_strength = pre_str + sph_str + diff_str
            d_r.update({'precursor_strength':pre_str/total_strength})
            d_r.update({'spherical_np_strength':sph_str/total_strength})
            d_r.update({'diffraction_strength':diff_str/total_strength})
            self.outputs['results'] = d_r 
            self.outputs['return_code'] = 0

