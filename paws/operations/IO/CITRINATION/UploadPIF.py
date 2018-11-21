from collections import OrderedDict
import os

from pypif import pif
import pypif.obj as pifobj 

from ...Operation import Operation

inputs=OrderedDict(
    pif=None,
    citrination_client=None,
    dsid=None,
    json_path=None,
    keep_json=False,
    upload_flag=False)
outputs=OrderedDict(response=None)
        
class UploadPIF(Operation):
    """
    Take a pypif.obj.System object and upload it to a given Citrination data set.    
    """

    def __init__(self):
        super(UploadPIF,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'A pypif.obj.System object or an array/list thereof'
        self.input_doc['citrination_client'] = 'A running CitrinationClient(PawsPlugin)' 
        self.input_doc['dsid'] = 'Data set ID where the pif record(s) will be stored on Citrination' 
        self.input_doc['json_path'] = 'Path where pif(s) will be saved' 
        self.input_doc['keep_json'] = 'Flag for whether or not to keep the json file' 
        self.input_doc['upload_flag'] = 'Flag for upload- set to False for a dry run' 
        self.output_doc['response'] = 'The Citrination server response to the upload'

    def run(self):
        cl_pgn = self.inputs['citrination_client'] 
        dsid = self.inputs['dsid'] 
        p = self.inputs['pif']        
        jsp = self.inputs['json_path']
        if not os.path.splitext(jsp)[1] in ['.json','.JSON']:
            jsp = jsp+'.json'
        jsfnm = os.path.split(jsp)[1]
        self.message_callback('PIF dump file: {}'.format(jsp))
        pif.dump(p, open(jsp,'w'))
        if self.inputs['upload_flag']:
            self.message_callback('Uploading {} to dataset {}'.format(jsp,dsid))
            try:
                r = cl_pgn.client.upload(dsid,jsp,jsfnm)
            except:
                r = 'An error occurred during upload- aborting'
                self.message_callback(r)
        else:
            r = 'upload_flag is set to False- no upload occurred'
            self.message_callback(r)
        if not self.inputs['keep_json']:
            self.message_callback('Removing {}'.format(jsp))
            os.remove(jsp) 
        self.outputs['response'] = r


