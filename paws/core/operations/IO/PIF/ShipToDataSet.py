import os

from pypif import pif
import pypif.obj as pifobj 

from ... import Operation as op
from ...Operation import Operation
        
class ShipToDataSet(Operation):
    """
    Take a pypif.obj.System object and ship it to a given Citrination data set.    
    """

    def __init__(self):
        input_names = ['pif','client','dsid','json_path','keep_json','ship_flag']
        output_names = ['response']
        super(ShipToDataSet,self).__init__(input_names,output_names)
        self.input_doc['pif'] = 'A pypif.obj.System object or an array/list thereof'
        self.input_doc['client'] = 'A running Citrination client' 
        self.input_doc['dsid'] = 'Data set ID where the pif record(s) will be stored on Citrination' 
        self.input_doc['json_path'] = 'Filesystem path where the json of the pif(s) will be saved' 
        self.input_doc['keep_json'] = 'Flag for whether or not to keep the json file' 
        self.input_doc['ship_flag'] = 'Flag for shipping the pif- set to False for a dry run' 
        self.output_doc['response'] = 'The Citrination server response to the shipment'
        self.input_src['pif'] = op.wf_input
        self.input_src['client'] = op.plugin_input
        self.input_src['dsid'] = op.text_input
        self.input_src['json_path'] = op.fs_input
        self.input_src['keep_json'] = op.text_input
        self.input_src['ship_flag'] = op.text_input
        self.input_type['pif'] = op.ref_type
        self.input_type['client'] = op.ref_type
        self.input_type['dsid'] = op.int_type
        self.input_type['json_path'] = op.path_type
        self.input_type['keep_json'] = op.bool_type
        self.input_type['ship_flag'] = op.bool_type
        self.inputs['ship_flag'] = False
        self.inputs['keep_json'] = False

    def run(self):
        cl = self.inputs['client'] 
        dsid = self.inputs['dsid'] 
        p = self.inputs['pif']        
        json_path = self.inputs['json_path']
        json_flag = self.inputs['keep_json']
        ship_flag = self.inputs['ship_flag']
        try:
            if isinstance(p,pifobj.ChemicalSystem):
                json_file = json_path+'/'+p.uid+'.json'
            else:
                json_file = json_path+'/pif_tmp.json'
            # make p an array of pifs to get a big json that has all records
            pif.dump(p, open(json_file,'w'))
            if ship_flag:
                r = cl.upload_file(json_file,dataset_id = dsid)
            else:
                r = 'dry run: no shipment occurred. pif object: {}'.format(pif.dumps(p))
            if not json_flag:
                os.remove(json_file) 
        except Exception as ex:
            r = 'An error occurred while shipping. Error message: {}'.format(ex.message)
        self.outputs['response'] = r


