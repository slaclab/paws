from collections import OrderedDict
import copy

from citrination_client import *
#from citrination_client.search.pif.query.pif_system_returning_query import PifSystemReturningQuery

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

inputs=OrderedDict(
    client=None,
    dataset_id=None,
    experiment_id=None,
    workflow=None,
    pif_input_name=None,
    extra_input_names=[],
    extra_inputs=[])
outputs=OrderedDict(
    batch_inputs=None,
    batch_outputs=None)

class CitrinationBatch(Operation):
    """Process a batch of PIF objects from a Citrination dataset."""

    def __init__(self):
        super(CitrinationBatch,self).__init__(inputs,outputs)
        self.input_doc['client'] = 'a Citrination client'
        self.input_doc['dataset_id'] = 'the (integer) dataset id to be fetched'
        self.input_doc['experiment_id'] = 'only records with this EXPERIMENT_ID will be returned'
        self.input_doc['workflow'] = 'the workflow to be executed'
        self.input_doc['pif_input_name'] = 'the workflow input name '\
            'to be used for passing the PIF objects into the workflow'
        self.input_doc['extra_input_names'] = 'list of names '\
            'of workflow inputs to be set to extra_inputs before batch-execution'
        self.input_doc['extra_inputs'] = 'data items '\
            'to be set to workflow inputs indicated by extra_input_names'
        self.output_doc['batch_inputs'] = 'list of dicts of [input_name:input_value]'
        self.output_doc['batch_outputs'] = 'list of dicts of [output_name:output_value] for all Workflow outputs'
        self.input_type['workflow'] = opmod.entire_workflow
        
    def run(self):
        c = self.inputs['client']
        dsid = self.inputs['dataset_id']
        expt_id = self.inputs['experiment_id']

        if expt_id is not None:
            query = self.dsid_query_with_expt_id(dsid,expt_id)
        else:
            query = self.dsid_query(dsid)

        all_hits = []
        n_hits = 0
        self.message_callback('Finding records... ')
        current_result = c.search(query)
        while current_result.hits is not None:
            all_hits.extend(current_result.hits)
            n_current_hits = len(current_result.hits)
            n_hits += n_current_hits
            query.from_index += n_current_hits 
            self.message_callback('{} found ... '.format(n_hits))
            current_result = c.search(query)
        self.message_callback('Found {} records.'.format(n_hits))

        pifs = [x.system for x in all_hits]
        n_batch = len(pifs)
        
        wf = self.inputs['workflow'] 
        inpname = self.inputs['pif_input_name'] 
        self.outputs['batch_inputs'] = [None for ib in range(n_batch)] 
        self.outputs['batch_outputs'] = [None for ib in range(n_batch)] 
        if self.data_callback: 
            self.data_callback('outputs.batch_inputs',[None for ib in range(n_batch)])
            self.data_callback('outputs.batch_outputs',[None for ib in range(n_batch)])
        inps = self.inputs['extra_input_names']
        vals = self.inputs['extra_inputs']
        # Load any additional inputs...
        if any(inps): 
            for inpnm,inpval in zip(inps,vals):
                wf.set_wf_input(inpnm,inpval)

        self.message_callback('STARTING BATCH')
        for i,pif in zip(range(n_batch),pifs):
            inp_dict = OrderedDict() 
            inp_dict[inpname] = pif 
            wf.set_wf_input(inpname,pif)
            self.message_callback('BATCH RUN {} / {}'.format(i,n_batch-1))
            wf.execute()
            out_dict = wf.wf_outputs_dict()
            self.outputs['batch_inputs'][i] = inp_dict
            self.outputs['batch_outputs'][i] = out_dict
            if self.data_callback: 
                self.data_callback('outputs.batch_inputs.'+str(i),inp_dict)
                self.data_callback('outputs.batch_outputs.'+str(i),copy.deepcopy(out_dict))
        self.message_callback('BATCH FINISHED')

    def dsid_query_with_expt_id(self,dsid,expt_id):
        query = PifSystemReturningQuery(
            from_index=0,
            size=100,
            query=DataQuery(
                dataset=DatasetQuery(
                    id=Filter(
                        equal=dsid)),    
                system=PifSystemQuery(
                    ids=IdQuery(
                        name=FieldQuery(
                            filter=Filter(
                                equal='EXPERIMENT_ID')),
                        value=FieldQuery(
                            filter=Filter(
                                equal=expt_id))))))
        return query

    def dsid_query(self,dsid):
        query = PifSystemReturningQuery(
            from_index=0,
            size=100,
            query=DataQuery(
                dataset=DatasetQuery(
                    id=Filter(
                        equal=dsid))))
        return query


