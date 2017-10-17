import numpy as np
import copy

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools
from ....tools.saxs import saxs_fit

class PostProcessTimeSeries(Operation):
    """Re-fit a set of SAXS spectra chronologically, to refine results."""

    def __init__(self):
        input_names = ['batch_outputs','time_key','qI_key','flags_key','params_key']
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
        self.input_type['batch_outputs'] = opmod.workflow_item
        self.output_doc['new_outputs'] = 'list of dicts '\
            'containing time stamps and newly refined parameters'
        self.inputs['time_key'] = 'time'
        self.inputs['flags_key'] = 'flags'
        self.inputs['params_key'] = 'params'

    def run(self):
        b_out = self.inputs['batch_outputs']
        kq_I = self.inputs['qI_key']
        ktime = self.inputs['time_key']
        kflags = self.inputs['flags_key']
        kparams = self.inputs['params_key']
    
        t = [b[ktime] for b in b_out]
        f = [b[kflags] for b in b_out]
        p = [b[kparams] for b in b_out]
        q_I = [b[kq_I] for b in b_out]
        new_outputs = []

        n_batch = len(b_out)
        idx_batch = np.arange(0,n_batch)

        for idx in idx_batch:
            p_i = copy.deepcopy(p[idx])
            if not idx==0:
                p_test = copy.deepcopy(p[idx-1])
                p_opt_test = saxs_fit.fit_spectrum(q_I[idx],f[idx],p_test,p_i['fixed_params'],p_i['objfun']) 
                if p_opt_test['objective_after'] < p_i['objective_after']:
                    p_i = p_opt_test
            if not idx == n_batch-1:
                p_test = copy.deepcopy(p[idx+1])
                p_opt_test = saxs_fit.fit_spectrum(q_I[idx],f[idx],p_test,p_i['fixed_params'],p_i['objfun']) 
                if p_opt_test['objective_after'] < p_i['objective_after']:
                    p_i = p_opt_test
            new_outputs.append({ktime:t[idx],kparams:p_i})
        self.outputs['new_outputs'] = new_outputs

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



