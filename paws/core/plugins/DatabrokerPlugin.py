from __future__ import print_function

from .. import pawstools
from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod
        
from filestore.fs import FileStore
from metadatastore.mds import MDS
from databroker import Broker
from databroker.core import register_builtin_handlers

class DatabrokerPlugin(PawsPlugin):
    """
    Wrapper contains a Citrination client and
    implements the PawsPlugin abc interface.
    """

    def __init__(self):
        input_names = ['host','port','fs_collection','mds_collection','username','password']
        super(DatabrokerPlugin,self).__init__(input_names)
        self.inputs['fs_collection'] = 'fs_dev'
        self.inputs['mds_collection'] = 'mds_dev'

    def start(self):

        host = self.inputs['host']
        port = self.inputs['port']
        fs_collection = self.inputs['fs_collection']
        mds_collection = self.inputs['mds_collection']
        username = self.inputs['username']
        password = self.inputs['password']

        fs_config = {'host': host, 'port': port,
                     'database': fs_collection, 'username':username,'password':password}
        mds_conf = dict(database=mds_collection, host=host, username=username, password=password,
                        port=port, timezone='US/Eastern')

        fs = FileStore(fs_config, version=1)

        # may need to register handlers
        # for name,handler in handlers.iteritems(): fs.register_handler(name, handler)
        register_builtin_handlers(fs)

        mds = MDS(mds_conf, 1, auth=False)

        db = Broker(mds, fs)
        self.db = db

    def stop(self):
        pass

    @property
    def content(self): 
        return {'client':self.db,'inputs':self.inputs}

    def description(self):
        desc = str("""DataBroker API client Plugin for PAWS:
        This is a container for the PAWS Client module.
        The databroker client connects to a databroker instance
        and exposes the databroker api through self.content['client'].
        Startup requires the host address, port, and collection name;
        username and password are optionally necessary.""")
        return desc

