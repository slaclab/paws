from functools import partial
from threading import Thread,Condition
import copy

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.stats import norm as scipynorm

from .PawsPlugin import PawsPlugin

class BayesianDesigner(PawsPlugin):
    """PawsPlugin for experimental design by Gaussian Process Bayesian Optimization."""

    def __init__(self,dataset=pd.DataFrame(),
        x_domain={},targets={},constraints={},range_constraints={},categorical_constraints={},
        covariance_kernel='sq_exp',covariance_kernel_width=1.,MC_max_iter=1000,MC_alpha=1.,
        verbose=False,log_file=None):
        """Create a BayesianDesigner.

        Parameters
        ----------
        dataset : pandas.DataFrame
            pandas DataFrame containing the modeling dataset 
        x_domain : dict
            dict of input column names and corresponding [min,max] lists 
        targets : dict
            dict of output names (keys) and target specifiers 
            (either "minimize" or "maximize")
        constraints : dict
            dict of output names (keys) and real-valued targets (values) 
        range_constraints: dict
            dict of output names (keys) and [min,max] constraint ranges (values) 
        categorical_constraints : dict
            dict of output names (keys) and categorical targets (values) 
        covariance_kernel : str
            choice of covariance kernel- currently either 'inv_exp' or 'sq_exp'
        covariance_kernel_width : float
            characteristic width of covariance kernel 
        MC_max_iter : int
            number of Monte Carlo iterations for optimizing acquisition function
        MC_alpha : int
            scaling factor for Monte Carlo random increments
        verbose : bool
        log_file : str
        """
        super(BayesianDesigner,self).__init__(verbose=verbose,log_file=log_file)
        self.x_domain = x_domain
        self.targets = targets
        self.constraints = constraints
        self.range_constraints = range_constraints
        self.categorical_constraints = categorical_constraints
        self.exploration_candidates = []
        self.exploitation_candidates = []
        self.covariance_kernel = covariance_kernel
        self.covariance_kernel_width = covariance_kernel_width
        self.MC_max_iter = MC_max_iter
        self.MC_alpha = MC_alpha
        self.modeling_lock = Condition()
        self.exploration_lock = Condition()
        self.exploitation_lock = Condition()
        self.set_data(dataset)
        
    @staticmethod
    def sq_exp_kernel(width,x1,x2):
        return np.exp(-np.sum((x2-x1)**2)/(2*width**2))

    @staticmethod
    def inv_exp_kernel(width,x1,x2):
        return np.exp(-np.linalg.norm(x2-x1)/(2*width))

    def set_data(self,df=None):
        if df is None: df = self.dataset
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
            # standardize y values 
            y_keys = list(self.constraints.keys()) + list(self.range_constraints.keys())
            self.y_scalers = dict.fromkeys(y_keys)
            self.ys_df = pd.DataFrame(columns=y_keys,index=df.index)
            for y_key in y_keys:
                y_array = np.array(df[y_key]).reshape(-1,1)
                self.y_scalers[y_key] = StandardScaler()
                self.y_scalers[y_key].fit(y_array)
                self.ys_df[y_key] = np.array(self.y_scalers[y_key].transform(y_array))
            self.ys_constraints = {}
            for y_key in self.constraints.keys():
                self.ys_constraints[y_key] = \
                self.y_scalers[y_key].transform(np.array(self.constraints[y_key])\
                .reshape(-1,1))[:,0].tolist()[0]
            self.ys_range_constraints = {}
            for y_key in self.range_constraints.keys():
                self.ys_range_constraints[y_key] = \
                self.y_scalers[y_key].transform(np.array(self.range_constraints[y_key])\
                .reshape(-1,1))[:,0].tolist()
            # build the covariance matrix, save its inverse 
            ckw = self.covariance_kernel_width
            nx = self.xs_df.shape[0]
            if self.covariance_kernel == 'sq_exp':
                self.cov_mat = np.array([[self.sq_exp_kernel(ckw,self.xs_df.loc[ix1,:],self.xs_df.loc[ix2,:]) 
                            for ix2 in range(nx)] for ix1 in range(nx)] ) 
            elif self.covariance_kernel == 'inv_exp':
                self.cov_mat = np.array([[self.inv_exp_kernel(ckw,self.xs_df.loc[ix1,:],self.xs_df.loc[ix2,:]) 
                            for ix2 in range(nx)] for ix1 in range(nx)] ) 
            else:
                raise ValueError('invalid kernel specification: {}'.format(self.covariance_kernel))
            self.inv_cov_mat = np.linalg.inv(self.cov_mat)

            # build estimators for all constrants/targets
            self.xplr_acq_factors = {}
            self.xploit_acq_factors = {}
            self.estimators = {}

            for y_key,target_spec in self.targets.items():
                ys_vector = self.ys_df.loc[:,y_key]
                gp_estimator = partial(self._gp_stats,ys_vector)
                if target_spec == 'maximize':
                    ys_incumbent = np.max(ys_vector)
                    Z_trans_xploit = partial(self.Z_PI,0.,gp_estimator,ys_incumbent)
                    Z_trans_xplr = partial(self.Z_PI,1.,gp_estimator,ys_incumbent)
                elif target_spec == 'minimize':
                    ys_incumbent = np.min(ys_vector)
                    negative_gp_estimator = partial(self._gp_stats,-1*ys_vector)
                    Z_trans_xploit = partial(self.Z_PI,0.,negative_gp_estimator,-1*ys_incumbent)
                    Z_trans_xplr = partial(self.Z_PI,1.,negative_gp_estimator,-1*ys_incumbent)
                target_func_xplr = partial(self.PI_cdf,Z_trans_xplr)
                target_func_xploit = partial(self.PI_cdf,Z_trans_xploit)
                self.xplr_acq_factors[y_key] = target_func_xplr 
                self.xploit_acq_factors[y_key] = target_func_xploit 
                self.estimators[y_key] = gp_estimator

            for y_key,ys_con in self.ys_constraints.items():
                ys_vector = self.ys_df.loc[:,y_key]
                gp_estimator = partial(self._gp_stats,ys_vector)
                negative_gp_estimator = partial(self._gp_stats,-1*ys_vector)
                Zlo_trans_xploit = partial(self.Z_PI,0.,gp_estimator,ys_con)
                Zhi_trans_xploit = partial(self.Z_PI,0.,negative_gp_estimator,-1*ys_con)
                Zlo_trans_xplr = partial(self.Z_PI,1.,gp_estimator,ys_con)
                Zhi_trans_xplr = partial(self.Z_PI,1.,negative_gp_estimator,-1*ys_con)
                target_func_xploit = partial(self.two_sided_cdf,Zlo_trans_xploit,Zhi_trans_xploit,4.) 
                target_func_xplr = partial(self.two_sided_cdf,Zlo_trans_xplr,Zhi_trans_xplr,4.) 
                self.xplr_acq_factors[y_key] = target_func_xplr 
                self.xploit_acq_factors[y_key] = target_func_xploit 
                self.estimators[y_key] = gp_estimator

            for y_key,ys_range in self.ys_range_constraints.items():
                ys_vector = self.ys_df.loc[:,y_key]
                gp_estimator = partial(self._gp_stats,ys_vector)
                negative_gp_estimator = partial(self._gp_stats,-1*ys_vector)
                # weight range constraints by a product of two error functions, one at each boundary
                # for the lower bound, use the bound as the incumbent_value to encourage sampling above it
                Zlo_trans = partial(self.Z_PI,0.,gp_estimator,ys_range[0])
                # for the higher bound, use the negative of the bound as incumbent
                Zhi_trans = partial(self.Z_PI,0.,negative_gp_estimator,-1*ys_range[1])
                range_func = partial(self.two_sided_cdf,Zlo_trans,Zhi_trans,1.) 
                self.xplr_acq_factors[y_key] = range_func
                self.xploit_acq_factors[y_key] = range_func
                self.estimators[y_key] = gp_estimator

            for y_key,y_cat in self.categorical_constraints.items():
                y_vector = np.array(self.dataset[y_key])
                if y_cat == 1:
                    gp_estimator = partial(self._gp_stats,y_vector)
                    y_incumbent = 0.5
                elif y_cat == 0:
                    gp_estimator = partial(self._gp_stats,-1*y_vector)
                    y_incumbent = -0.5
                else:
                    raise ValueError('categorical constraints must be 0 or 1')
                Z_trans = partial(self.Z_PI,0.,gp_estimator,y_incumbent)
                cat_func = partial(self.PI_cdf,Z_trans)
                self.xplr_acq_factors[y_key] = cat_func
                self.xploit_acq_factors[y_key] = cat_func
                self.estimators[y_key] = gp_estimator
        if self.verbose: self.message_callback('MODEL SETUP COMPLETE!')

    def add_samples(self,*args):
        with self.modeling_lock:
            for sampl in args:
                self.dataset = self.dataset.append(sampl,ignore_index=True)
        self.set_data()

    def _gp_stats(self,ys_vector,xs):
        ckw = self.covariance_kernel_width
        if self.covariance_kernel == 'sq_exp':
            cov_self = self.sq_exp_kernel(ckw,xs,xs)
            cov_vector = np.array([self.sq_exp_kernel(ckw,xs,self.xs_df.loc[ix,:]) for ix in range(self.xs_df.shape[0])])
        elif self.covariance_kernel == 'inv_exp':
            cov_self = self.inv_exp_kernel(ckw,xs,xs)
            cov_vector = np.array([self.inv_exp_kernel(ckw,xs,self.xs_df.loc[ix,:]) for ix in range(self.xs_df.shape[0])])
        mn = np.dot(np.dot(cov_vector,self.inv_cov_mat),ys_vector)
        var = cov_self-np.dot(np.dot(cov_vector,self.inv_cov_mat),cov_vector)  
        #print('mean: {}, var: {}'.format(mn,var))
        return mn,var

    def compute_exploration_function(self,recipe_dict): 
        with self.modeling_lock:
            x = np.array([recipe_dict[xk] for xk in self.xs_df.columns])
            xs = self.x_scaler.transform(x.reshape(1,-1))
            return self.compute_acq(self.xplr_acq_factors.values(),xs.ravel()) 

    def compute_exploitation_function(self,recipe_dict): 
        with self.modeling_lock:
            x = np.array([recipe_dict[xk] for xk in self.xs_df.columns])
            xs = self.x_scaler.transform(x.reshape(1,-1))
            return self.compute_acq(self.xploit_acq_factors.values(),xs.ravel()) 

    @staticmethod
    def Z_PI(explorative_strength,gp_estimator,incumbent_value,xs):
        gp_mean, gp_var = gp_estimator(xs)
        #print('{} (var: {})'.format(gp_mean,gp_var))
        #if gp_var <= 1.E-12: return 0
        if gp_var <= 0: return 0
        #import pdb; pdb.set_trace()
        return (gp_mean-incumbent_value-explorative_strength)/np.sqrt(gp_var)

    @staticmethod
    def PI_cdf(Z_transform,xs):
        return scipynorm.cdf(Z_transform(xs))

    def two_sided_cdf(self,Zlo_trans,Zhi_trans,scale_factor,xs):
        PI_lo = self.PI_cdf(Zlo_trans,xs)
        PI_hi = self.PI_cdf(Zhi_trans,xs)
        return scale_factor * PI_lo * PI_hi

    def set_constraint(self,constraint_name,constraint_val):
        with self.modeling_lock:
            self.constraints[constraint_name] = constraint_val

    def optimize_exploration_candidate(self):
        if self.verbose: self.message_callback('starting exploration candidate optimization')
        with self.running_lock:
            opt_thread = Thread(target=partial(
                self._optimize_candidate,
                self.xplr_acq_factors.values(),
                self.exploration_candidates,
                self.exploration_lock))
            opt_thread.start()
            self.running_lock.wait()

    def optimize_exploitation_candidate(self):
        if self.verbose: self.message_callback('starting exploitation candidate optimization')
        with self.running_lock:
            opt_thread = Thread(target=partial(
                self._optimize_candidate,
                self.xploit_acq_factors.values(),
                self.exploitation_candidates,
                self.exploitation_lock))
            opt_thread.start()
            self.running_lock.wait()

    def get_exploration_candidate(self):
        if self.verbose: self.message_callback('fetching exploration candidate')
        with self.exploration_lock:
            if not self.exploration_candidates:
                # wait() to release lock and await notification 
                self.exploration_lock.wait()
            cand = self.exploration_candidates.pop(0)
        with self.modeling_lock:
            pred = self.predict(cand)
            acq = self.compute_exploration_function(cand)
        return cand, pred, acq

    def get_exploitation_candidate(self):
        if self.verbose: self.message_callback('fetching exploitation candidate')
        with self.exploitation_lock:
            if not self.exploitation_candidates:
                # wait() to release lock and await notification 
                self.exploitation_lock.wait()
            cand = self.exploitation_candidates.pop(0)
        with self.modeling_lock:
            pred = self.predict(cand)
            acq = self.compute_exploitation_function(cand)
        return cand, pred, acq

    def _optimize_candidate(self,acq_factors,result_container,result_lock):
        if self.verbose:
            self.message_callback('seeking candidate- '
            + '\nconstraints: {} '.format(self.constraints)
            + '\nrange_constraints: {}'.format(self.range_constraints)
            + '\ncategorical constraints: {}'.format(self.categorical_constraints))
        with self.modeling_lock:
            self.run_notify()
            with result_lock:
                xs_opt = self._optimize_acq(acq_factors)
                # inverse-transform the candidate, retrieve recipe 
                x_opt = self.x_scaler.inverse_transform(xs_opt.reshape(1,-1))[0]
                cand_opt = dict([(xk,xval) for xk,xval in zip(self.xs_df.columns,x_opt)])
                if self.verbose:
                    pred = self.predict(cand_opt)
                    msg = 'optimized candidate predictions: '
                    for y_key, pred in pred.items():
                        msg += '\n    {}: {} (var: {})'.format(y_key,pred[0],pred[1]) 
                    msg += '\n    acquisition value: {}'.format(self.compute_acq_for_recipe(acq_factors,cand_opt)) 
                    self.message_callback(msg)
                result_container.append(copy.deepcopy(cand_opt))
                # send notification in case there is a thread waiting for the result 
                result_lock.notify()

    def predict(self,recipe_dict):
        with self.modeling_lock:
            x = np.array([recipe_dict[xk] for xk in self.xs_df.columns])
            xs = self.x_scaler.transform(x.reshape(1,-1))
            predictions = dict.fromkeys(self.estimators.keys())
            for y_key, est in self.estimators.items():
                if y_key in self.constraints \
                or y_key in self.range_constraints \
                or y_key in self.targets:
                    ys_pred,ys_var = est(xs.ravel())
                    y_pred = self.y_scalers[y_key].inverse_transform(ys_pred.reshape(1,-1))
                    # TODO: verify if this is the proper way to inverse-scale the predicted variance
                    y_var = ys_var * self.y_scalers[y_key].scale_[0]**2
                    predictions[y_key] = (y_pred[0,0],y_var)
                elif y_key in self.categorical_constraints:
                    y_pred, y_var = est(xs.ravel())
                    predictions[y_key] = (y_pred, y_var)
        return predictions

    def compute_acq_for_recipe(self,funcs,recipe_dict):
        with self.modeling_lock:
            x = np.array([recipe_dict[xk] for xk in self.xs_df.columns])
            xs = self.x_scaler.transform(x.reshape(1,-1))
        return self.compute_acq(funcs,xs.ravel()) 

    @staticmethod
    def compute_acq(funcs,xs):
        # TODO: all fs should take a the covariance vector as an arg,
        # and the covariance vector should be computed here.
        # Then, the variance estimate should be computed here.
        # The fs should just compute the means
        return np.product([f(xs) for f in funcs])

    def _optimize_acq(self,funcs):
        if self.verbose: 
            self.message_callback('starting {} MC iterations at alpha={}'.format(self.MC_max_iter,self.MC_alpha))
        # start with a random value
        # TODO: start on a grid or on the best-yet training set point-
        # add methods for both and inputs for selecting which one to use
        xs_best = np.array([np.random.rand(1)[0] for xkey in self.x_domain.keys()])
        obj_best = self.compute_acq(funcs,xs_best)
        xs_current = xs_best
        obj_current = obj_best
        n_acc = 0
        for iit in range(1,self.MC_max_iter+1):
            # apply a random change
            delta_xs = self.MC_alpha*np.array([np.random.rand(1)[0]-0.5 for xx in xs_current])
            xs_new = xs_current + delta_xs 
            # if it violates the domain, reject
            if any([xn<0. or xn>1. for xn in xs_new]):
                obj_new = 0.
                #print('DOMAIN VIOLATION: REJECT')
            else:
                # evaluate the objective
                obj_new = self.compute_acq(funcs,xs_new)
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

            if np.mod(iit,100) == 0:
                # check the acceptance ratio
                ac_ratio = float(n_acc)/iit
                if self.verbose:
                    self.message_callback('iter {}/{}: acceptance ratio: {}'.format(
                    iit,self.MC_max_iter,ac_ratio))

        return xs_best

