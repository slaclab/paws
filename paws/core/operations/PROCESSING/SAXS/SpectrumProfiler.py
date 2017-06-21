import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ...Operation import Operation
from ... import optools
from . import saxstools

class SpectrumProfiler(Operation):
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
        output_names = ['return_code','precursor_flag','form_flag','structure_flag','metrics']
        super(SpectrumProfiler, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = 'optional- 1d array of intensity uncertainty values I(q)'
        self.output_doc['return_code'] = str('integer indicating '
        + 'whether or not the profiling finished. '
        + 'Possible values: 0=success, 1=error (raised an Exception), '
        + '2=warning (input data has unexpected characteristics).')
        self.output_doc['precursor_flag'] = 'Boolean indicating presence of precursor terms. '
        self.output_doc['form_flag'] = 'Boolean indicating presence of form factor terms. '
        self.output_doc['structure_flag'] = 'Boolean indicating presence of structure factor terms. '
        self.output_doc['metrics'] = str('dict profiling the input spectrum '
        + 'with various numerical measures of the overall spectral profile. '
        + 'Dict keys and descriptions: \n'
        + 'bin_strengths: Integrated intensity in 10 evenly spaced q-bins. \n'
        + 'Imax_over_Imean: maximum intensity divided by mean intensity. \n'
        + 'Imax_over_Ilowq: maximum intensity divided by average intensity over lowest 10% of q domain. \n'
        + 'q_Imax: q value of the maximum intensity. \n'
        + 'q_corr: Pearson correlation between I(q) and q. \n'
        + 'qsquared_corr: Pearson correlation between I(q) and q^2. \n'
        + 'cos2q_corr: Pearson correlation between I(q) and (cos(q))^2. \n'
        + 'cosq_corr: Pearson correlation between I(q) and cos(q). \n'
        + 'invq_corr: Pearson correlation between I(q) and 1/q. \n'
        + 'q_logcorr: Same as q_corr, but with log(I(q)). \n'
        + 'qsquared_logcorr: Same as qsquared_corr, but with log(I(q)). \n'
        + 'cos2q_logcorr: Same as cos2q_corr, but with log(I(q)). \n'
        + 'cosq_logcorr: Same as cosq_corr, but with log(I(q)). \n'
        + 'invq_logcorr: Same as invq_corr, but with log(I(q)).')
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
	    ###check correlations of input vs. some known trends...
        n_q = len(q)
	    # correlations on intensity
        q_corr = saxstools.compute_pearson(I,np.linspace(0,1,n_q))
        qsquared_corr = saxstools.compute_pearson(I,np.linspace(0,1,n_q)**2)
        cosq_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1])))
        cos2q_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1]))**2)
        invq_corr = saxstools.compute_pearson(I,q**-1)
        # correlations on log intensity
        idx_nz = np.invert(I == 0)
        q_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , np.linspace(0,1,n_q)[idx_nz] )
        qsquared_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , (np.linspace(0,1,n_q)[idx_nz])**2 )
        cosq_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , np.cos(q*np.pi/(2*q[-1]))[idx_nz] )
        cos2q_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , (np.cos(q*np.pi/(2*q[-1]))[idx_nz])**2 )
        invq_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , q[idx_nz]**-1 )
        #invq4_corr = saxstools.compute_pearson(I,q**-4)
        #I0 = I[np.min(np.argwhere(I>0))]
        idxmax = np.argmax(I)
        Imax = I[idxmax] 
        q_Imax = q[idxmax]
        Imean = np.mean(I)
        Imax_over_Imean = float(Imax)/float(Imean)
        ###compute bin-integrated spectral intensities.
        ### TODO: use these somehow
        qmin, qmax = q[0], q[-1]
        qrange = qmax-qmin
        bin_strengths = np.zeros(10)
        for i in range(10):
            qmini, qmaxi = qmin+i*qrange/10,qmin+(i+1)*qrange/10
            idxi = list((q>=qmini) & (q<qmaxi))
            idxi_shift = [False]+idxi[:-1]
            dqi = q[ idxi ] - q[ idxi_shift ]
            Ii = I[ idxi ]
            bin_strengths[i] = np.sum(Ii * dqi) / (qmaxi-qmini)
        Imax_over_Ilowq = float(Imax)/bin_strengths[0]
        # Flagging form factor: These tend to correlate with 1/q
        form_flag = invq_logcorr > 0.7 or invq_corr > 0.3 
        # Flagging precursors: Only flag if there is also a form term.
        # (Assume fitting precursors alone is boring).
        precursor_flag = form_flag and ( any([cosq_corr > 0.6, cos2q_corr > 0.6])
                        or all([cosq_logcorr>0.4,cos2q_logcorr>0.4,cosq_corr>0.5,cos2q_corr>0.5]) )
        # Flagging structure: look for large values away from q=0.
        # TODO: more detailed structure factor evaluation. 
        structure_flag = Imax_over_Ilowq > 1.2 and Imax_over_Imean > 4 and q_Imax > 0.05
        #######
        # Any good/bad filters should be added here.
        ok_flag = True
        flag_msg = ''
        if q_corr > 0.2:
            ok_flag = False
            flag_msg = str('This algorithm expects spectra that tend to decrease in q. '
            + 'The input spectrum seems to be overall increasing in q.')
        #if (...) 
        #    ok_flag = False
        #    flag_msg = 'This spectrum seems mostly flat.'
        #elif (...):
        #    ok_flag = False
        #    flag_msg = ''
        #######
        d_r = {}
        d_r.update({'bin_strengths':bin_strengths})
        d_r.update({'Imax_over_Imean':Imax_over_Imean})
        d_r.update({'Imax_over_Ilowq':Imax_over_Ilowq})
        d_r.update({'q_Imax':q_Imax})
        d_r.update({'q_logcorr':q_logcorr})
        d_r.update({'qsquared_logcorr':qsquared_logcorr})
        d_r.update({'cos2q_logcorr':cos2q_logcorr})
        d_r.update({'cosq_logcorr':cosq_logcorr})
        d_r.update({'invq_logcorr':invq_logcorr})
        d_r.update({'q_corr':q_corr})
        d_r.update({'qsquared_corr':qsquared_corr})
        d_r.update({'cos2q_corr':cos2q_corr})
        d_r.update({'cosq_corr':cosq_corr})
        d_r.update({'invq_corr':invq_corr})
        self.outputs['metrics'] = d_r 
        if not ok_flag:
            d_r['WARNING_MESSAGE'] = flag_msg
            self.outputs['precursor_flag'] = False 
            self.outputs['form_flag'] = False 
            self.outputs['structure_flag'] = False
            self.outputs['return_code'] = 1
        else:
            self.outputs['precursor_flag'] = precursor_flag
            self.outputs['form_flag'] = form_flag
            self.outputs['structure_flag'] = structure_flag
            self.outputs['return_code'] = 0

        #low_q_idxs = (q < q[0]+0.1*(q[-1]-q[0]))
        #high_q_idxs = (q > q[0]+0.9*(q[-1]-q[0]))
        #n_low_q = np.sum(np.array(low_q_idxs))
        #n_high_q = np.sum(np.array(high_q_idxs))
        # If the max intensity is outside the low-q region, throw flag
        #if not np.argmax(I) in range(2*n_low_q):
        #    ok_flag = False
        #    flag_msg = str('The maximum intensity '
        #    + '({} at q={}) '.format(np.max(I),q[np.argmax(I)])
        #    + 'is outside the lower 20% of the q-range '
        #    + '({} to {}).'.format(q[0],q[2*n_low_q]))
        # If there is a huge maximum somewhere, throw flag
        #elif np.max(I) > 10*np.mean(I[:2*n_low_q]):
        #    ok_flag = False
        #    flag_msg = str('The maximum intensity '
        #    + '({} at q={}) '.format(np.max(I),q[np.argmax(I)])
        #    + 'is greater than 10x the mean intensity '
        #    + 'of the lower 20% of the q-range '
        #    + '({} from {} to {}).'
        #    .format(np.mean(I[low_q_idxs]),q[0],q[n_low_q]))
        # If high-q intensity not significantly smaller than low-q, throw flag
        #elif not np.sum(I[:n_low_q]) > 10*np.sum(I[-1*n_high_q:]):
        #    ok_flag = False
        #    flag_msg = str('The lower 10% of the q-range '
        #    + '({} to {}) '.format(q[0],q[n_low_q])
        #    + 'has less than 10 times the intensity '
        #    + 'of the upper 10% of the q-range '
        #    + '({} to {}).'.format(q[-1*n_high_q],q[-1]))


