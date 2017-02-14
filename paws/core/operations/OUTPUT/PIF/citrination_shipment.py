import os

from pypif import pif
from citrination_client import CitrinationClient 

from ...operation import Operation
from ... import optools
        
# TODO: Note that the entire data set can be one json,
# of an array of pif records, and this will lead to a faster upload.

class CreateDataSet(Operation):
    """
    Take a Citrination client as input and use it to create a data set.
    Output the index of the created data set.
    """

    def __init__(self):
        input_names = ['client','name','description','share']
        output_names = ['ok_flag','dsid']
        super(CreateDataSet,self).__init__(input_names,output_names)
        self.input_doc['client'] = 'A reference to a running Citrination client.'
        self.input_doc['name'] = 'Name for the new data set.'
        self.input_doc['description'] = 'Description for the new data set.'
        self.input_doc['share'] = 'Flag whether or not dataset should be shared with all users on the instance.'
        self.output_doc['ok_flag'] = 'Indicator of whether or not the data set was created successfully.'
        self.output_doc['dsid'] = 'The index of the new data set, if created successfully.'
        self.input_src['client'] = optools.plugin_input
        self.input_src['name'] = optools.text_input
        self.input_src['description'] = optools.text_input
        self.input_src['share'] = optools.text_input
        self.input_type['client'] = optools.ref_type
        self.input_type['name'] = optools.str_type
        self.input_type['description'] = optools.str_type
        self.input_type['share'] = optools.bool_type
        self.inputs['description'] = 'New Citrination data set'
        self.inputs['share'] = False

    def run(self):
        c = self.inputs['client']
        f = True
        try:
            r = c.create_data_set()
            #if 'dataset' in r.keys():
            #    s = 'client successfully queried data set {}.'.format(dsid)
            #    f = True
            #else:
            #    s = 'client queried data set {} but found no dataset in response dict: Response: {}'.format(dsid,r)
            #    f = True
        except Exception as ex:
            s = 'client failed to create data set. Error message: {}'.format(ex.message)
            f = False
        self.outputs['ok_flag'] = f
        self.outputs['dsid'] = -1 

class CheckDataSet(Operation):
    """
    Take a Citrination client as input and use it to query a data set.
    Output some indication of whether or not the query was successful.
    """
    
    def __init__(self):
        input_names = ['client','dsid']
        output_names = ['ok_flag','status']
        super(CheckDataSet,self).__init__(input_names,output_names)
        self.input_doc['client'] = 'A reference to a running Citrination client.'
        self.input_doc['dsid'] = 'The data set to be queried.'
        self.output_doc['ok_flag'] = 'Indicator of whether or not the data set passes the test.'
        self.output_doc['status'] = 'Message describing the state of the data set.'
        self.input_src['client'] = optools.plugin_input
        self.input_src['dsid'] = optools.text_input
        self.input_type['dsid'] = optools.int_type

    def run(self):
        c = self.inputs['client']
        dsid = self.inputs['dsid'] 
        f = True
        try:
            r = c.get_dataset_files(dsid)
            if 'dataset' in r.keys():
                s = 'client successfully queried data set {}.'.format(dsid)
                f = True
            else:
                s = 'client queried data set {} but found no dataset in response dict: Response: {}'.format(dsid,r)
                f = True
        except Exception as ex:
            s = 'client failed to query data set number {}. Error message: {}'.format(dsid,ex.message)
            f = False
        self.outputs['ok_flag'] = f
        self.outputs['status'] = s

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


class ShipJSON(Operation):
    """
    Take a .json file containing a pif, and ship the pif to a given Citrination data set.    
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

