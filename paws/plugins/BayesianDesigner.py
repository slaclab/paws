from functools import partial
from threading import Thread,Condition
import copy

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.stats import norm as scipynorm
from matplotlib import pyplot as plt

from .PawsPlugin import PawsPlugin

class BayesianDesigner(PawsPlugin):
    """Design tool employing Bayesian Optimization on a Gaussian Process prior."""

    def __init__(self,
            strategy='MPI',strategic_params={'exploration_incentive':0.},
            noise_sd=0.,x_domain={},targets={},constraints={},
            range_constraints={},categorical_constraints={},
            covariance_kernel='sq_exp',covariance_kernel_params={'width':1.},
            MC_max_iter=1000,MC_alpha=1.,
            verbose=False,log_file=None):
        """Create a BayesianDesigner.

        Parameters
        ----------
        strategy : str
            optimization strategy (currently only 'MPI' is supported).
            'MPI' seeks to Maximize the Probability of Improvement for all targets,
            while (jointly) maximizing the likelihood of satisfying all constraints.
        strategic_params : dict
            parameters that affect the optimization strategy
            (currently only 'exploration_incentive' is supported)
        noise_sd : float
            standard deviation of observation noise- if greater than zero,
            the diagonal covariance elements are augmented by `noise_sd`**2.
        x_domain : dict
            dict of input column names and corresponding [min,max] lists 
        targets : dict
            dict of output names (keys) and target specifiers 
            (either 'minimize' or 'maximize')
        constraints : dict
            dict of output names (keys) and real-valued targets (values) 
        range_constraints: dict
            dict of output names (keys) and [min,max] constraint ranges (values)-
            specify open intervals by setting min or max to None. 
        categorical_constraints : dict
            dict of output names (keys) and categorical targets (values) 
        covariance_kernel : str
            choice of covariance kernel- currently either 'inv_exp' or 'sq_exp'
        covariance_kernel_params : dict 
            dict of covariance kernel parameters (currently only 'width' is supported) 
        MC_max_iter : int
            number of Monte Carlo iterations for optimizing acquisition function
        MC_alpha : int
            scaling factor for Monte Carlo random steps 
        verbose : bool
        log_file : str
        """
        super(BayesianDesigner,self).__init__(verbose=verbose,log_file=log_file)
        self.strategy = strategy
        self.strat_params = strategic_params 
        self.noise_sd = noise_sd 
        self.x_domain = x_domain
        self.targets = targets
        self.constraints = constraints
        self.range_constraints = range_constraints
        self.categorical_constraints = categorical_constraints
        self.covariance_kernel = covariance_kernel
        self.cov_params = covariance_kernel_params
        self.MC_max_iter = MC_max_iter
        self.MC_alpha = MC_alpha
        self.modeling_lock = Condition()
        self.candidate_lock = Condition()
        self._candidates = []
        self.dataset = None
        # TODO: check targets and constraints for redundant keys,
        # raise an exception if any are found
        
    @staticmethod
    def _sq_exp_kernel(x1,x2,width):
        return np.exp(-np.sum((x2-x1)**2)/(2*width**2))

    @staticmethod
    def _inv_exp_kernel(x1,x2,width):
        return np.exp(-np.linalg.norm(x2-x1)/(width))

    def cov_kernel(self,x1,x2):
        if self.covariance_kernel == 'sq_exp':
            return self._sq_exp_kernel(x1,x2,self.cov_params['width'])
        elif self.covariance_kernel == 'inv_exp':
            return self._inv_exp_kernel(x1,x2,self.cov_params['width'])
        else:
            raise ValueError('invalid kernel specification: {}'.format(self.covariance_kernel))

    def add_samples(self,*args):
        with self.modeling_lock:
            for sampl in args:
                self.dataset = self.dataset.append(sampl,ignore_index=True)
        self.set_data()

    def set_data(self,df=None):
        if self.verbose: self.message_callback('LOCKING AND SETTING UP MODEL')
        with self.modeling_lock:
            self.dataset = df
            # standardize x values
            self.x_scaler = MinMaxScaler()
            x_keys = list(self.x_domain.keys())
            x_domain_df = pd.DataFrame(self.x_domain,columns=x_keys)
            self.x_scaler.fit(x_domain_df)
            self.xs_domain_df = pd.DataFrame(self.x_scaler.transform(x_domain_df),columns=x_keys)
            self.xs_df = pd.DataFrame(self.x_scaler.transform(df[x_keys]),columns=x_keys)
            # build the covariance matrix, save its inverse 
            nx = self.xs_df.shape[0]
            self.cov_mat = np.array([[
                    self.cov_kernel(self.xs_df.loc[ix1,:],self.xs_df.loc[ix2,:]) 
                    for ix2 in range(nx)] for ix1 in range(nx)]) 
            if self.noise_sd > 0.:
                self.cov_mat += self.noise_sd**2*np.eye(self.cov_mat.shape[0])
            self.inv_cov_mat = np.linalg.inv(self.cov_mat)
            self._set_target_data()
            if self.verbose: self.message_callback('MODEL SETUP COMPLETE!')
    
    def _set_target_data(self):

        # dicts for holding scalers, scaled values, gp model surrogates, incumbents,
        # index filters, and index-filtered inverse covariance matrices
        self.y_scalers = {}
        self.y_arrays = {}
        self.ys_arrays = {}
        self.gp_arrays = {}
        self.gp_range_constraints = {} 
        self.gp_categorical_constraints = {} 
        self.gp_incumbents = {}
        self.filter_flags = {}
        self.good_idxs = {}
        self.filtered_cov_mats = {}
        self.filtered_inv_cov_mats = {}

        # model zero-centered integers (-1 and 1) for all categorical constraints
        for y_key, y_cat in self.categorical_constraints.items():
            y_array = np.array(self.dataset[y_key],dtype=int)
            good_idx = np.invert(np.isnan(y_array))
            self.good_idxs[y_key] = good_idx
            y_array = y_array[good_idx].reshape(-1,1)  
            self.y_arrays[y_key] = y_array
            self.ys_arrays[y_key] = y_array
            self.gp_arrays[y_key] = copy.deepcopy(y_array) 
            # let the decision boundary lie at zero: set False labels to -1
            self.gp_arrays[y_key][self.ys_arrays[y_key]==0]=-1
            self.gp_categorical_constraints[y_key] = 1
            if not bool(y_cat):
                self.gp_categorical_constraints[y_key] = -1
            self.filter_flags[y_key] = not self.good_idxs[y_key].all()
            if self.filter_flags[y_key]:
                # TODO: check if any self.good_idxs match,
                # and if so, use the corresponding self.filtered_inv_cov_mats,
                # instead of computing yet another inverse
                self.filtered_cov_mats[y_key] = self.cov_mat[good_idx,:][:,good_idx]  
                self.filtered_inv_cov_mats[y_key] = np.linalg.inv(self.filtered_cov_mats[y_key]) 

        # model standardized values for all range constraints
        for y_key, y_range in self.range_constraints.items():
            y_array = np.array(self.dataset[y_key])
            good_idx = np.invert(np.isnan(y_array))
            self.good_idxs[y_key] = good_idx
            y_array = y_array[good_idx].reshape(-1,1) 
            self.y_arrays[y_key] = y_array
            self.y_scalers[y_key] = StandardScaler()
            self.y_scalers[y_key].fit(y_array)
            self.ys_arrays[y_key] = self.y_scalers[y_key].transform(y_array)
            self.gp_arrays[y_key] = self.ys_arrays[y_key]
            self.gp_range_constraints[y_key] = [None,None]
            if y_range[0] is not None:
                self.gp_range_constraints[y_key][0] = \
                    self.y_scalers[y_key].transform(np.array(y_range[0]).reshape(-1,1))[0,0]
            if y_range[1] is not None:
                self.gp_range_constraints[y_key][1] = \
                    self.y_scalers[y_key].transform(np.array(y_range[1]).reshape(-1,1))[0,0]
            self.filter_flags[y_key] = not self.good_idxs[y_key].all()
            if self.filter_flags[y_key]:
                self.filtered_cov_mats[y_key] = self.cov_mat[good_idx,:][:,good_idx]  
                self.filtered_inv_cov_mats[y_key] = np.linalg.inv(self.filtered_cov_mats[y_key]) 

        # model exact value constraints 
        # by the likelihood to optimize the error
        # relative to the incumbent best sample 
        # TODO: how to use self.strategy here?
        for y_key, y_val in self.constraints.items():
            y_array = np.array(self.dataset[y_key])
            good_idx = np.invert(np.isnan(y_array))
            self.good_idxs[y_key] = good_idx
            y_array = y_array[good_idx].reshape(-1,1)  
            self.y_arrays[y_key] = y_array
            self.y_scalers[y_key] = StandardScaler()
            self.y_scalers[y_key].fit(y_array)
            y_scaled = np.array(self.y_scalers[y_key].transform(y_array))
            self.ys_arrays[y_key] = y_scaled 
            self.gp_arrays[y_key] = y_scaled 
            y_diff_sqr = (y_array-y_val)**2
            self.gp_incumbents[y_key] = self.gp_arrays[y_key][np.argmin(y_diff_sqr)][0]
            self.filter_flags[y_key] = not self.good_idxs[y_key].all()
            if self.filter_flags[y_key]:
                self.filtered_cov_mats[y_key] = self.cov_mat[good_idx,:][:,good_idx]  
                self.filtered_inv_cov_mats[y_key] = np.linalg.inv(self.filtered_cov_mats[y_key]) 

        # model targets by the likelihood to optimize (min or max)
        # relative to the incumbent best sample,
        # in the context of self.strategy
        for y_key, targ_spec in self.targets.items():
            y_array = np.array(self.dataset[y_key])
            good_idx = np.invert(np.isnan(y_array))
            self.good_idxs[y_key] = good_idx
            y_array = y_array[good_idx].reshape(-1,1)   
            self.y_scalers[y_key] = StandardScaler()
            self.y_scalers[y_key].fit(y_array)
            self.ys_arrays[y_key] = self.y_scalers[y_key].transform(y_array)
            self.gp_arrays[y_key] = self.ys_arrays[y_key]
            #if self.x_cov_noise > 0.:
            #    gp_preds = []
            #    for ix in self.xs_df.index:
            #        xs = np.array(self.xs_df.loc[ix,:]) 
            #        cov_vec = self.cov_vector(xs)
            #        gp_preds.append(self._gp_mean(cov_vec,self.gp_arrays[y_key])) 
            #    gp_preds = np.array(gp_preds)
            #else:
            if targ_spec == 'minimize':
                self.gp_incumbents[y_key] = np.min(self.gp_arrays[y_key])
            elif targ_spec == 'maximize':
                self.gp_incumbents[y_key] = np.max(self.gp_arrays[y_key])
            else:
                raise ValueError('unsupported target for {}: {}'
                        .format(y_key,target_spec))
            self.filter_flags[y_key] = not self.good_idxs[y_key].all()
            if self.filter_flags[y_key]:
                self.filtered_cov_mats[y_key] = self.cov_mat[good_idx,:][:,good_idx]  
                self.filtered_inv_cov_mats[y_key] = np.linalg.inv(self.filtered_cov_mats[y_key]) 

    def set_targets(self,**kwargs):
        with self.modeling_lock:
            for y_key,targ_spec in kwargs.items():
                if not y_key in self.targets:
                    raise KeyError('target key {} does not exist'.format(y_key))
                self.targets[y_key] = targ_spec
            self._set_target_data()
        if self.verbose: self.message_callback('targets set: {}'.format(kwargs))

    def set_constraints(self,**kwargs):
        with self.modeling_lock:
            for y_key,y_val in kwargs.items():
                if not y_key in self.constraints:
                    raise KeyError('constraint key {} does not exist'.format(y_key))
                self.constraints[y_key] = y_val
            self._set_target_data()
        if self.verbose: self.message_callback('constraints set: {}'.format(kwargs))

    def set_categorical_constraints(self,**kwargs):
        with self.modeling_lock:
            for y_key,y_val in kwargs.items():
                if not y_key in self.categorical_constraints:
                    raise KeyError('categorical constraint key {} does not exist'.format(y_key))
                self.categorical_constraints[y_key] = y_cat
            self._set_target_data()
        if self.verbose: self.message_callback('categorical constraints set: {}'.format(kwargs))

    def set_range_constraints(self,**kwargs):
        with self.modeling_lock:
            for y_key,y_val in kwargs.items():
                if not y_key in self.range_constraints:
                    raise KeyError('range constraint key {} does not exist'.format(y_key))
                self.range_constraints[y_key] = y_range
            self._set_target_data()
        if self.verbose: self.message_callback('range constraints set: {}'.format(kwargs))

    def cov_vector(self,xs,idx_filter=None):
        if idx_filter is None:
            xs_idx = np.array(self.xs_df.index)
        else:
            xs_idx = np.array(self.xs_df.index)[idx_filter]
        covv = np.array([self.cov_kernel(xs,self.xs_df.loc[ix,:]) for ix in xs_idx])
        return covv 

    def _gp_var(self,cov_vector,inv_cov_mat):
        self_cov = 1.
        if self.noise_sd > 0.:
            self_cov = 1.+self.noise_sd**2
        return self_cov-np.dot(np.dot(cov_vector,inv_cov_mat),cov_vector)

    def _gp_mean(self,cov_vector,inv_cov_mat,y_vector):
        return np.dot(np.dot(cov_vector,inv_cov_mat),y_vector)

    def _compute_cov(self,xs,y_key=None):
        if y_key:
            covvec = self.cov_vector(xs,self.good_idxs[y_key])
            gp_var = self._gp_var(covvec,self.filtered_inv_cov_mats[y_key])
        else:
            covvec = self.cov_vector(xs)
            gp_var = self._gp_var(covvec,self.inv_cov_mat)
        if gp_var <= 0.: 
            gp_sd = 0.
        else:
            gp_sd = np.sqrt(gp_var)
        return covvec,gp_var,gp_sd

    def predict_outputs(self,xs):
        preds = {} 
        gp_preds = {} 
        gp_scores = {} 

        with self.modeling_lock:

            # get covariance and gp predictions without filters
            covvec_all,gp_var_all,gp_sd_all = self._compute_cov(xs)

            # evaluate categoricals
            for y_key,gp_cat in self.gp_categorical_constraints.items():
                if self.filter_flags[y_key]:
                    covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                    inv_cov_y = self.filtered_inv_cov_mats[y_key]
                else:
                    covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                    inv_cov_y = self.inv_cov_mat
                gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
                gp_preds[y_key] = [gp_mean_y,gp_sd_y]
                # decision boundary is zero, and the likelihood is the cdf above/below zero
                pred = bool(gp_mean_y>0)
                if pred:
                    proba = float(1.-scipynorm.cdf(0.,gp_mean_y,gp_sd_y))
                else:
                    proba = float(scipynorm.cdf(0.,gp_mean_y,gp_sd_y))
                preds[y_key] = [pred,proba]
                gp_scores[y_key] = self.categorical_probability(gp_cat,gp_mean_y,gp_sd_y)

            # evaluate targets
            for y_key, targ_spec in self.targets.items():
                if self.filter_flags[y_key]:
                    covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                    inv_cov_y = self.filtered_inv_cov_mats[y_key]
                else:
                    covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                    inv_cov_y = self.inv_cov_mat
                gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
                gp_preds[y_key] = [gp_mean_y,gp_sd_y]
                ys_mean = self._gp_mean(covvec_y,inv_cov_y,self.ys_arrays[y_key])[0]
                mean = self.y_scalers[y_key].inverse_transform(np.array(ys_mean).reshape(-1,1))[0,0]
                sd = gp_sd_y*self.y_scalers[y_key].scale_[0]
                preds[y_key] = [mean,sd]
                gp_incumb = self.gp_incumbents[y_key]
                expl_inc = self.strat_params['exploration_incentive']
                gp_scores[y_key] = self.improvement_probability(
                          targ_spec,gp_incumb,gp_mean_y,gp_sd_y,expl_inc)

            # evaluate constraints
            for y_key, y_con in self.constraints.items():
                if self.filter_flags[y_key]:
                    covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                    inv_cov_y = self.filtered_inv_cov_mats[y_key]
                else:
                    covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                    inv_cov_y = self.inv_cov_mat
                gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
                gp_preds[y_key] = [gp_mean_y,gp_sd_y]
                ys_mean = self._gp_mean(covvec_y,inv_cov_y,self.ys_arrays[y_key])[0]
                mean = self.y_scalers[y_key].inverse_transform(np.array(ys_mean).reshape(-1,1))[0,0]
                sd = gp_sd_y*self.y_scalers[y_key].scale_[0]
                preds[y_key] = [mean,sd]
                #expl_inc = self.strat_params['exploration_incentive']
                # TODO: think about how to incorporate exploration incentive here
                ys_con = self.y_scalers[y_key].transform(np.array(y_con).reshape(-1,1))[0,0]
                gp_incumb = self.gp_incumbents[y_key]
                incumb_abserr = np.abs(gp_incumb-ys_con)
                gp_rc = [ys_con-incumb_abserr,ys_con+incumb_abserr]
                range_val = self.range_probability(gp_rc,gp_mean_y,gp_sd_y)
                max_range_val = 2*incumb_abserr/np.sqrt(2.*np.pi*gp_sd_y**2)
                acq_val = range_val/max_range_val
                gp_scores[y_key] = acq_val

            # evaluate range constraints
            for y_key,gp_rc in self.gp_range_constraints.items():
                if self.filter_flags[y_key]:
                    covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                    inv_cov_y = self.filtered_inv_cov_mats[y_key]
                else:
                    covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                    inv_cov_y = self.inv_cov_mat
                gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
                gp_preds[y_key] = [gp_mean_y,gp_sd_y]
                ys_mean = self._gp_mean(covvec_y,inv_cov_y,self.ys_arrays[y_key])[0]
                mean = self.y_scalers[y_key].inverse_transform(np.array(ys_mean).reshape(-1,1))[0,0]
                sd = gp_sd_y*self.y_scalers[y_key].scale_[0]
                preds[y_key] = [mean,sd]
                gp_scores[y_key] = self.range_probability(gp_rc,gp_mean_y,gp_sd_y)

        return preds,gp_preds,gp_scores

    def plot_outputs(self,gp_preds,gp_scores):
        # cats
        for y_key,gp_cat in self.gp_categorical_constraints.items():
            print('{} score: {}'.format(y_key,gp_scores[y_key]))
            self.plot_distrib(y_key,gp_preds[y_key][0],gp_preds[y_key][1],boundary=0.,target=gp_cat)
        # ranges
        for y_key,gp_rc in self.gp_range_constraints.items():
            print('{} score: {}'.format(y_key,gp_scores[y_key]))
            self.plot_distrib(y_key,gp_preds[y_key][0],gp_preds[y_key][1],lower=gp_rc[0],upper=gp_rc[1])
        # vals
        for y_key, y_con in self.constraints.items():
            print('{} score: {}'.format(y_key,gp_scores[y_key]))
            ys_con = self.y_scalers[y_key].transform(np.array(y_con).reshape(-1,1))[0,0]
            incumb = self.gp_incumbents[y_key]
            incumb_abserr = np.abs(incumb-ys_con)
            tgt_range = [ys_con-incumb_abserr,ys_con+incumb_abserr]
            self.plot_distrib(y_key,gp_preds[y_key][0],gp_preds[y_key][1],
                    lower=tgt_range[0],target=ys_con,upper=tgt_range[1])
        # targs
        for y_key, targ_spec in self.targets.items():
            print('{} score: {}'.format(y_key,gp_scores[y_key]))
            incumb = self.gp_incumbents[y_key]
            self.plot_distrib(y_key,gp_mean,gp_sd,incumbent=incumb)

    def _joint_acq_func(self,xs):
        acq_vals = []
            
        # get covariance and gp predictions without filters
        covvec_all,gp_var_all,gp_sd_all = self._compute_cov(xs)

        # compute acq. value for each categorical constraint:
        # this should be the likelihood of the prediction 
        # to project onto the specified category 
        for y_key,gp_cat in self.gp_categorical_constraints.items():
            if self.filter_flags[y_key]:
                covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                inv_cov_y = self.filtered_inv_cov_mats[y_key]
            else:
                covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                inv_cov_y = self.inv_cov_mat
            gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
            acq_val = self.categorical_probability(gp_cat,gp_mean_y,gp_sd_y)
            acq_vals.append(acq_val)

        # compute acq. value for each target:
        # this should be the likelihood of optimizing the target,
        # in the context of self.strategy 
        for y_key,target_spec in self.targets.items():
            if self.filter_flags[y_key]:
                covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                inv_cov_y = self.filtered_inv_cov_mats[y_key]
            else:
                covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                inv_cov_y = self.inv_cov_mat
            gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
            expl_inc = self.strat_params['exploration_incentive']
            gp_incumb = self.gp_incumbents[y_key]
            if self.strategy == 'MPI':
                acq_val = self.improvement_probability(
                          target_spec,gp_incumb,gp_mean_y,gp_sd_y,expl_inc)
                acq_vals.append(acq_val)
            else:
                raise ValueError('optimization strategy {} not supported'.format(self.strategy))

        # compute acq. value for each constraint:
        # this should be the likelihood of optimizing
        # the value relative to the incumbent 
        for y_key,y_con in self.constraints.items():
            if self.filter_flags[y_key]:
                covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                inv_cov_y = self.filtered_inv_cov_mats[y_key]
            else:
                covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                inv_cov_y = self.inv_cov_mat
            gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
            ys_con = self.y_scalers[y_key].transform(np.array(y_con).reshape(-1,1))[0,0]
            gp_incumb = self.gp_incumbents[y_key]
            incumb_abserr = np.abs(gp_incumb-ys_con)
            gp_rc = [ys_con-incumb_abserr,ys_con+incumb_abserr]
            range_val = self.range_probability(gp_rc,gp_mean_y,gp_sd_y)
            max_range_val = 2*incumb_abserr/np.sqrt(2.*np.pi*gp_sd_y**2)
            acq_val = range_val/max_range_val
            acq_vals.append(acq_val)
            
        # compute acq. value for each range constraint:
        # this should be the likelihood of the prediction 
        # to fall within the range of the constraint
        for y_key,gp_rc in self.gp_range_constraints.items():
            if self.filter_flags[y_key]:
                covvec_y,gp_var_y,gp_sd_y = self._compute_cov(xs,y_key)
                inv_cov_y = self.filtered_inv_cov_mats[y_key]
            else:
                covvec_y,gp_var_y,gp_sd_y = covvec_all,gp_var_all,gp_sd_all 
                inv_cov_y = self.inv_cov_mat
            gp_mean_y = self._gp_mean(covvec_y,inv_cov_y,self.gp_arrays[y_key])[0]
            acq_val = self.range_probability(gp_rc,gp_mean_y,gp_sd_y)
            acq_vals.append(acq_val)

        return np.product(acq_vals)

    def improvement_probability(self,target_spec,incumb,gp_mean,gp_sd,expl_inc):
        if target_spec == 'maximize':
            ztarg = (gp_mean-incumb-expl_inc)/gp_sd
        elif target_spec == 'minimize':
            ztarg = (incumb-gp_mean-expl_inc)/gp_sd
        acq_val = scipynorm.cdf(ztarg)
        return acq_val
 
    def range_probability(self,gp_range,gp_mean,gp_sd):
        cdf_ub = 1.
        if gp_range[1] is not None:
            cdf_ub = scipynorm.cdf(gp_range[1],gp_mean,gp_sd)
        cdf_lb = 0.
        if gp_range[0] is not None: 
            cdf_lb = scipynorm.cdf(gp_range[0],gp_mean,gp_sd)
        acq_val = cdf_ub - cdf_lb 
        return acq_val

    def categorical_probability(self,gp_cat,gp_mean,gp_sd):
        if gp_cat==1:
            # get the probability of a value greater than zero
            acq_val = 1.-scipynorm.cdf(0,gp_mean,gp_sd)
        else: 
            # get the probability of a value less than zero
            acq_val = scipynorm.cdf(0,gp_mean,gp_sd)
        return acq_val

    def optimize_candidate(self):
        if self.verbose: self.message_callback('starting candidate optimization')
        # take the running_lock and wait on it-
        # this ensures that the optimization method
        # gets priority to take the modeling_lock
        with self.running_lock:
            opt_thread = Thread(target=self._optimize_candidate)
            opt_thread.start()
            self.running_lock.wait()

    def get_next_candidate(self):
        if self.verbose: self.message_callback('fetching candidate...')
        with self.candidate_lock:
            while not self._candidates:
                if self.verbose: self.message_callback(
                    'no candidates- waiting...')
                # wait() to release candiate_lock and await notification 
                self.candidate_lock.wait()
            cand_data = self._candidates.pop(0)
            #####
            xs = cand_data['xs_array']
            preds,gp_preds,gp_scores = self.predict_outputs(xs)
            cand_data.update(prediction=preds,gp_prediction=gp_preds,scores=gp_scores)
            #####
        return cand_data

    def _optimize_candidate(self):
        with self.modeling_lock:
            if self.verbose:
                self.message_callback('LOCKING MODEL AND SEEKING CANDIDATE')
            # the thread that launched this method 
            # should be waiting for a self.run_notify(),
            # to avoid accidentally stealing the modeling_lock
            self.run_notify()
            xs_opt, acq_val = self._optimize_acq()
            # inverse-transform the optimized candidate
            x_opt = self.x_scaler.inverse_transform(xs_opt.reshape(1,-1))[0]
            # store the optimized candidate in a dict, keyed by column names
            cand_opt = dict([(xk,xval) for xk,xval in zip(self.xs_df.columns,x_opt)])
            cand_opt_s = dict([(xk,xsval) for xk,xsval in zip(self.xs_df.columns,xs_opt)])
            candidate_data = {'targets':copy.deepcopy(self.targets),\
                'constraints':copy.deepcopy(self.constraints),\
                'range_constraints':copy.deepcopy(self.range_constraints),\
                'categorical_constraints':copy.deepcopy(self.categorical_constraints),\
                'candidate':cand_opt,'scaled_candidate':cand_opt_s,\
                'xs_array':xs_opt,'acquisition_value':acq_val}
            with self.candidate_lock:
                self._candidates.append(candidate_data)
                # send notification in case there is a thread waiting for the result 
                self.candidate_lock.notify()

    def _optimize_acq(self):
        if self.verbose: 
            self.message_callback('starting {} MC iterations at alpha={}'
                                .format(self.MC_max_iter,self.MC_alpha))

        # start with a random value
        #xs_best = np.array([np.random.rand(1)[0] for xkey in self.x_domain.keys()])

        # start on a grid or on the best-yet training set point-
        # TODO: add inputs for selecting start point strategy 
        ts_acq = [self._joint_acq_func(np.array(self.xs_df.loc[ix,:])) for ix in self.xs_df.index]
        ts_acq = np.array(ts_acq)
        ibest = np.argmax(ts_acq)
        xs_best = np.array(self.xs_df.iloc[ibest,:])

        obj_best = self._joint_acq_func(xs_best)
        xs_current = xs_best
        obj_current = obj_best
        n_acc = 0
        for iit in range(1,self.MC_max_iter+1):
            # apply a random change
            delta_xs = 2*self.MC_alpha*np.array([np.random.rand(1)[0]-0.5 for xx in xs_current])
            xs_new = xs_current + delta_xs 
            # if it violates the domain, reject
            if any([xn<0. or xn>1. for xn in xs_new]):
                obj_new = 0.
                #print('DOMAIN VIOLATION: REJECT')
            else:
                # evaluate the objective
                obj_new = self._joint_acq_func(xs_new)
                # if the objective goes up, keep it
                if (obj_new > obj_current):
                    #print('IMPROVEMENT: {} --> {}'.format(obj_current,obj_new))
                    xs_current = xs_new
                    obj_current = obj_new
                    n_acc += 1
                    # if this is the best yet, save it
                    if (obj_new > obj_best):
                        #print('*** NEW BEST: {} --> {}'.format(obj_best,obj_new))
                        xs_best = xs_new 
                        obj_best = obj_new 
                else:
                    # if the objective goes down, make a stochastic decision
                    bdry = np.random.rand(1)[0]
                    #print('PROPOSAL: {} --> {}'.format(obj_current,obj_new))
                    if (obj_current <= 0.) or (obj_new/obj_current > bdry):
                        #print('ACCEPTED: {} > {}'.format(obj_new/obj_current,bdry))
                        #print('ACCEPTED: objective {} -> {}'.format(obj_current,obj_new))
                        xs_current = xs_new
                        obj_current = obj_new
                        n_acc += 1

            if (np.mod(iit,1000)==0) or (iit<1000 and np.mod(iit,100)==0):
                # check the acceptance ratio
                ac_ratio = float(n_acc)/iit
                if self.verbose:
                    self.message_callback('iter {}/{}- acceptance ratio: {}, best value: {}'.format(
                    iit,self.MC_max_iter,ac_ratio,obj_best))

        return xs_best, obj_best

    def plot_distrib(self,y_key,gp_mean,gp_sd,**kwargs):
        print('target: {}'.format(y_key))
        print('prediction: {} (sd: {}))'.format(gp_mean,gp_sd))
        gp_range = np.linspace(gp_mean-6.*gp_sd,gp_mean+6.*gp_sd,num=100)
        gp_pdf = scipynorm.pdf(gp_range,gp_mean,gp_sd)*(self.gp_arrays[y_key].shape[0])
        plt.figure()
        plt.plot(gp_range,gp_pdf,'r')
        kwkeys = list(kwargs.keys())
        plotkeys = []
        for kwkey in kwkeys:
            kwval = kwargs[kwkey]
            if kwval is not None:
                plotkeys.append(kwkey)
                plt.axvline(x=kwval)
        plt.hist(self.gp_arrays[y_key],bins=round(self.gp_arrays[y_key].shape[0]))
        plt.legend(['gp prediction']+plotkeys+['training samples'])
        plt.show()

