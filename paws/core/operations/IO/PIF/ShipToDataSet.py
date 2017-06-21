import os

from pypif import pif

from ...Operation import Operation
from ... import optools
        
class ShipToDataSet(Operation):
    """
    Take a pypif.obj.System object and ship it to a given Citrination data set.    
    """

    def __init__(self):
        input_names = ['pif','client','dsid','json_path','json_flag','ship_flag']
        output_names = ['response']
        super(ShipToDataSet,self).__init__(input_names,output_names)
        self.input_doc['pif'] = 'A pypif.obj.System object'
        self.input_doc['client'] = 'A working Citrination client' 
        self.input_doc['dsid'] = 'Data set ID where the pif will be stored on Citrination' 
        self.input_doc['json_path'] = 'Filesystem path where the json of the pif will be saved' 
        self.input_doc['json_flag'] = 'Flag for whether or not to save the pif as json' 
        self.input_doc['ship_flag'] = 'Flag for actually shipping the pif' 
        self.output_doc['response'] = 'The Citrination server response to the shipment'
        self.input_src['pif'] = optools.wf_input
        self.input_src['client'] = optools.plugin_input
        self.input_src['dsid'] = optools.wf_input
        self.input_src['json_path'] = optools.fs_input
        self.input_src['json_flag'] = optools.text_input
        self.input_src['ship_flag'] = optools.text_input
        self.input_type['pif'] = optools.ref_type
        self.input_type['client'] = optools.ref_type
        self.input_type['dsid'] = optools.ref_type
        self.input_type['json_path'] = optools.path_type
        self.input_type['json_flag'] = optools.bool_type
        self.input_type['ship_flag'] = optools.bool_type
        self.inputs['ship_flag'] = False
        self.inputs['json_flag'] = False

    def run(self):
        cl = self.inputs['client'] 
        dsid = self.inputs['dsid'] 
        p = self.inputs['pif']        
        json_path = self.inputs['json_path']
        json_flag = self.inputs['json_flag']
        ship_flag = self.inputs['ship_flag']
        try:
            json_file = json_path+'/'+p.uid+'.json'
            # make p an array of pifs to get a big json that has all records
            pif.dump(p, open(json_file,'w'))
            if ship_flag:
                r = cl.upload_file(json_file,data_set_id = dsid)
            else:
                r = 'dry run: no shipment occurred. pif object: {}'.format(pif.dumps(p))
            if not json_flag:
                os.remove(json_file) 
        except Exception as ex:
            r = 'An error occurred while shipping. Error message: {}'.format(ex.message)
        self.outputs['response'] = r


