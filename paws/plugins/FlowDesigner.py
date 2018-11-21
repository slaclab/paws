from __future__ import print_function
from collections import OrderedDict
import os
import copy
import time

from citrination_client.models.design import Target,constraints 

from .PawsPlugin import PawsPlugin

content = OrderedDict(
    citrination_client=None,
    dataview_id=None,
    target=None,
    target_goal='Min',
    constraints={},
    range_constraints={},
    n_candidates=2,
    design_effort=2)

class FlowDesigner(PawsPlugin):

    def __init__(self):
        super(FlowDesigner,self).__init__(content)
        self.thread_blocking = False
        self.content_doc['citrination_client'] = 'A running CitrinationClient plugin'
        self.content_doc['dataview_id'] = 'integer id of the data view to query' 
        self.content_doc['target'] = 'property name to optimize' 
        self.content_doc['target_goal'] = 'Min or Max, depending on target optimization goals' 
        self.content_doc['constraints'] = 'dict of property names and target values' 
        self.content_doc['range_constraints'] = 'dict of property names and list of [min,max] values' 
        self.content_doc['n_candidates'] = 'number of design candidates to request per iteration' 
        self.content_doc['design_effort'] = 'how hard to try to meet the targets (int from 1 to 30)' 
        self.best_materials = []
        self.next_experiments = []

    def description(self):
        desc = 'FlowDesigner Plugin: '\
            'Queries a data view on Citrination '\
            'to predict the flow rates needed for '\
            'a FlowReactor Plugin to achieve a target.'
        return desc

    def start(self):
        super(FlowDesigner,self).start() 

    def set_design_goal(self,design_goal):
        self.content['target']=design_goal['target']
        self.content['target_goal']=design_goal['target_goal']
        self.content['constraints']=design_goal['constraints']
        self.content['range_constraints']=design_goal['range_constraints']

    def get_candidate_recipes(self):
        cc = self.content['citrination_client']
        dvid = self.content['dataview_id']
        tgt = Target(self.content['target'],self.content['target_goal'])
        straints = []
        n_candidates = self.content['n_candidates'] 
        design_effort = self.content['design_effort'] 
        for prop_name, val in self.content['constraints'].items():
            straints.append(constraints.RealValueConstraint(prop_name,val))
        for prop_name, lmts in self.content['range_constraints'].items():
            straints.append(constraints.RealRangeConstraint(prop_name,lmts[0],lmts[1]))
        #DOC: cc.submit_design_run(
        #       data_view_id,
        #       num_candidates (int in [1,20]),
        #       effort (int in [1,30]),
        #       target=None, constraints=[],
        #       sampler='Default') 
        msg = 'Designing for: \nTarget: {} \nConstraints: {} \nRange constraints: {}'.format(
            self.content['target'],self.content['constraints'],self.content['range_constraints'])
        self.message_callback(msg)
        try_again = True
        while try_again:
            try:
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
                try_again = False 
            except:
                pass
        self.best_materials = desres.best_materials
        self.next_experiments = desres.next_experiments

