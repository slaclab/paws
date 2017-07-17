from twisted.internet import task, reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.protocols.policies import TimeoutMixin

from .PawsPlugin import PawsPlugin
from ..operations import Operation as op

class TCPClientPlugin(PawsPlugin):

    def __init__(self):
        input_names = ['host','port']
        super(TCPClientPlugin,self).__init__(input_names)
        self.input_src['host'] = op.text_input
        self.input_src['port'] = op.text_input
        self.input_type['host'] = op.str_type
        self.input_type['port'] = op.int_type
        self.input_doc['host'] = 'string representing host name or IP address'
        self.input_doc['port'] = 'integer port number at which some server will be listening' 
       
    def start(self):
        self.host = self.inputs['host'] 
        self.port = self.inputs['port'] 
        self.client_factory = TCPClientFactory(TCPTestProtocol)
        # Set up the TCP connection with host and port, specify the factory
        reactor.connectTCP(self.host, self.port, self.client_factory)

    def stop(self):
        reactor.stop()
        # TODO: Anything else for cleaning up the connections.

    def description(self):
        desc = str('TCP Client Plugin for Paws: '
            + 'This is a TCP Client for general purpose and testing.')
        return desc

    def content(self):
        return {'inputs':self.inputs,'history':self.client_factory.history,'client_factory':self.client_factory}

    def send_text(self,txt):
        self.client_factory.cmd_list = [txt]
        reactor.run()                   

class TCPTestProtocol(LineReceiver):

    def __init__(self):
        """
        It is expected that this constructor will be called by a ClientFactory.
        The ClientFactory is expected to set protocol.factory to refer to itself
        after instantiating the protocol.
        The ClientFactory is expected to have a .history (list of strings).
        """
        #print "Protocol build"
        #self.delimiter = '\r\n'
        self.delimiter = '\n'
        self.cmdList = []

    def addCommand(self, cmd): 
        self.cmdList.append(cmd)

    def connectionMade(self):
        # Set up any objects specific to this Protocol.
        self.factory.history.append('CONNECTION MADE')
        #self.sendLineFromList() 

    def lineReceived(self, line):
        self.factory.history.append('RECEIVED: {}'.format(line))
 
    def connectionLost(self):
        # Dereference any objects specific to this Protocol.
        self.factory.history.append('CLIENT LOST CONNECTION')
        self.factory = None 
        self.cmdList = None 
    
    def send_lines(self):
        if self.cmdList == []:
            self.factory.history.append('COMMAND LIST EMPTY: LOSING CONNECTION')
            self.transport.loseConnection()
        else:
            line = self.cmdList.pop(0)
            #print "send: %s" % line
            self.factory.history.append('SEND: {}'.format(line))
            #LineReceiver.sendLine(self, line)
            self.sendLine(line)
            # call self.timeoutConnection after 5 seconds
            #self.setTimeout(5)

    #def timeoutConnection(self):
    #    #print "Connection timeout, communication aborted"
    #    self.factory.history.append('TIMEOUT: aborting connection')
    #    self.transport.abortConnection()

class TCPClientFactory(ClientFactory):

    def __init__(self, protocol):
        #print "ClientFactory build"
        self.protocol = protocol
        self.history = []
        self.cmd_list = []

    def buildProtocol(self, addr):
        #print "Connected to %s" % addr
        self.history.append('BUILDING PROTOCOL. ADDRESS = {}'.format(addr))
        p = self.protocol()
        p.factory = self
        p.cmdList = self.cmd_list
        self.cmd_list = []
        return p

    def clientConnectionFailed(self, connector, reason):
        """Clients call this when they are unable to initialize their connection."""
        self.history.append('CONNECTION FAILED: {}'.format(reason.getErrorMessage()))
        self.history.append('STOPPING REACTOR')
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        """Clients call this when their connections are lost."""
        #Note: could optionally use connector.connect() to try to rescue the session.
        self.history.append('CONNECTION LOST: {}'.format(reason.getErrorMessage()))
        self.history.append('STOPPING REACTOR')
        reactor.stop()


