from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_fit

inputs = OrderedDict(
    q_I=None,
    flags=None,
    params=None,
    step_size=0.1,
    nsteps_burn=1000,
    nsteps_anneal=1000,
    nsteps_quench=1000,
    T_anneal=0.1,
    T_burn=0.2)
outputs = OrderedDict(
    best_params=None,
    final_params=None,
    report=None)

class SpectrumMCAnneal(Operation):
    """Anneal SAXS fitting parameters by Metropolis-Hastings Monte Carlo.

    This Operation seeks a globally optimal fit 
    for the parameters of a SAXS equation,
    given some measured data.
    It is useful for refining optimizations 
    that tend to get stuck in local minima.
    """

    def __init__(self):
        super(SpectrumMCAnneal, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of measured data: '\
            'intensity (arb) with respect to scattering vector (1/Angstrom)'
        self.input_doc['flags'] = 'dict of flags '\
            'indicating which populations to fit'
        self.input_doc['params'] = 'dict of initial values '\
            'for the scattering equation parameters '
        self.input_doc['step_size'] = 'random walk step size, '\
            'as a fraction of intial params' 
        self.input_doc['nsteps_burn'] = 'number of iterations '\
            'to perform in the initial burn-off phase' 
        self.input_doc['nsteps_anneal'] = 'number of iterations '\
            'to perform in the annealing phase' 
        self.input_doc['nsteps_quench'] = 'number of iterations '\
            'to perform in the quenching (zero acceptance) phase' 
        
        self.output_doc['best_params'] = 'dict of scattering parameters '\
            'yielding the best fit over all trials'
        self.output_doc['final_params'] = 'dict of scattering parameters '\
            'obtained in the final step of the algorithm'
        self.output_doc['report'] = 'dict expressing the objective function, '\
            'its evaluation at the initial and final points of the fit, '\
            'and the Metropolis rejection ratio'
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.input_type['params'] = opmod.workflow_item

    def run(self):
        q_I = self.inputs['q_I']
        f = self.inputs['flags']
        p = self.inputs['params']
        stepsz = self.inputs['step_size']
        ns_burn = self.inputs['nsteps_burn']
        ns_anneal = self.inputs['nsteps_anneal']
        ns_quench = self.inputs['nsteps_quench']
        T_burn = self.inputs['T_burn']
        T_anneal = self.inputs['T_anneal']

        print('beginning burn ({} steps)'.format(ns_burn))
        p_best,p_fin,rpt_burn = saxs_fit.MC_anneal_fit(q_I,f,p,stepsz,ns_burn,T_burn)
        print('finished burn. objectives: \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
            .format(rpt_burn['obj_init'],rpt_burn['obj_best'],rpt_burn['obj_final'],rpt_burn['reject_ratio']))

        print('beginning anneal ({} steps)'.format(ns_burn))
        p_best,p_fin,rpt_anneal = saxs_fit.MC_anneal_fit(q_I,f,p_best,stepsz,ns_anneal,T_anneal)
        print('finished anneal. objectives: \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
            .format(rpt_anneal['obj_init'],rpt_anneal['obj_best'],rpt_anneal['obj_final'],rpt_anneal['reject_ratio']))

        print('beginning quench ({} steps)'.format(ns_quench))
        p_best,p_fin,rpt_quench = saxs_fit.MC_anneal_fit(q_I,f,p_best,stepsz,ns_quench,0.)
        print('finished quench. objectives: \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
            .format(rpt_quench['obj_init'],rpt_quench['obj_best'],rpt_quench['obj_final'],rpt_quench['reject_ratio']))

        rpt_quench['burn_reject_ratio'] = rpt_burn['reject_ratio']
        rpt_quench['quench_reject_ratio'] = rpt_quench['reject_ratio']
        rpt_quench['reject_ratio'] = rpt_anneal['reject_ratio']
        self.outputs['best_params'] = p_best 
        self.outputs['final_params'] = p_fin 
        self.outputs['report'] = rpt_quench 

