from collections import OrderedDict
import os

from pypif import pif
import pypif.obj as pifobj 
from citrination_client import PifSystemReturningQuery, PifSystemQuery, DataQuery, DatasetQuery, IdQuery, FieldQuery, Filter

from ...Operation import Operation

inputs=OrderedDict(
    client_plugin=None,
    dsid=None,
    experiment_id=None)
outputs=OrderedDict(pif_list=None)
        
class GetPIFs(Operation):
    """Fetch a list of PIF objects from Citrination"""

    def __init__(self):
        super(GetPIFs,self).__init__(inputs,outputs)
        self.input_doc['client_plugin'] = 'A running CitrinationClient(PawsPlugin)' 
        self.input_doc['dsid'] = 'Citrination data set ID'
        self.input_doc['experiment_id'] = 'EXPERIMENT_ID tag (optional)'
        self.output_doc['pif_list'] = 'List of PIF objects'

    def run(self):
        cl_pgn = self.inputs['client_plugin'] 
        dsid = self.inputs['dsid'] 
        expt_id = self.inputs['experiment_id']

        if expt_id is not None:
            query = self.dsid_query_with_expt_id(dsid,expt_id)
        else:
            query = self.dsid_query(dsid)

        all_hits = []
        n_hits = 0
        self.message_callback('Querying Citrination for records.')
        #import pdb; pdb.set_trace()
        #
        current_result = cl_pgn.client.search(query)
        # TODO: is it wise to use the clone in this way?
        #
        while current_result.hits is not None:
            all_hits.extend(current_result.hits)
            n_current_hits = len(current_result.hits)
            n_hits += n_current_hits
            query.from_index += n_current_hits 
            #self.message_callback('{} found ... '.format(n_hits))
            current_result = cl_pgn.client.search(query)
        self.message_callback('Found {} records.'.format(n_hits))

        pifs = [x.system for x in all_hits]
        self.outputs['pif_list'] = pifs        

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


