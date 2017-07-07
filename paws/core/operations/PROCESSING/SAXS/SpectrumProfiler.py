import numpy as np
from collections import OrderedDict

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
    scattering from dilute nanoparticles of various form factors 
    (currently only spheres),
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
        output_names = ['return_code','features']
        super(SpectrumProfiler, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = 'optional- 1d array of intensity uncertainty values I(q)'
        self.output_doc['return_code'] = str('integer indicating '
        + 'whether or not the profiling finished. '
        + 'Possible values: 0=success, 1=error (raised an Exception), '
        + '2=warning (input data has unexpected characteristics).')
        self.output_doc['features'] = str('dict profiling the input spectrum. '
        + 'Dict keys and descriptions: \n'
        + 'WARNING_MESSAGE: warning message, only added if return_code==2. \n'
        + 'bad_data_flag: Boolean indicating that the spectrum is unfamiliar or mostly made of noise. \n'
        + 'precursor_flag: Boolean indicating presence of precursor terms. \n'
        + 'form_flag: Boolean indicating presence of form factor terms. \n'
        + 'structure_flag: Boolean indicating presence of structure factor terms. \n'
        + 'structure_id: Structure identity, e.g. fcc, hcp, bcc, etc. \n'
        + 'form_id: Form factor identity, e.g. sphere, cube, rod, etc. \n'
        + 'high_freq_ratio: Ratio of the upper half to the lower half '
        + 'of the power spectrum of the discrete fourier transform of the intensity. \n'
        + 'fluctuations_over_mean: Integrated fluctuation of intensity '
        + '(sum of absolute value of differences between adjacent points) '
        + 'divided by the mean intensity. \n'
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

        ### amplitude analysis:
        idxmax = np.argmax(I)
        Imax = I[idxmax] 
        q_Imax = q[idxmax]
        Imean = np.mean(I)

        ### fourier analysis
        n_q = len(q)
        fftI = np.fft.fft(I)
        ampI = np.abs(fftI)
        powI = np.abs(fftI)**2
        high_freq_ratio = np.sum(powI[n_q/4:n_q/2])/np.sum(powI[1:n_q/4])
        #high_freq_ratio = np.sum(ampI[n_q/4:n_q/2])/np.sum(ampI[1:n_q/4])

        ### fluctuation analysis
        fluc = np.sum(np.abs(I[1:]-I[:-1]))
        fluctuations_over_mean = fluc/Imean 

	    # correlations on intensity
        q_corr = saxstools.compute_pearson(I,np.linspace(0,1,n_q))
        qsquared_corr = saxstools.compute_pearson(I,np.linspace(0,1,n_q)**2)
        cosq_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1])))
        cos2q_corr = saxstools.compute_pearson(I,np.cos(q*np.pi/(2*q[-1]))**2)
        invq_corr = saxstools.compute_pearson(I,q**-1)
        #invq4_corr = saxstools.compute_pearson(I,q**-4)

        # correlations on log intensity
        idx_nz = np.invert(I <= 0)
        q_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , np.linspace(0,1,n_q)[idx_nz] )
        qsquared_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , (np.linspace(0,1,n_q)[idx_nz])**2 )
        cosq_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , np.cos(q*np.pi/(2*q[-1]))[idx_nz] )
        cos2q_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , (np.cos(q*np.pi/(2*q[-1]))[idx_nz])**2 )
        invq_logcorr = saxstools.compute_pearson( np.log(I[idx_nz]) , q[idx_nz]**-1 )

        ### bin-integrated intensity analysis
        # TODO: standardize these bins in q space
        qmin, qmax = q[0], q[-1]
        qrange = qmax-qmin
        bin_strengths = np.zeros(10)
        for i in range(10):
            qmini, qmaxi = qmin+i*qrange/10,qmin+(i+1)*qrange/10
            idxi = list((q>=qmini) & (q<qmaxi))
            idxi_shift = [False]+idxi[:-1]
            idxi = np.array(idxi,dtype=bool)
            idxi_shift = np.array(idxi_shift,dtype=bool)
            dqi = q[ idxi_shift ] - q[ idxi ]
            Ii = I[ idxi ]
            bin_strengths[i] = np.sum(Ii * dqi) / (qmaxi-qmini)
        low_q_dominance = np.sum(bin_strengths[:5])/np.sum(bin_strengths[5:10]) 

        # Flagging bad data: 
        # Bad data have high noise
        # (high fluctuations relative to the mean)
        # or may be increasing-ish in q
        bad_data_flag = (fluctuations_over_mean > 30 
                        or q_corr > 0.2
                        or low_q_dominance < 2)
        Imax_over_Ilowq = float(Imax)/bin_strengths[0]
        Imax_over_Imean = float(Imax)/float(Imean)
        form_id = None 
        structure_id = None 
        if bad_data_flag:
            form_flag = False
            precursor_flag = False
            structure_flag = False
        else:
            # Flagging form factor: These tend to (log-)correlate with 1/q.
            # Spectra with relatively small form factor contribution 
            # tend to linear-correlate strongly with 1/q
            form_flag = ((invq_logcorr > 0.7 or invq_corr > 0.95) 
                        and low_q_dominance > 5 
                        and bin_strengths[0] / bin_strengths[-1] > 100)
            #and not all([cosq_corr > 0.7,cosq_logcorr > 0.7, cos2q_logcorr > 0.7, cos2q_corr>0.7]))
            if form_flag:
                # TODO: determine form factor here
                form_id = 'sphere'
 
            # Flagging precursors: 
            # Bin strengths should be decreasing, but not wildly  
            precursor_flag = low_q_dominance > 2 and low_q_dominance < 1000 

            # Flagging structure:
            # Largest bin is likely not lowest-q bin 
            structure_flag = Imax_over_Ilowq > 1.2 and q_Imax > 0.05 #and Imax_over_Imean > 4 
            # or (not np.argmax(bin_strengths) == 0))
            if structure_flag:
                # TODO: determine structure factor here
                structure_id = 'fcc'
        #######
        # More good/bad filters could be added here.
        #flag_msg = ''
        #if q_corr > 0.2:
        #    ok_flag = False
        #flag_msg = str('This algorithm expects spectra that tend to decrease in q. '
        #+ 'The input spectrum seems to be overall increasing in q.')
        #if (...) 
        #    ok_flag = False
        #    flag_msg = 'This spectrum seems mostly flat.'
        #elif (...):
        #    ok_flag = False
        #    flag_msg = ''
        #######
        ok_flag = True
        d_r = OrderedDict() 
        if not ok_flag:
            d_r['WARNING_MESSAGE'] = flag_msg
            self.outputs['return_code'] = 1
        else:
            d_r['bin_strengths'] = bin_strengths
            d_r['Imax_over_Imean'] = Imax_over_Imean
            d_r['Imax_over_Ilowq'] = Imax_over_Ilowq
            d_r['low_q_dominance'] = low_q_dominance 
            d_r['high_freq_ratio'] = high_freq_ratio 
            d_r['fluctuations_over_mean'] = fluctuations_over_mean 
            d_r['q_Imax'] = q_Imax
            d_r['q_logcorr'] = q_logcorr
            d_r['qsquared_logcorr'] = qsquared_logcorr
            d_r['cos2q_logcorr'] = cos2q_logcorr
            d_r['cosq_logcorr'] = cosq_logcorr
            d_r['invq_logcorr'] = invq_logcorr
            d_r['q_corr'] = q_corr
            d_r['qsquared_corr'] = qsquared_corr
            d_r['cos2q_corr'] = cos2q_corr
            d_r['cosq_corr'] = cosq_corr
            d_r['invq_corr'] = invq_corr
            d_r['bad_data_flag'] = bad_data_flag
            d_r['precursor_flag'] = precursor_flag
            d_r['form_flag'] = form_flag
            d_r['structure_flag'] = structure_flag
            d_r['structure_id'] = structure_id 
            d_r['form_id'] = form_id 
        self.outputs['return_code'] = 0
        self.outputs['features'] = d_r 

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


