from __future__ import print_function
from collections import OrderedDict
import os
import copy
import time

from citrination_client.models.design import Target,constraints 

from .PawsPlugin import PawsPlugin

inputs = OrderedDict(
    citrination_client=None,
    dataview_id=None,
    target=None,
    constraints={},
    range_constraints={},
    n_candidates=2,
    design_effort=2)

class FlowDesigner(PawsPlugin):

    def __init__(self):
        super(FlowDesigner,self).__init__(inputs)
        self.thread_blocking = False
        self.input_doc['citrination_client'] = 'A running CitrinationClient plugin'
        self.input_doc['dataview_id'] = 'integer id of the data view to query' 
        self.input_doc['target'] = 'property name to minimize' 
        self.input_doc['constraints'] = 'dict of property names and target values' 
        self.input_doc['range_constraints'] = 'dict of property names and list of [min,max] values' 
        self.input_doc['n_candidates'] = 'number of design candidates to request per iteration' 
        self.input_doc['design_effort'] = 'how hard to try to meet the targets (int from 1 to 30)' 
        self.target = self.inputs['target']
        self.constraints = self.inputs['constraints']
        self.range_constraints = self.inputs['range_constraints']
        self.candidates = []
        self.bg_candidates = []
        self.recipe_list = [] 
        self.bg_recipe_list = [] 
        self.bg_designer = BgDesigner(self)

    def description(self):
        desc = 'FlowDesigner Plugin: '\
            'Queries a data view on Citrination '\
            'to predict the flow rates needed for '\
            'a FlowReactor Plugin to achieve a target.'
        return desc

    def start(self):
        super(FlowDesigner,self).start() 

    #def set_target(self,property_name):
    #    self.target = property_name

    #def set_constraint(self,property_name,target_value):
    #    self.constraints[property_name] = value

    #def set_range_constraint(self,property_name,min_value,max_value):
    #    self.range_constraints[property_name] = [min_value,max_value]

    def get_candidate_recipes(self):
        cc = self.inputs['citrination_client']
        dvid = self.inputs['dataview_id']
        tgt = Target(self.inputs['target'],'Min')
        straints = []
        n_candidates = self.inputs['n_candidates'] 
        design_effort = self.inputs['design_effort'] 
        for prop_name, val in self.inputs['constraints'].items():
            straints.append(constraints.RealValueConstraint(prop_name,val))
        for prop_name, lmts in self.inputs['range_constraints'].items():
            straints.append(constraints.RealRangeConstraint(prop_name,lmts[0],lmts[1]))
        #cc.submit_design_run(
            # data_view_id,
            # num_candidates (int in [1,20]),
            # effort (int in [1,30]),
            # target=None, constraints=[],
            # sampler='Default') 
        des = cc.client.submit_design_run(dvid,n_candidates,design_effort,tgt,straints) 
        fin = False
        while not fin:
            time.sleep(2)
            stat = cc.client.get_design_run_status(dvid, des.uuid)
            self.message_callback('design finished: {}'.format(stat.finished()))
            self.message_callback('design status: {}/100'.format(stat.progress))
            if int(stat.progress) == 100:
                fin = True
        desres = cc.client.get_design_run_results(dvid,des.uuid)
        # TODO: add settings to dictate sampling of next_experiments, best_materials
        #for expt in desres.next_experiments:
        for expt in desres.next_experiments+desres.best_materials:
            rcp = {}
            rcp['T_set'] = float(expt['descriptor_values']['Property T_set']) 
            rcp['T_ramp'] = 30.
            rcp['flowrate'] = float(expt['descriptor_values']['Property flowrate'])
            rcp['solvent'] = 'Pd_TOP' 
            vol_frac = {}
            vol_frac['TOP'] = float(expt['descriptor_values']['Property TOP_fraction'])  
            vol_frac['oleylamine'] = float(expt['descriptor_values']['Property oleylamine_fraction'])  
            vol_frac['ODE'] = 0.
            rcp['reagent_volume_fractions'] = vol_frac
            bg_rcp = {}
            bg_rcp['T_set'] = float(expt['descriptor_values']['Property T_set']) 
            bg_rcp['T_ramp'] = 30.
            bg_rcp['flowrate'] = float(expt['descriptor_values']['Property flowrate'])
            bg_rcp['solvent'] = 'Pd_TOP' 
            bg_vol_frac = {}
            bg_vol_frac['TOP'] = float(expt['descriptor_values']['Property TOP_fraction'])  
            bg_vol_frac['oleylamine'] = float(expt['descriptor_values']['Property oleylamine_fraction'])  
            bg_vol_frac['ODE'] = 1.-bg_vol_frac['oleylamine']-bg_vol_frac['TOP']
            bg_rcp['reagent_volume_fractions'] = bg_vol_frac
            self.candidates.append(rcp)
            self.bg_candidates.append(bg_rcp)

    def next(self):
        return self.__next__()

    def __next__(self):
        if not any(self.candidates):
            self.get_candidate_recipes()
        rcp = self.candidates.pop(0)
        self.recipe_list.append(rcp)
        return rcp

    def get_plugin_content(self):
        c = super(FlowDesigner,self).get_plugin_content()
        c.update(dict(
            recipe_list = self.recipe_list,
            bg_recipe_list = self.bg_recipe_list,
            bg_designer = self.bg_designer))
        return c

class BgDesigner(object):
    
    def __init__(self,flow_designer):
        super(BgDesigner,self).__init__()
        self.flow_designer = flow_designer

    def next(self):
        return self.__next__()

    def __next__(self):
        if len(self.flow_designer.bg_candidates) > len(self.flow_designer.candidates):
            bg_rcp = self.flow_designer.bg_candidates.pop(0)
            self.flow_designer.bg_recipe_list.append(bg_rcp)
            return bg_rcp
        else:
            return None
        #if len(self.recipe_list) < len(self.flow_designer.recipe_list):
        #    rcp_idx = len(self.recipe_list)
        #    flow_rcp = self.flow_designer.recipe_list[rcp_idx]
        #    bg_rcp = copy.deepcopy(flow_rcp)
        #    oley_frac = flow_rcp['reagent_volume_fractions']['oleylamine']
        #    TOP_frac = flow_rcp['reagent_volume_fractions']['TOP']
        #    bg_rcp['reagent_volume_fractions']['ODE'] = 1.-oley_frac-TOP_frac
        #    self.recipe_list.append(bg_rcp)
        #    return bg_rcp
        #else:
        #    return None
        




