import numpy as np
from scipy import interp

from ...Operation import Operation
from ... import optools

class NPSAXSHeuristics(Operation):
    """
    Use a SAXS spectrum (I(q) vs. q) to 
    guess the mean and standard deviation of particle sizes
    under the assumption of spherical nanoparticles
    with a Gaussian size distribution.
    TODO: document the algorithm here.
    Output the mean and standard deviation of particle radius,
    and the scattered intensity at q=0.

    Assumes the data have already been background subtracted, 
    smoothed, and otherwise cleaned.
    """

    def __init__(self):
        # TODO: deprecate debug_info
        input_names = ['q', 'I', 'dI']
        output_names = ['return_code','results','I_guess','debug_info']
        super(NPSAXSHeuristics, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.input_doc['dI'] = '1d array of error estimates of intensity values (optional- input None to ignore)'
        self.output_doc['return_code'] = str('integer indicating whether or not the spectrum was found to be fittable. '
        + 'Possible values: -1=error, 0=not fittable, 1=fittable')
        self.output_doc['results'] = str('dictionary containing heuristic guesses for '
        + 'the mean size, standard deviation, and the inferred value of I(q=0). '
        + 'Dict keys (strings): "r_mean", "sigma_r", "I_at_0". Units: Angstrom, Angstrom, counts.')
        self.output_doc['debug_info'] = 'dict of information for debugging' 
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['dI'] = optools.ref_type

    def run(self):
        try:
            q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
            # If the maximum intensity is not somewhere up front, throw the flag.
            if not np.argmax(I) in range(10):
                ok_flag = False
            else:
                ok_flag = True
            # Any other ok_flag filters should be added here.
            if not ok_flag: 
                self.outputs['return_code'] = 0
            else:
                # Heuristics: get the first local max
                # and first local minimum of I*q**4 for q>0
                Iqqqq = I*q**4
                idxmax1, idxmin1 = 0,0
                # w is the number of adjacent points to consider 
                # when examining I*q^4 local extrema 
                w = 10
                test_range = iter(range(w,len(q)-w-1))
                # TODO: catch a potential range error below
                while idxmax1 == 0 or idxmin1 == 0:
                    idx = test_range.next()
                    if np.argmax(Iqqqq[idx-w:idx+w]) == w:
                        idxmax1 = idx
                    if np.argmin(Iqqqq[idx-w:idx+w]) == w and not idxmax1 == 0:
                        idxmin1 = idx
                    idx += 1
                # Get the characteristic width of the minimum
                # by locally fitting it to a polynomial.
                # TODO: regularize before fitting
                if not dI:
                    # uniform weights
                    wt = np.ones(shape(qfit))   
                else:
                    # inverse error weights, 1/dI, 
                    # if dI represents Gaussian uncertainty with sigma=dI
                    wt = 1./dI
                qmin1 = q[idxmin1]
                I_at_qmin1 = I[idxmin1]
                pmin1 = np.polyfit(q[idxmin1-w:idxmin1+w],
                        Iqqq[idxmin1-w:idxmin1+w],
                        2,None,False,wt[idxmin1-w:idxmin1+w],False)
                # The curvature is twice the highest-order coefficient
                curvmin1 = 2*pmin1[0]
                # Get a guess for I(q=0) by polynomial fitting,
                # in the region below the first max of I*q^4.
                # TODO: add constraints for slope, curv to be zero at q=0?
                # TODO: if the low-q sampling is poor,
                #       flag return code or add to debug_info
                #if qlim > 0.75 * qFirstDip:
                #    detailed_flags['poor_low_q_sampling'] = True
                #    print "Low-q sampling seems to be poor and will likely affect estimate quality."
                #low_q = (q < qlim)
                p = np.polyfit(q[:idxmax1],I[:idxmax1],2,None,False,wt,False) 
                # I(q=0) is the constant term of the fit
                I_at_0 = p[-1] 
                # Choose heuristics for relating this measurement
                # to known (ideal) diffraction patterns.
                # Heuristics: I_at_0/I(qmin1), curvmin1/qmin1 

                # Reference values for these heuristics
                # have been fit to polynomials in (r0,sigma_r) space
                    

        except ex:
            msg = 'An exception was raised during execution. Error message: {}'.format(ex.message) 
            dbg_info = {'err_msg':msg}
            self.outputs['debug_info'] = dbg_info
            self.outputs['return_code'] = -1



        # more checks
        # is highest value early? is qFirstDip late?
        #if np.argmax(I) > int(0.3 * I.size):
        #    detailed_flags['late_intensity_max'] = True
        #if np.where(q < qFirstDip)[0][-1] < int(0.1 * q.size):
        #    detailed_flags['early_qFirstDip'] = True
        ## are there vaguely zinger-like or dead pixel-like features?
        #curv = (I[2:] - 2 * I[1:-1] + I[:-2])
        #var = (curv ** 2).mean() ** 0.5
        #if (curv < -5 * var).any():
        #    detailed_flags['zinger_like_feature'] = True
        #if (curv > 5 * var).any():
        #    detailed_flags['dead_pixel_like_feature'] = True
        ## vaguely figure-of-merit-like numbers
        #detailed_flags['root_mean_square_diff'] = ((Imodel - I) ** 2).mean() ** 0.5
        #logsafe = ~(np.isnan(I) | (I < 0))
        #detailed_flags['logarithmic_root_mean_square_diff'] = np.e ** (
        #((np.log((Imodel - I)[logsafe])) ** 2).mean() ** 0.5)





