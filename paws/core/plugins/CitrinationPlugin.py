from __future__ import print_function

from pypif import pif
from citrination_client import CitrinationClient 

from .. import pawstools
from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod

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
        self.inputs['address'] = 'http://citrination.com' 
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
        desc = str('Citrination Client Plugin for Paws: '
            + 'This is a container for the Citrination Client module. '
            + 'The Citrination Client connects to a Citrination instance '
            + 'and exposes some parts of the Citrination API. '
            + 'Startup requires the web address of a Citrination instance '
            + 'and an API key that provides access to that instance.')
        return desc


