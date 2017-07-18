import numpy as np
from collections import OrderedDict

from ... import Operation as op
from ...Operation import Operation
from ....tools import saxstools

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
        output_names = ['features']
        super(SpectrumProfiler, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = 'optional- 1d array of intensity uncertainty values I(q)'
        self.output_doc['features'] = str('dict profiling the input spectrum. '
        + 'Dict keys and descriptions: \n'
        + 'ERROR_MESSAGE: Any errors or warnings are reported here. \n'
        + 'bad_data_flag: Boolean indicating that the spectrum is unfamiliar or mostly made of noise. \n'
        + 'precursor_flag: Boolean indicating presence of precursor terms. \n'
        + 'form_flag: Boolean indicating presence of form factor terms. \n'
        + 'form_id: Form factor identity, e.g. sphere, cube, rod, etc. \n'
        + 'structure_flag: Boolean indicating presence of structure factor terms. \n'
        + 'structure_id: Structure identity, e.g. fcc, hcp, bcc, etc. \n'
        + 'low_q_ratio: fraction of integrated intensity for q<0.4 '
        + 'high_q_ratio: fraction of integrated intensity for q>0.4 '
        + 'low_q_logratio: fraction of total log(I)-min(log(I)) over q<0.4 '
        + 'high_q_logratio: fraction of total log(I)-min(log(I)) over q>0.4 '
        + 'high_freq_ratio: Ratio of the upper half to the lower half '
        + 'of the power spectrum of the discrete fourier transform of the intensity. \n'
        + 'fluctuation_strength: Integrated fluctuation of intensity '
        + '(sum of difference in intensity between adjacent points '
        + 'taken only where this difference changes sign), '
        + 'divided by the range (maximum minus minimum) of intensity. \n'
        + 'Imax_over_Imean: maximum intensity divided by mean intensity. \n'
        + 'Imax_over_Imean_local: maximum intensity divided by '
        + 'mean intensity over q values within 10% of the q value of the maximum. \n'
        + 'Imax_over_Ilowq: Maximum intensity divided by mean intensity over q<0.1. \n'
        + 'Imax_over_Ihighq: Maximum intensity divided by mean intensity over q>0.4. \n'
        + 'Ilowq_over_Ihighq: Mean intensity for q<0.1 divided by mean intensity for q>0.4. \n'
        + 'low_q_logcurv: Curvature of parabola fit to log(I) versus log(q) for q<0.1. \n'
        + 'q_Imax: q value of the maximum intensity. ')
        #+ 'bin_strengths: (not implemented). \n'
        #+ 'q_corr: Pearson correlation between I(q) and q. \n'
        #+ 'qsquared_corr: Pearson correlation between I(q) and q^2. \n'
        #+ 'cos2q_corr: Pearson correlation between I(q) and (cos(q))^2. \n'
        #+ 'cosq_corr: Pearson correlation between I(q) and cos(q). \n'
        #+ 'invq_corr: Pearson correlation between I(q) and 1/q. \n'
        #+ 'q_logcorr: Same as q_corr, but with log(I(q)). \n'
        #+ 'qsquared_logcorr: Same as qsquared_corr, but with log(I(q)). \n'
        #+ 'cos2q_logcorr: Same as cos2q_corr, but with log(I(q)). \n'
        #+ 'cosq_logcorr: Same as cosq_corr, but with log(I(q)). \n'
        #+ 'invq_logcorr: Same as invq_corr, but with log(I(q)).')
        self.input_src['q'] = op.wf_input
        self.input_src['I'] = op.wf_input
        self.input_src['dI'] = op.no_input
        self.input_type['q'] = op.ref_type
        self.input_type['I'] = op.ref_type

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        dI = self.inputs['dI']
        # Set return code to 1 (error) by default;
        # if execution finishes, set it to 0

        ### amplitude analysis:
        idxmax = np.argmax(I)
        Imax = I[idxmax] 
        q_Imax = q[idxmax]
        idxmin = np.argmin(I)
        Imin = I[idxmin]
        Irange = Imax - Imin
        Imean = np.mean(I)
        Imax_over_Imean = float(Imax)/float(Imean)
        idx_around_max = ((q > 0.9*q_Imax) & (q < 1.1*q_Imax))
        Imean_around_max = np.mean(I[idx_around_max])
        Imax_over_Imean_local = Imax / Imean_around_max

        ### fourier analysis
        n_q = len(q)
        fftI = np.fft.fft(I)
        ampI = np.abs(fftI)
        powI = np.abs(fftI)**2
        high_freq_ratio = np.sum(powI[n_q/4:n_q/2])/np.sum(powI[1:n_q/4])
        #high_freq_ratio = np.sum(ampI[n_q/4:n_q/2])/np.sum(ampI[1:n_q/4])

        ### fluctuation analysis
        # array of the difference between neighboring points:
        nn_diff = I[1:]-I[:-1]
        # keep indices where the sign of this difference changes.
        # also keep first index
        nn_diff_prod = nn_diff[1:]*nn_diff[:-1]
        idx_keep = np.hstack((np.array([True]),nn_diff_prod<0))
        fluc = np.sum(np.abs(nn_diff[idx_keep]))
        #fluctuation_strength = fluc/Irange
        fluctuation_strength = fluc/Imean

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
        #qmin, qmax = q[0], q[-1]
        #qrange = qmax-qmin
        #bin_strengths = np.zeros(10)
        #for i in range(10):
        #    qmini, qmaxi = qmin+i*qrange/10,qmin+(i+1)*qrange/10
        #    idxi = list((q>=qmini) & (q<qmaxi))
        #    idxi_shift = [False]+idxi[:-1]
        #    idxi = np.array(idxi,dtype=bool)
        #    idxi_shift = np.array(idxi_shift,dtype=bool)
        #    dqi = q[ idxi_shift ] - q[ idxi ]
        #    Ii = I[ idxi ]
        #    bin_strengths[i] = np.sum(Ii * dqi) / (qmaxi-qmini)
        idx_nz = np.invert((I==0))
        q_nz = q[idx_nz] 
        I_nz_log = np.log(I[idx_nz])
        # make values positive:
        I_nz_log = I_nz_log-np.min(I_nz_log)
        I_logsum = np.sum(I_nz_log)
        low_q_logratio = np.sum(I_nz_log[(q_nz<0.4)])/I_logsum
        high_q_logratio = np.sum(I_nz_log[(q_nz>=0.4)])/I_logsum
        I_sum = np.sum(I)
        low_q_ratio = np.sum(I[(q<0.4)])/I_sum
        high_q_ratio = np.sum(I[(q>=0.4)])/I_sum

        ### curve shape analysis
        lowq_idx = q<0.1
        highq_idx = q>0.4
        lowq = q[lowq_idx]
        highq = q[highq_idx]
        I_lowq = I[lowq_idx]
        I_highq = I[highq_idx]
        I_lowq_mean = np.mean(I_lowq)
        I_highq_mean = np.mean(I_highq)
        lowq_mean = np.mean(lowq)
        lowq_std = np.std(lowq)
        I_lowq_std = np.std(I_lowq)
        I_lowq_s = I_lowq/I_lowq_std
        lowq_s = (lowq - lowq_mean)/lowq_std
        #p_lowq = saxstools.fit_with_slope_constraint(lowq_s,np.log(I_lowq_s),-1*lowq_mean/lowq_std,0,3) 
        #p_lowq = saxstools.fit_with_slope_constraint(lowq_s,np.log(I_lowq_s),lowq_s[-1],0,3) 
        p_lowq = np.polyfit(lowq_s,np.log(I_lowq_s),2)
        low_q_logcurv = p_lowq[0]
        Imax_over_Ilowq = float(Imax)/I_lowq_mean
        Imax_over_Ihighq = float(Imax)/I_highq_mean
        Ilowq_over_Ihighq = I_lowq_mean/I_highq_mean

        # Flagging bad data: 
        # Data with high noise are bad.
        # Data that are totally flat or increasing in q are bad.
        # Data that do not have downward curvature at low q are often bad, but not always.
        bad_data_flag = ( fluctuation_strength > 20 
                        or low_q_ratio/high_q_ratio < 1
                        or Ilowq_over_Ihighq < 10 )
                        #or (low_q_logcurv > 0 and Ilowq_over_Ihighq < 10))

        form_id = None 
        structure_id = None 
        if bad_data_flag:
            form_flag = False
            precursor_flag = False
            structure_flag = False
        else:
            # Flagging form factor:
            # Intensity should be quite decreasing in q.
            # Low-q region should be quite flat.
            # Low-q mean intensity should be much larger than low-q fluctuations.
            form_flag = low_q_ratio/high_q_ratio > 10 
            if form_flag:
                # TODO: determine form factor here
                form_id = 'sphere'
 
            # Flagging precursors: 
            # Intensity should decrease in q, at least mildly.
            # Intensity should decrease more sharply at high q.
            # Low-q region of spectrum should be quite flat.
            # Noise levels may be high if only precursors are present.
            # More high-q intensity than form factor alone.
            precursor_flag = low_q_ratio/high_q_ratio > 2 and high_q_ratio > 1E-3 

            # Flagging structure:
            # Structure is present if max intensity occurs outside the low-q region. 
            # Maximum intensity should be large relative to its 'local' mean intensity. 
            structure_flag = Imax_over_Imean_local > 2 
            if structure_flag:
                # TODO: determine structure factor here
                structure_id = 'fcc'
        d_r = OrderedDict() 
        #d_r['bin_strengths'] = bin_strengths
        #d_r['bin_strengths'] = None 
        d_r['bad_data_flag'] = bad_data_flag
        d_r['precursor_flag'] = precursor_flag
        d_r['form_flag'] = form_flag
        d_r['structure_flag'] = structure_flag
        d_r['structure_id'] = structure_id 
        d_r['form_id'] = form_id 
        d_r['low_q_logcurv'] = low_q_logcurv
        d_r['Imax_over_Imean'] = Imax_over_Imean
        d_r['Imax_over_Imean_local'] = Imax_over_Imean_local
        d_r['Imax_over_Ilowq'] = Imax_over_Ilowq 
        d_r['Imax_over_Ihighq'] = Imax_over_Ihighq 
        d_r['Ilowq_over_Ihighq'] = Ilowq_over_Ihighq 
        d_r['low_q_logratio'] = low_q_logratio 
        d_r['high_q_logratio'] = high_q_logratio 
        d_r['low_q_ratio'] = low_q_ratio 
        d_r['high_q_ratio'] = high_q_ratio 
        d_r['high_freq_ratio'] = high_freq_ratio 
        d_r['fluctuation_strength'] = fluctuation_strength
        d_r['q_Imax'] = q_Imax
        #d_r['q_logcorr'] = q_logcorr
        #d_r['qsquared_logcorr'] = qsquared_logcorr
        #d_r['cos2q_logcorr'] = cos2q_logcorr
        #d_r['cosq_logcorr'] = cosq_logcorr
        #d_r['invq_logcorr'] = invq_logcorr
        #d_r['q_corr'] = q_corr
        #d_r['qsquared_corr'] = qsquared_corr
        #d_r['cos2q_corr'] = cos2q_corr
        #d_r['cosq_corr'] = cosq_corr
        #d_r['invq_corr'] = invq_corr
        self.outputs['features'] = d_r 

