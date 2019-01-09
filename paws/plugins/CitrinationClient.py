from __future__ import print_function
from collections import OrderedDict
import os

from pypif import pif
from citrination_client import CitrinationClient as CitCli
from citrination_client import PifSystemReturningQuery, PifSystemQuery, DataQuery, DatasetQuery, IdQuery, FieldQuery, Filter

from .PawsPlugin import PawsPlugin

content = OrderedDict(
    address=None,
    api_key_file=None)

class CitrinationClient(PawsPlugin):
    """PAWS Plugin wrapping a Citrination client"""

    def __init__(self):
        super(CitrinationClient,self).__init__(content)
        self.content_doc['address'] = 'web address of citrination instance'
        self.content_doc['api_key_file'] = 'path to a file in the local filesystem containing a valid citrination api key'
        self.client=None

    def start(self):
        super(CitrinationClient,self).start()
        self.address = self.content['address'] 
        f = open(self.content['api_key_file'],'r')
        self.api_key = str(f.readline()).strip()
        f.close()
        self.client = CitCli(self.api_key,self.address)

    def stop(self):
        self.client = None

    def upload_pif(self,pif_object,dataset_id,json_path,keep_json=True,upload=True):
        """Upload a PIF to Citrination.

        Parameters
        ----------
        pif_object : object
            A pypif.obj.System object or an array/list thereof
        dataset_id : int
            Integer dataset id where the pif(s) will be uploaded 
        json_path : str
            Path on local filesystem where PIF json data will be dumped
        keep_json : bool
            Flag for whether or not to keep the json dump file 
        upload : False
            Flag for whether or not to perform upload- set to False for a dry run

        Returns
        -------
        resp : str
            Response from the Citrination server.
        """
        if not os.path.splitext(json_path)[1] in ['.json','.JSON']:
            json_path = json_path+'.json'
        jsfnm = os.path.split(json_path)[1]
        self.message_callback('PIF dump file: {}'.format(json_path))
        pif.dump(pif_object, open(json_path,'w'))
        if upload:
            self.message_callback('Uploading {} to dataset {}'.format(json_path,dataset_id))
            try:
                resp = self.client.upload(dataset_id,json_path,jsfnm)
            except:
                resp = 'An error occurred during upload- aborting'
                self.message_callback(resp)
                raise
        else:
            resp = 'upload flag is set to False- no upload occurred'
            self.message_callback(resp)
        if not keep_json:
            self.message_callback('Removing {}'.format(json_path))
            os.remove(json_path) 
        return resp

    def download_pifs(dataset_id,experiment_id=None):
        """Download PIFs from Citrination.

        Parameters
        ----------
        dataset_id : int
            Integer dataset id from where the pif(s) will be downloaded 
        experiment_id : str 
            Optional string for filtering pifs on their experiment_id attributes 
        
        Returns
        -------
        pifs : object
            One or more pypif.obj.System objects
        """
        if experiment_id is not None:
            query = self.dsid_query_with_expt_id(dataset_id,experiment_id)
        else:
            query = self.dsid_query(dataset_id)
        all_hits = []
        n_hits = 0
        self.message_callback('Querying Citrination for records.')
        current_result = self.client.search(query)
        while current_result.hits is not None:
            all_hits.extend(current_result.hits)
            n_current_hits = len(current_result.hits)
            n_hits += n_current_hits
            query.from_index += n_current_hits 
            current_result = self.client.search(query)
        self.message_callback('Found {} records.'.format(n_hits))
        pifs = [x.system for x in all_hits]
        return pifs 
