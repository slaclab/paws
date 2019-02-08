from functools import partial

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import norm as scipynorm

from .PawsPlugin import PawsPlugin

class BayesianFlowDesigner(PawsPlugin):

    def __init__(self,dataset=pd.DataFrame(),
        x_domain={},constraints={},range_constraints={},categorical_constraints={},
        covariance_kernel_width=1.,MC_max_iter=1000,MC_alpha=1.,
        verbose=False,log_file=None):
        """Create a BayesianFlowDesigner.

        Parameters
        ----------
        dataset : pandas.DataFrame
            pandas DataFrame containing the modeling dataset 
        x_domain : dict
            dict of input column names and corresponding [min,max] lists 
        constraints : dict
            dict of output names (keys) and real-valued targets (values) 
        range_constraints: dict
            dict of output names (keys) and [min,max] constraint ranges (values) 
        categorical_constraints : dict
            dict of output names (keys) and categorical targets (values) 
        covariance_kernel_width : float
            characteristic width of squared-exponential covariance matrix
        MC_max_iter : int
            number of Monte Carlo iterations for optimizing acquisition function
        MC_alpha : int
            scaling factor for Monte Carlo random increments
        verbose : bool
        log_file : str
        """
        super(BayesianFlowDesigner,self).__init__(thread_blocking=False,verbose=verbose,log_file=log_file)
        self.x_domain = x_domain
        self.constraints = constraints
        self.range_constraints = range_constraints
        self.categorical_constraints = categorical_constraints
        self.covariance_kernel_width = covariance_kernel_width
        self.MC_max_iter = MC_max_iter
        self.MC_alpha = MC_alpha
        self.set_data(dataset)
        
    def set_data(self,df=None):
        if df is None: df = self.dataset
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
            self.y_scalers[y_key] = MinMaxScaler()
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
        self.cov_mat = np.array([[self.sq_exp_kernel(ckw,self.xs_df.loc[ix1,:],self.xs_df.loc[ix2,:]) 
                            for ix2 in range(nx)] for ix1 in range(nx)] ) 
        self.inv_cov_mat = np.linalg.inv(self.cov_mat)

    def add_samples(self,*args):
        for sampl in args:
            self.dataset = self.dataset.append(sampl,ignore_index=True)
        self.set_data()

    def gp_stats(self,ys_vector,xs):
        ckw = self.covariance_kernel_width
        cov_self = self.sq_exp_kernel(ckw,xs,xs)
        cov_vector = np.array([self.sq_exp_kernel(ckw,xs,self.xs_df.loc[ix,:]) for ix in range(self.xs_df.shape[0])])
        mn = np.dot(np.dot(cov_vector,self.inv_cov_mat),ys_vector)
        var = cov_self-np.dot(np.dot(cov_vector,self.inv_cov_mat),cov_vector)  
        return mn,var

    @staticmethod
    def sq_exp_kernel(width,x1,x2):
        return np.exp(-np.linalg.norm(x2-x1)/(2*width**2))

    @staticmethod
    def Z_PI(explorative_strength,gp_estimator,incumbent_value,xs):
        gp_mean, gp_var = gp_estimator(xs)
        #if gp_var <= 1.E-12: return 0
        if gp_var == 0: return 0
        return (gp_mean-incumbent_value-explorative_strength)/np.sqrt(gp_var)

    @staticmethod
    def PI_cdf(Z_transform,xs):
        return scipynorm.cdf(Z_transform(xs))

    def two_sided_cdf(self,Zlo_trans,Zhi_trans,scale_factor,xs):
        PI_lo = self.PI_cdf(Zlo_trans,xs)
        PI_hi = self.PI_cdf(Zhi_trans,xs)
        return scale_factor * PI_lo * PI_hi

    def get_candidate_recipes(self):
        if self.verbose:
            self.message_callback('seeking candidates- '
            + '\nconstraints: {} '.format(self.constraints)
            + '\nrange_constraints: {}'.format(self.range_constraints)
            + '\ncategorical constraints: {}'.format(self.categorical_constraints))
        xplr_acq_factors = {}
        xploit_acq_factors = {}
        estimators = {}
        for y_key,ys_con in self.ys_constraints.items():
            ys_vector = self.ys_df.loc[:,y_key]
            gp_estimator = partial(self.gp_stats,ys_vector)
            negative_gp_estimator = partial(self.gp_stats,-1*ys_vector)
            Zlo_trans_xploit = partial(self.Z_PI,0.,gp_estimator,ys_con)
            Zhi_trans_xploit = partial(self.Z_PI,0.,negative_gp_estimator,-1*ys_con)
            Zlo_trans_xplr = partial(self.Z_PI,1.,gp_estimator,ys_con)
            Zhi_trans_xplr = partial(self.Z_PI,1.,negative_gp_estimator,-1*ys_con)
            target_func_xploit = partial(self.two_sided_cdf,Zlo_trans_xploit,Zhi_trans_xploit,4.) 
            target_func_xplr = partial(self.two_sided_cdf,Zlo_trans_xplr,Zhi_trans_xplr,4.) 
            xplr_acq_factors[y_key] = target_func_xplr 
            xploit_acq_factors[y_key] = target_func_xploit 
            estimators[y_key] = gp_estimator

        for y_key,ys_range in self.ys_range_constraints.items():
            ys_vector = self.ys_df.loc[:,y_key]
            gp_estimator = partial(self.gp_stats,ys_vector)
            negative_gp_estimator = partial(self.gp_stats,-1*ys_vector)
            # weight range constraints by a product of two error functions, one at each boundary
            # for the lower bound, use the bound as the incumbent_value to encourage sampling above it
            Zlo_trans = partial(self.Z_PI,0.,gp_estimator,ys_range[0])
            # for the higher bound, use the negative of the bound as incumbent
            Zhi_trans = partial(self.Z_PI,0.,negative_gp_estimator,-1*ys_range[1])
            range_func = partial(self.two_sided_cdf,Zlo_trans,Zhi_trans,1.) 
            xplr_acq_factors[y_key] = range_func
            xploit_acq_factors[y_key] = range_func
            estimators[y_key] = gp_estimator

        for y_key,y_cat in self.categorical_constraints.items():
            y_vector = np.array(self.dataset[y_key])
            if y_cat == 1:
                gp_estimator = partial(self.gp_stats,y_vector)
                y_incumbent = 0.5
            elif y_cat == 0:
                gp_estimator = partial(self.gp_stats,-1*y_vector)
                y_incumbent = -0.5
            else:
                raise ValueError('categorical constraints must be 0 or 1')
            Z_trans = partial(self.Z_PI,0.,gp_estimator,y_incumbent)
            cat_func = partial(self.PI_cdf,Z_trans)
            xplr_acq_factors[y_key] = cat_func
            xploit_acq_factors[y_key] = cat_func
            estimators[y_key] = gp_estimator
            
        # optimize acquisition functions over x, within bounds
        xs_xplr = self.optimize_acq(xplr_acq_factors.values())
        xs_xploit = self.optimize_acq(xploit_acq_factors.values()) 

        # inverse-transform the resolved candidates, save as recipes
        x_xplr = self.x_scaler.inverse_transform(xs_xplr.reshape(1,-1))[0]
        x_xploit = self.x_scaler.inverse_transform(xs_xploit.reshape(1,-1))[0]
        cand_xplr = dict([(xk,xval) for xk,xval in zip(self.xs_df.columns,x_xplr)])
        cand_xploit = dict([(xk,xval) for xk,xval in zip(self.xs_df.columns,x_xploit)])
        self.exploration_candidate = cand_xplr
        self.exploitation_candidate = cand_xploit 

    def optimize_acq(self,funcs):
        if self.verbose: 
            self.message_callback('starting {} MC iterations at alpha={}'.format(self.MC_max_iter,self.MC_alpha))
        # start with a random value
        x_best = np.array([np.random.rand(1)[0] for xkey in self.x_domain.keys()])
        obj_best = np.product([f(x_best) for f in funcs])
        x_current = x_best
        obj_current = obj_best
        n_acc = 0
        for iit in range(1,self.MC_max_iter+1):
            # apply a random change
            delta_x = self.MC_alpha*np.array([np.random.rand(1)[0]-0.5 for xx in x_current])
            x_new = x_current + delta_x 
            # if it violates the domain, reject
            if any([xn<0. or xn>1. for xn in x_new]):
                obj_new = 0.
                #print('DOMAIN VIOLATION: REJECT')
            else:
                # evaluate the objective
                obj_new = np.product([f(x_new) for f in funcs])
                # if the objective goes up, keep it
                if (obj_new > obj_current):
                    #print('IMPROVEMENT: {} --> {}'.format(obj_current,obj_new))
                    x_current = x_new
                    obj_current = obj_new
                    n_acc += 1
                    # if this is the best yet, save it
                    if (obj_new > obj_best):
                        #print('*** NEW BEST: {} --> {}'.format(obj_best,obj_new))
                        x_best = x_new 
                        obj_best = obj_new 
                else:
                    # if the objective goes down, make a stochastic decision
                    bdry = np.random.rand(1)[0]
                    #print('PROPOSAL: {} --> {}'.format(obj_current,obj_new))
                    if (obj_new/obj_current > bdry):
                        #print('ACCEPTED: {} > {}'.format(obj_new/obj_current,bdry))
                        x_current = x_new
                        obj_current = obj_new
                        n_acc += 1

            if np.mod(iit,100) == 0:
                # check the acceptance ratio
                ac_ratio = float(n_acc)/iit
                if self.verbose:
                    self.message_callback('iter {}/{}: acceptance ratio: {}'.format(
                    iit,self.MC_max_iter,ac_ratio))

        return x_best

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
