from __future__ import print_function
from collections import OrderedDict

from pypif import pif
from citrination_client import CitrinationClient as CitCli

from .PawsPlugin import PawsPlugin

content = OrderedDict(
    address=None,
    api_key_file=None)

class CitrinationClient(PawsPlugin):
    """PAWS Plugin wrapping a Citrination client"""

    def __init__(self):
        super(CitrinationClient,self).__init__(content)
        self.content_doc['address'] = 'web address of citrination instance'
        self.content_doc['api_key_file'] = 'path to a file in the local filesystem containing a valid citrination api key'
        self.client=None

    def start(self):
        super(CitrinationClient,self).start()
        self.address = self.content['address'] 
        f = open(self.content['api_key_file'],'r')
        self.api_key = str(f.readline()).strip()
        f.close()
        self.client = CitCli(self.api_key,self.address)

    def stop(self):
        self.client = None

    def description(self):
        desc = str('Citrination Client Plugin for Paws: '
            + 'This is a container for the Citrination Client module. '
            + 'The Citrination Client connects to a Citrination instance '
            + 'and exposes some parts of the Citrination API. '
            + 'Startup requires the web address of a Citrination instance '
            + 'and an API key that provides access to that instance.')
        return desc


