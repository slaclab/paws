from collections import OrderedDict
import os

from pypif import pif
import pypif.obj as pifobj 

from ...Operation import Operation

inputs=OrderedDict(
    pif=None,
    client_plugin=None,
    dsid=None,
    json_dirpath=None,
    json_filename=None,
    keep_json=False,
    ship_flag=False)
outputs=OrderedDict(response=None)
        
class ShipToDataSet(Operation):
    """
    Take a pypif.obj.System object and ship it to a given Citrination data set.    
    """

    def __init__(self):
        super(ShipToDataSet,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'A pypif.obj.System object or an array/list thereof'
        self.input_doc['client_plugin'] = 'A running CitrinationClient(PawsPlugin)' 
        self.input_doc['dsid'] = 'Data set ID where the pif record(s) will be stored on Citrination' 
        self.input_doc['json_dirpath'] = 'Filesystem path where a json file of the pif(s) will be saved' 
        self.input_doc['json_filename'] = 'Name of the .json file where the pif(s) will be saved' 
        self.input_doc['keep_json'] = 'Flag for whether or not to keep the json file' 
        self.input_doc['ship_flag'] = 'Flag for shipping the pif- set to False for a dry run' 
        self.output_doc['response'] = 'The Citrination server response to the shipment'

    def run(self):
        cl_pgn = self.inputs['client_plugin'] 
        dsid = self.inputs['dsid'] 
        p = self.inputs['pif']        
        json_dir = self.inputs['json_dirpath']
        json_file = self.inputs['json_filename']
        if not os.path.splitext(json_file)[1] == 'json':
            json_file = json_file+'.json'
        json_file = os.path.join(json_dir,json_file)

        json_flag = self.inputs['keep_json']
        ship_flag = self.inputs['ship_flag']
        self.message_callback('dumping PIF data to {}'.format(json_file))
        pif.dump(p, open(json_file,'w'))
        if ship_flag:
            self.message_callback('Uploading {} to dataset {}'.format(json_file,dsid))
            r = cl_pgn.client.upload_file(json_file,dataset_id = dsid)
        else:
            r = 'dry run: no shipment occurred.'
        if not json_flag:
            self.message_callback('Removing {}'.format(json_file))
            os.remove(json_file) 
        self.outputs['response'] = r


