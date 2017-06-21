from ...Operation import Operation
from ... import optools
        
class ShipJSON(Operation):
    """
    Take a .json file containing a pif or array of pifs, ship it to a Citrination data set.    
    """

    def __init__(self):
        input_names = ['json_path','client','dsid','ship_flag']
        output_names = ['response']
        super(ShipJSON,self).__init__(input_names,output_names)
        self.input_doc['json_path'] = 'Filesystem path where the json of the pif is saved' 
        self.input_doc['client'] = 'A working Citrination client' 
        self.input_doc['dsid'] = 'Data set ID where the pif will be stored on Citrination' 
        self.input_doc['ship_flag'] = 'Flag for actually shipping the pif' 
        self.output_doc['response'] = 'The Citrination server response to the shipment'
        self.input_src['json_path'] = optools.fs_input
        self.input_src['client'] = optools.plugin_input
        self.input_src['dsid'] = optools.wf_input
        self.input_src['ship_flag'] = optools.text_input
        self.input_type['json_path'] = optools.path_type
        self.input_type['client'] = optools.ref_type
        self.input_type['dsid'] = optools.ref_type
        self.input_type['ship_flag'] = optools.bool_type
        self.inputs['ship_flag'] = False

    def run(self):
        json_path = self.inputs['json_path']
        cl = self.inputs['client'] 
        dsid = self.inputs['dsid'] 
        ship_flag = self.inputs['ship_flag']
        try:
            if ship_flag:
                r = cl.upload_file(json_path,data_set_id = dsid)
            else:
                r = 'dry run: no shipment occurred. json path: {}'.format(json_path)
        except Exception as ex:
            r = 'An error occurred while shipping. Error message: {}'.format(ex.message)
        self.outputs['response'] = r

