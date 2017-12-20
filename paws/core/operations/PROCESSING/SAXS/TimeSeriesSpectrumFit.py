from collections import OrderedDict
import copy

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools
from saxskit import saxs_fit

inputs = OrderedDict(
    t_qI = None,
    t_populations = None,
    t_params = None,
    t_reports = None,
    fixed_params = None,
    order = 'chronological',
    n_test = 4,
    n_stop = None)
outputs = OrderedDict(
    t_populations = None,
    t_params = None,
    t_reports = None)

class TimeSeriesSpectrumFit(Operation):
    """Fit or re-fit a chronological series of SAXS spectra"""

    def __init__(self):
        super(TimeSeriesSpectrumFit,self).__init__(inputs,outputs)        
        self.input_doc['t_qI'] = 'n-by-2 array, '\
            'column 1 has the time, column 2 has the array of q and I'
        self.input_doc['t_populations'] = 'n-by-2 array, '\
            'column 1 has the time, column 2 has the populations dict'
        self.input_doc['t_params'] = 'n-by-2 array, '\
            'column 1 has the time, column 2 has the parameters dict. '\
            'These parameters are used as the starting condition for the fit. '
        self.input_doc['t_reports'] = 'n-by-2 array, '\
            'column 1 has the time, column 2 has the fit reports dict. '\
            '`t_reports` should correspond to `t_params`. '\
            'If the input `order` is set to "highest_error", '\
            'the reports will be used to determine the order.'
        self.input_doc['fixed_params'] = 'dict indicating which parameters '\
            'to hold fixed during optimization of fit.'
        self.input_doc['order'] = 'choice of processing order, '\
            'either "chronological" or "highest_error".'
        self.input_doc['n_test'] = 'try this many starting parameters'
        self.input_doc['n_stop'] = '(optional) '\
            'stop after this many fits have been performed. '

        self.output_doc['t_populations'] = 'like input `t_populations`, '\
            'but with entries updated for new fits'
        self.output_doc['t_params'] = 'like input `t_params`, '\
            'but with entries updated for new fits'
        self.output_doc['t_reports'] = 'like input `t_reports`, '\
            'but with entries updated for new fits'

    def run(self):
        t_qI = self.inputs['t_qI']
        t_pops = copy.deepcopy(self.inputs['t_populations'])
        t_pars = copy.deepcopy(self.inputs['t_params'])
        t_rpts = copy.deepcopy(self.inputs['t_reports'])
        p_fix = self.inputs['fixed_params']
        odr = self.inputs['order']
        n_stop = self.inputs['n_stop'] 
        n_test = self.inputs['n_test']

        nt = len(t_qI)
        it_order = range(nt)
        if odr == 'highest_error':
            it_order = np.argsort(np.array([t_rpt[1]['objective_value'] 
            if 'objective_value' in t_rpt[1] else 0. for t_rpt in t_rpts]))[::-1]
        if n_stop is not None and n_stop < len(it_order):
            it_order = it_order[:n_stop] 
        n_stop = len(it_order)

        for i_stop,it in zip(range(n_stop),it_order):

            q_I = t_qI[it][1]
            pops = t_pops[it][1]
            pars = t_pars[it][1]
            rpt = t_rpts[it][1]

            if not bool(pops['unidentified']) \
            and not bool(pops['diffraction_peaks']):


                if self.message_callback:
                    msg = 'RUNNING FIT {} / {} '\
                        '\npops: {} '\
                        '\ntime index: {} '\
                        '\ninitial objective: {}'.format(
                        i_stop,n_stop,pops,it,rpt['objective_value'])
                    self.message_callback(msg)


                sxf = saxs_fit.SaxsFitter(q_I,pops)
                # take parameters from the nearest time points
                test_idx = range(max([0,it-n_test]),min(nt,it+n_test+1))
                # compare objectives for all trial parameters
                rpt_best = rpt
                p_best = pars
                for itest in test_idx:
                    test_pops = t_pops[itest][1]
                    if not bool(test_pops['unidentified']) \
                    and not bool(test_pops['diffraction_peaks'])\
                    and test_pops == pops:
                        test_pars = t_pars[itest][1]
                        p_opt,rpt = sxf.fit(test_pars,p_fix,'chi2log')


                        msg = 'trial fit result: {}'.format(rpt['objective_value'])
                        self.message_callback(msg)


                        if rpt['objective_value'] < rpt_best['objective_value']:
                            rpt_best = rpt
                            p_best = p_opt
                    else:
                        self.message_callback('skipping test with pops: {}'.format(test_pops))

                t_pars[it] = (t_pars[it][0],p_best)
                t_rpts[it] = (t_rpts[it][1],rpt_best)

                msg = 'FINISHED FIT. final objective: {}'\
                    .format(rpt_best['objective_value'])
                self.message_callback(msg)


            else:
                if self.message_callback:
                    msg = 'SKIPPING FIT {} / {} '\
                        '\nunidentified: {} '\
                        '\ndiffraction peaks: {}'.format(
                        i_stop,n_stop,
                        pops['unidentified'],
                        pops['diffraction_peaks'])
                    self.message_callback(msg)

        self.outputs['t_populations'] = t_pops
        self.outputs['t_params'] = t_pars
        self.outputs['t_reports'] = t_rpts
