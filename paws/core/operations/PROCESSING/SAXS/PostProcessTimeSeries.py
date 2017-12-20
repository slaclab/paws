from collections import OrderedDict
import copy

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools
from saxskit import saxs_fit

inputs = OrderedDict(batch_outputs=None,time_key=None,
                    q_I_key=None,q_I_opt_key=None,flags_key=None,
                    params_key=None,reports_key=None)
outputs = OrderedDict(new_outputs=None)

class PostProcessTimeSeries(Operation):
    """Re-fit a set of SAXS spectra chronologically, to refine results."""

    def __init__(self):
        super(PostProcessTimeSeries,self).__init__(inputs,outputs)        
        self.input_doc['batch_outputs'] = 'list of dicts '\
            'of workflow outputs, produced by a batch execution'
        self.input_doc['time_key'] = 'dict key for time stamp in batch_outputs'
        self.input_doc['q_I_key'] = 'dict key for '\
            'measured spectrum data from batch_outputs'
        self.input_doc['q_I_opt_key'] = 'dict key for '\
            'optimized fit to measured spectrum from batch_outputs'
        self.input_doc['flags_key'] = 'dict key for '\
            'population flags from batch_outputs'
        self.input_doc['params_key'] = 'dict key for '\
            'SAXS equation parameters from batch_outputs' 
        self.input_doc['reports_key'] = 'dict key for '\
            'SAXS fitting report from batch_outputs' 
        self.output_doc['new_outputs'] = 'list of dicts '\
            'containing time stamps and newly refined parameters'

    def run(self):
        b_out = copy.deepcopy(self.inputs['batch_outputs'])
        t = np.array([b[self.inputs['time_key']] for b in b_out])
        i_xsort = np.argsort(t)
        t = t[i_xsort]
        b_out = [b_out[i] for i in i_xsort]
        q_I = np.array([b[self.inputs['q_I_key']] for b in b_out])
        f = np.array([b[self.inputs['flags_key']] for b in b_out])
        p = np.array([b[self.inputs['params_key']] for b in b_out])
        r = np.array([b[self.inputs['reports_key']] for b in b_out])

        n_batch = len(b_out)
        idx_batch = np.arange(0,n_batch)

        empty_outputs = [None for ib in idx_batch] 
        self.outputs['new_outputs'] = empty_outputs 
        if self.data_callback: 
            self.data_callback('outputs.new_outputs',empty_outputs)

        for idx,d in zip(idx_batch,b_out):
            p_i = copy.deepcopy(p[idx])
            rpt_i = copy.deepcopy(r[idx])
            out_dict = b_out[idx] 
            if not f[idx]['bad_data'] and not f[idx]['diffraction_peaks']:
                test_idx = []
                if not idx==0:
                    if not f[idx-1]['bad_data'] and not f[idx-1]['diffraction_peaks']:
                        test_idx.append(idx-1)
                if not idx == n_batch-1:
                    if not f[idx+1]['bad_data'] and not f[idx+1]['diffraction_peaks']:
                        test_idx.append(idx+1)
                for idxt in test_idx:
                    p_test = copy.deepcopy(p_i)
                    for k in p_test.keys():
                        if k in p[idxt].keys():
                            p_test[k] = p[idxt][k]
                    #if rpt_i['objective'] in ['chi2log_fixI0']:
                    I0_i = saxs_fit.compute_saxs(np.array([0.]),f[idx],p_i) 
                    I0_test = saxs_fit.compute_saxs(np.array([0.]),f[idx],p_test) 
                    I0_ratio = I0_i[0] / I0_test[0]
                    for Ikey in ['G_precursor','I0_sphere','I0_floor']:
                        if Ikey in p_test.keys():
                            p_test[Ikey] = p_test[Ikey] * I0_ratio
                    print('testing params: \n{}'.format(p_test))
                    #p_opt_test,rpt_test = saxs_fit.fit_spectrum(q_I[idx],f[idx],p_test,rpt_i['fixed_params'],rpt_i['objective']) 
                    p_opt_test,rpt_test = saxs_fit.fit_spectrum(q_I[idx],f[idx],p_test,[],'chi2log') 
                    if rpt_test['objective_after'] < rpt_i['objective_after']:
                        print('*** {}: objective improved ***'.format(__name__))
                        print('*** old: {} ***'.format(rpt_i['objective_after']))
                        print('*** new: {} ***'.format(rpt_test['objective_after']))
                        p_i = p_opt_test
                        rpt_i = rpt_test

                        #from matplotlib import pyplot as plt
                        #I_old = saxs_fit.compute_saxs(q,f[idx],p[idx])
                        #I0_old = saxs_fit.compute_saxs(np.array([0.]),f[idx],p[idx])
                        #I0_new = saxs_fit.compute_saxs(np.array([0.]),f[idx],p_i)
                        #plt.plot(q,q_I[idx][:,1])
                        #plt.plot(q,I_old,'r')
                        #plt.plot(q,I_new,'g')
                        #print('I(q=0) \nbefore: {} \nafter: {}'.format(I0_old,I0_new))
                        #plt.show()

            #out_dict[self.inputs['time_key']] = t[idx]
            out_dict[self.inputs['params_key']] = p_i
            out_dict[self.inputs['reports_key']] = rpt_i
            #out_dict[self.inputs['flags_key']] = f[idx] 
            #out_dict[self.inputs['q_I_key']] = q_I[idx] 
            q = q_I[idx][:,0] 
            I_new = saxs_fit.compute_saxs(q,f[idx],p_i)
            out_dict[self.inputs['q_I_opt_key']] = np.array([q,I_new]).T 
            self.outputs['new_outputs'][idx] = out_dict
            if self.data_callback: 
                self.data_callback('outputs.new_outputs.'+str(idx),copy.deepcopy(out_dict))

            # an alternate approach using statistics of several nearby points...
            #p_i = copy.deepcopy(p[idx])
            ## Collect params for several of the nearest points
            #idx_use = (abs(idx_batch-idx) < 4) & idx_batch != idx
            #p_stats = dict.fromkeys(p_i.keys())
            #for k in p_i.keys():
            #    p_stats[k] = []
            ## Collect params of any nearby, relevant samples 
            #for p_j in p[idx_use]:
            #    if k in p_j.keys():
            #        p_stats[k].append(p_j[k])
            ## Are params of this idx outlier-like?
            #for k in p_i.keys():
            #    p_mean = np.mean(p_stats)
            #    p_std = np.std(p_stats)
            #    if p_i[k] > p_mean+p_std or p_i[k] < p_mean-p_std:
            #        # If so, re-set to the local mean
            #        p_i[k] = p_mean
            ## Re-fit, then save the result
            #p_reopt = saxs_fit.fit_spectrum(q_I[idx],f[idx],p_i,pfix[idx])
            #p_new.append(p_reopt)



