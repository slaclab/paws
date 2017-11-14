from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_fit

inputs = OrderedDict(
    q_I=None,
    flags=None,
    params=None,
    step_size=0.01,
    nsteps_burn=1000,
    nsteps_anneal=1000,
    nsteps_quench=1000,
    T_anneal=0.2,
    T_burn=0.3)
outputs = OrderedDict(
    best_params=None,
    final_params=None,
    report=None)

class SpectrumMCAnneal(Operation):
    """Anneal SAXS fitting parameters by Metropolis-Hastings Monte Carlo.

    This Operation explores the space 
    of parameters for a SAXS intensity equation,
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
        self.input_doc['step_size'] = 'random walk fractional step size'
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
        self.output_doc['report'] = 'dict reporting '\
            'the number of steps and reject ratio'
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.input_type['params'] = opmod.workflow_item

    def run(self):
        q_I = self.inputs['q_I']
        flg = self.inputs['flags']
        par = self.inputs['params']
        stepsz = self.inputs['step_size']
        ns_burn = self.inputs['nsteps_burn']
        ns_anneal = self.inputs['nsteps_anneal']
        ns_quench = self.inputs['nsteps_quench']
        T_burn = self.inputs['T_burn']
        T_anneal = self.inputs['T_anneal']

        if not flg['bad_data'] and not flg['diffraction_peaks']:
            p_best,p_fin,rpt_burn = saxs_fit.MC_anneal_fit(q_I,flg,par,stepsz,ns_burn,T_burn)
            if self.message_callback:
                self.message_callback('finished burn. \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
                .format(rpt_burn['objective_init'],
                    rpt_burn['objective_best'],
                    rpt_burn['objective_final'],
                    rpt_burn['reject_ratio']))
            p_best,p_fin,rpt_anneal = saxs_fit.MC_anneal_fit(q_I,flg,p_best,stepsz,ns_anneal,T_anneal)
            if self.message_callback:
                self.message_callback('finished anneal. \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
                .format(rpt_anneal['objective_init'],
                    rpt_anneal['objective_best'],
                    rpt_anneal['objective_final'],
                    rpt_anneal['reject_ratio']))
            p_best,p_fin,rpt_quench = saxs_fit.MC_anneal_fit(q_I,flg,p_best,stepsz,ns_quench,0.)
            if self.message_callback:
                self.message_callback('finished quench. \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
                .format(rpt_quench['objective_init'],
                    rpt_quench['objective_best'],
                    rpt_quench['objective_final'],
                    rpt_quench['reject_ratio']))
            self.outputs['best_params'] = p_best 
            self.outputs['final_params'] = p_fin 
            rpt = OrderedDict(
                objective_init = rpt_burn['objective_init'],
                objective_best = rpt_quench['objective_best'],
                objective_final = rpt_quench['objective_final'],
                reject_ratio = rpt_anneal['reject_ratio'])
            self.outputs['report'] = rpt 