#        # TEST
#        #r0_vector = np.array(self.dataset['r0_sphere'])
#        #r0_gp_estimator = partial(self.gp_stats,r0_vector)
#        y_mean_test = dict.fromkeys(xplr_acq_factors.keys())
#        y_var_test = dict.fromkeys(xplr_acq_factors.keys())
#        xplr_test = dict.fromkeys(xplr_acq_factors.keys())
#        xploit_test = dict.fromkeys(xplr_acq_factors.keys())
#        for y_key in xplr_acq_factors.keys():
#            y_mean_test[y_key] = []
#            y_var_test[y_key] = []
#            xplr_test[y_key] = []
#            xploit_test[y_key] = []
#        #for ix in range(self.xs_df.shape[0]):
#        r0_obj_mean_test = []
#        r0_obj_var_test = []
#        for ix in range(100):
#            # training set sampling:
#            #xcand = self.xs_df.loc[ix,:]
#            # training set plus noise sampling:
#            #xcand = self.xs_df.loc[ix,:] + 0.1*(np.random.rand(self.xs_df.shape[1])-0.5)
#            # random sampling:
#            xcand = np.array([np.random.rand(1)[0] for xkey in self.x_domain.keys()])
#            print('----------- sample {} ------------'.format(ix))
#            print('r0_sphere target: {}'.format(self.constraints['r0_sphere']))
#            #print('r0_sphere value: {}'.format(r0_vector[ix]))
#            #print('r0_sphere estimate: {} (+/- {})'.format(gp_mean,gp_var))
#            for y_key in xplr_acq_factors.keys():
#                y_vector = np.array(self.dataset[y_key])
#                y_gp_estimator = partial(self.gp_stats,y_vector)
#                y_gp_mean,y_gp_var = y_gp_estimator(xcand) 
#                xplr_score = xplr_acq_factors[y_key](xcand)
#                xploit_score = xploit_acq_factors[y_key](xcand)
#                gp_est = estimators[y_key]
#                gp_mean, gp_var = gp_est(xcand)
#                print('{}: {} +/- {} (explore: {}, exploit: {})'.format(
#                    y_key,
#                    y_gp_mean, y_gp_var,
#                    #gp_mean, gp_var,
#                    xplr_score,xploit_score
#                    ))
#                y_mean_test[y_key].append(y_gp_mean)
#                y_var_test[y_key].append(y_gp_var)
#                xplr_test[y_key].append(xplr_score)
#                xploit_test[y_key].append(xploit_score)
#            r0_obj_mean, r0_obj_var = estimators['r0_sphere'](xcand)
#            r0_obj_mean_test.append(r0_obj_mean)
#            r0_obj_var_test.append(r0_obj_var)
#            print('net exploration factor: {}'.format(
#            np.product([func(xcand) for func in xplr_acq_factors.values()])))
#            print('net exploitation factor: {}'.format(
#            np.product([func(xcand) for func in xploit_acq_factors.values()])))
#            #import pdb; pdb.set_trace()
#        from matplotlib import pyplot as plt
#        for y_key in xplr_acq_factors.keys():
#        #for y_key in ['r0_sphere']:
#            plt.figure()
#            plt.clf()
#            plt.scatter(y_mean_test[y_key],y_var_test[y_key],s=20,c=xplr_test[y_key])
#            plt.xlabel('GP mean estimate')
#            plt.ylabel('GP var estimate')
#            plt.title('{}: exploration score'.format(y_key))
#            plt.colorbar()
#
#            plt.figure()
#            plt.clf()
#            plt.scatter(y_mean_test[y_key],y_var_test[y_key],s=20,c=xploit_test[y_key])
#            plt.xlabel('GP mean estimate')
#            plt.ylabel('GP var estimate')
#            plt.title('{}: exploitation score'.format(y_key))
#            plt.colorbar()
#
#        plt.show()
#
#
