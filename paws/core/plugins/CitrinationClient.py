from __future__ import print_function
from collections import OrderedDict

from pypif import pif
from citrination_client import CitrinationClient 

from .. import pawstools
from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod

inputs = OrderedDict(
    address=None,
    api_key_file=None)

class CitrinationClient(PawsPlugin):
    """PAWS Plugin wrapping a Citrination client"""

    def __init__(self):
        super(CitrinationClient,self).__init__(inputs)
        self.input_doc['address'] = 'web address of citrination instance'
        self.input_doc['api_key_file'] = 'path to a file in the local filesystem containing a valid citrination api key'
        self.ctn_client = None

    def start(self):
        self.address = self.inputs['address'] 
        f = open(self.inputs['api_key_file'],'r')
        self.api_key = str(f.readline()).strip()
        f.close()
        self.ctn_client = CitrinationClient(site=self.address,api_key=self.api_key)

    def stop(self):
        self.ctn_client = None

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


