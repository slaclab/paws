from ... import Operation as op
from ...Operation import Operation
        
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
        self.input_src['client'] = op.plugin_input
        self.input_src['dsid'] = op.text_input
        self.input_type['client'] = op.ref_type
        self.input_type['dsid'] = op.int_type

    def run(self):
        c = self.inputs['client']
        dsid = self.inputs['dsid'] 
        f = True
        try:
            r = c.get_dataset_files(dsid)
            if 'name' in r.keys():
                s = 'client successfully queried data set {}: {}. Response: {}'.format(dsid,r['name'],r)
                f = True
            else:
                s = 'client queried data set {}, but was unable to find the data set name. Response: {}'.format(dsid,r)
                f = True
        except Exception as ex:
            s = 'client failed to query data set number {}. Error message: {}'.format(dsid,ex.message)
            f = False
        self.outputs['ok_flag'] = f
        self.outputs['status'] = s

