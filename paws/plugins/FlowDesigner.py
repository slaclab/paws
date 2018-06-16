from __future__ import print_function
from collections import OrderedDict
import os
import copy

from citrination_client.models.design import Target,constraints 

from .PawsPlugin import PawsPlugin

inputs = OrderedDict(
    citrination_client=None,
    dataview_id=None,
    targets={},
    verbose=False)

class FlowDesigner(PawsPlugin):

    def __init__(self):
        super(FlowDesigner,self).__init__(inputs)
        self.thread_blocking = False
        self.input_doc['citrination_client'] = 'A running CitrinationClient plugin'
        self.input_doc['dataview_id'] = 'integer id of the data view to query' 
        self.input_doc['targets'] = 'dict of property names and target values' 
        self.input_doc['verbose'] = 'If True, plugin uses its message_callback' 

    def description(self):
        desc = 'FlowDesigner Plugin: '\
            'Queries a data view on Citrination '\
            'to predict the flow rates needed for '\
            'a FlowReactor Plugin to achieve a target.'
        return desc

    def start(self):
        pass
        #vb = self.inputs['verbose'] 
        #tgts = self.inputs['targets']

    def set_target(self,output_name,target_value):
        self.inputs['targets'][output_name] = value

    def get_recipe(self):
        cc = self.inputs['citrination_client']
        dvid = self.inputs['dataview_id']
        #tgt = Target('Property pop0_site0_r0')
        tgt = Target('Property pop0_site0_sigma','Min')
        cnts = []
        cnts.append(constraints.RealValueConstraint('Property pop0_site0_r0',30))
        #cc.submit_design_run(data_view_id, num_candidates (int in [1,20]), effort (int in [1,30]), target=None, constraints=[], sampler='Default') 
        cc.client.submit_design_run(dvid,1,20,tgt,cnts) 



