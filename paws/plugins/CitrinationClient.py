import os

from pypif import pif
from citrination_client import CitrinationClient as CitCli

from .PawsPlugin import PawsPlugin

class CitrinationClient(PawsPlugin):
    """PAWS Plugin wrapping a Citrination client"""

    def __init__(self,address='',api_key_file='',verbose=False,log_file=''):
        """Create a CitrinationClient.
        
        Parameters
        ----------
        address : str
            web address of citrination instance
        api_key_file : str
            path to a file in the local filesystem containing a valid citrination api key
        verbose : bool
        log_file : str
        """
        super(CitrinationClient,self).__init__(verbose=verbose,log_file=log_file)
        self.address = address
        self.api_key_file = api_key_file
        self.client = None

    def start(self):
        super(CitrinationClient,self).start()
        api_key = str(open(self.api_key_file,'r').readline()).strip()
        self.client = CitCli(api_key,self.address)

    def create_dataset_version(self,dataset_id):
        self.client.create_dataset_version(dataset_id)

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

