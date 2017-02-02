import os

from pypif import pif
from citrination_client import CitrinationClient 

from ...slacxop import Operation
from ... import optools
from .... import slacxtools
        
# TODO: Note that the entire data set can be one json,
# of an array of pif records, and this will lead to a faster upload.

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
        self.input_src['dsid'] = optools.user_input
        self.input_type['dsid'] = optools.int_type

    def run(self):
        c = self.inputs['client']
        dsid = self.inputs['dsid'] 
        f = True
        try:
            r = c.get_dataset_files(dsid)
            # check for the 'dataset' key
            if 'dataset' in r.keys():
                s = 'client successfully queried data set {}.'.format(dsid)
                f = True
            else:
                s = 'client queried data set {} but found no dataset in response dict: Response: {}'.format(dsid,r)
                f = True
        except Exception as ex:
            s = 'client failed to query data set number {}. Error message: '.format(dsid) + ex.message
            f = False
        self.outputs['ok_flag'] = f
        self.outputs['status'] = s

class ShipToDataSet(Operation):
    """
    Take a pypif.obj.System object and ship it to a given Citrination data set.    
    """

    def __init__(self):
        input_names = ['pif','client','dsid','ship_flag']
        output_names = ['response']
        super(ShipToDataSet,self).__init__(input_names,output_names)
        self.input_doc['pif'] = 'A pypif.obj.System object'
        self.input_doc['client'] = 'A working Citrination client' 
        self.input_doc['dsid'] = 'Data set ID where the pif will be stored on Citrination' 
        self.input_doc['ship_flag'] = 'Flag for actually shipping the pif' 
        self.output_doc['response'] = 'The Citrination server response to the shipment'
        self.input_src['pif'] = optools.wf_input
        self.input_src['client'] = optools.plugin_input
        self.input_src['dsid'] = optools.user_input
        self.input_src['ship_flag'] = optools.wf_input
        self.input_type['pif'] = optools.auto_type
        self.input_type['client'] = optools.auto_type
        self.input_type['dsid'] = optools.int_type
        self.input_type['ship_flag'] = optools.auto_type

    def run(self):
        cl = self.inputs['client'] 
        # Create the data set
        dsid = self.inputs['dsid'] 
        p = self.inputs['pif']        
        ship_flag = self.inputs['ship_flag']
        try:
            json_file = slacxtools.scratchdir+'/'+p.uid+'.json'
            pif.dump(p, open(json_file,'w'))
            if ship_flag:
                r = cl.upload_file(json_file,data_set_id = dsid)
            else:
                r = 'dry run: no shipment occurred. pif object: {}'.format(pif.dumps(p))
            os.remove(json_file) 
            #print 'add DATA SET {} to tags'.format(dsid)
            #p.tags.append('DATA SET {}'.format(dsid))
            #print 'dump {} to data set {}'.format(json_file,dsid)
            #cl.upload_file(json_file,data_set_id = dsid)
            #print 'NOT SHIPPING {} (this is a test)'.format(json_file)
            #retcodes.append(dsid)
            # delete dataset json
            #print 'deleting file {}'.format(json_file)
        except Exception as ex:
            r = 'An error occurred while shipping. Error message: {}'.format(ex.message)
        self.outputs['response'] = r


