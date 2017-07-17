from __future__ import print_function

from pypif import pif
from citrination_client import CitrinationClient 

from .. import pawstools
from .PawsPlugin import PawsPlugin
from ..operations import Operation as op

class CitrinationPlugin(PawsPlugin):
    """
    Wrapper contains a Citrination client and
    implements the PawsPlugin abc interface.
    """

    def __init__(self):
        input_names = ['address','api_key_file']
        super(CitrinationPlugin,self).__init__(input_names)
        self.input_doc['address'] = 'web address of citrination instance'
        self.input_doc['api_key_file'] = 'path to a file in the local filesystem containing a valid citrination api key'
        self.input_src['address'] = op.text_input
        self.input_src['api_key_file'] = op.fs_input
        self.input_type['address'] = op.str_type
        self.input_type['api_key_file'] = op.path_type
        self.inputs['address'] = 'https://slac.citrination.com' 
        self.ctn_client = None
        self.return_codes = {} 

    def start(self):
        self.address = self.inputs['address'] 
        f = open(self.inputs['api_key_file'],'r')
        self.api_key = str(f.readline()).strip()
        f.close()
        self.ctn_client = CitrinationClient(api_key = self.api_key, site = self.address)

    def stop(self):
        pass

    def content(self): 
        return {'client':self.ctn_client,'inputs':self.inputs}

    def description(self):
        desc = str('Citrination API Client Plugin for Paws: '
            + 'This is a container for the Citrination Client module. '
            + 'The Citrination Client connects to a Citrination instance '
            + 'and exposes some parts of the Citrination API. '
            + 'Startup requires the web address of a Citrination instance '
            + 'and an API key that provides access to that instance.')
        return desc

    def ship_dataset(self,pifs):
        # Create the data set
        response = self.ctn_client.create_data_set()
        dsid = response.json()['id']
        # TODO: Note that the entire data set can be one json,
        # of an array of pif records, and this will lead to a faster upload.
        for p in pifs:
            try:
                json_file = pawstools.scratchdir+'/'+p.uid+'.json'
                pif.dump(p, open(json_file,'w'))
                #print 'add DATA SET {} to tags'.format(dsid)
                #p.tags.append('DATA SET {}'.format(dsid))
                #print 'dump {} to data set {}'.format(json_file,dsid)
                cl.upload_file(json_file,data_set_id = dsid)
                #print 'NOT SHIPPING {} (this is a test)'.format(json_file)
                self.return_codes[p.uid]=1
                # delete dataset json
                #print 'deleting file {}'.format(json_file)
                os.remove(json_file) 
            except:
                # TODO: Pass along some return code from the server?
                self.return_codes[p.uid]=-1


