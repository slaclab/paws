from ...Operation import Operation
from ... import optools
        
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

