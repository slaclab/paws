import numpy as np
import copy
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools
from ....tools.saxs import saxs_fit

class PostProcessTimeSeries(Operation):
    """Re-fit a set of SAXS spectra chronologically, to refine results."""

    def __init__(self):
        input_names = ['batch_outputs','time_key','q_I_key','flags_key','params_key','reports_key']
        output_names = ['new_outputs']
        super(PostProcessTimeSeries,self).__init__(input_names,output_names)        
        self.input_doc['batch_outputs'] = 'list of dicts '\
            'of workflow outputs, produced by a batch execution'
        self.input_doc['time_key'] = 'dict key for time stamp in batch_outputs'
        self.input_doc['flags_key'] = 'dict key for getting spectrum '\
            '(n-by-2 array of q and I) from batch_outputs'
        self.input_doc['flags_key'] = 'dict key for '\
            'population flags in batch_outputs'
        self.input_doc['params_key'] = 'dict key for '\
            'SAXS equation parameters in batch_outputs' 
        self.input_doc['reports_key'] = 'dict key for '\
            'SAXS fitting report in batch_outputs' 
        self.input_type['batch_outputs'] = opmod.workflow_item
        self.output_doc['new_outputs'] = 'list of dicts '\
            'containing time stamps and newly refined parameters'

    def run(self):
        b_out = self.inputs['batch_outputs']
        t = np.array([b[self.inputs['time_key']] for b in b_out])
        q_I = np.array([b[self.inputs['q_I_key']] for b in b_out])
        f = np.array([b[self.inputs['flags_key']] for b in b_out])
        p = np.array([b[self.inputs['params_key']] for b in b_out])
        r = np.array([b[self.inputs['reports_key']] for b in b_out])

        i_xsort = np.argsort(t)
        t = t[i_xsort]
        f = f[i_xsort]
        p = p[i_xsort]
        r = r[i_xsort]
        q_I = q_I[i_xsort]

        n_batch = len(t)
        idx_batch = np.arange(0,n_batch)

        self.outputs['new_outputs'] = []
        for idx in idx_batch:
            if not f[idx]['bad_data'] and not f[idx]['diffraction_peaks']:
                p_i = copy.deepcopy(p[idx])
                rpt_i = r[idx]
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
                    I0_ratio = I0_i / I0_test
                    for Ikey in ['G_precursor','I0_sphere','I0_floor']:
                        if Ikey in p_test.keys():
                            p_test[Ikey] = p_test[Ikey] * I0_ratio
                    print('testing params: \n{}'.format(p_test))
                    #p_opt_test,rpt_test = saxs_fit.fit_spectrum(q_I[idx],f[idx],p_test,rpt_i['fixed_params'],rpt_i['objective']) 
                    p_opt_test,rpt_test = saxs_fit.fit_spectrum(q_I[idx],f[idx],p_test,[],'chi2log') 
                    if rpt_test['objective_after'] < rpt_i['objective_after']:
                        print('*** {}: objective improved ***'.format(__name__))
                        print('*** old: {} ***'.format(rpt_i['objective_after']))
                        print('*** new: {} ***'.format(rpt_i['objective_after']))
                        p_i = p_opt_test
                        rpt_i = rpt_test
                        q = q_I[idx][:,0] 
                        I_new = saxs_fit.compute_saxs(q,f[idx],p_i)
                        out_dict['q_I_opt'] = np.array([q,I_new]).T 

                        from matplotlib import pyplot as plt
                        I_old = saxs_fit.compute_saxs(q,f[idx],p[idx])
                        I0_old = saxs_fit.compute_saxs(np.array([0.]),f[idx],p[idx])
                        I0_new = saxs_fit.compute_saxs(np.array([0.]),f[idx],p_i)
                        plt.plot(q,q_I[idx][:,1])
                        plt.plot(q,I_old)
                        plt.plot(q,I_new)
                        print('I(q=0) \nbefore: {} \nafter: {}'.format(I0_old,I0_new))
                        plt.show()

            out_dict = OrderedDict()
            out_dict[self.inputs['time_key']] = t[idx]
            out_dict[self.inputs['params_key']] = p_i
            out_dict[self.inputs['reports_key']] = rpt_i
            out_dict[self.inputs['flags_key']] = f[idx] 
            out_dict[self.inputs['q_I_key']] = q_I[idx] 
            self.outputs['new_outputs'].append(out_dict)
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



