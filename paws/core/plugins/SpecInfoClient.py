from __future__ import print_function
from collections import OrderedDict
import socket 

from .PawsPlugin import PawsPlugin
from ..operations import Operation as opmod

inputs = OrderedDict(
    host = None,
    port = None)

class SpecInfoClient(PawsPlugin):

    def __init__(self):
        super(SpecInfoClient,self).__init__(inputs)
        self.input_doc['host'] = 'string representing host name or IP address'
        self.input_doc['port'] = 'integer port number where SpecInfoServer listens' 
        self.history = []
        self.sock = None
       
    def start(self):
        hst = self.inputs['host'] 
        prt = self.inputs['port'] 
        #try:
        self.sock = socket.create_connection((hst,prt)) 
        #except:
        #    self.socket_error(self.sock.error)

    def description(self):
        desc = 'SpecInfoClient Plugin: '\
            'This is a TCP Client used to communicate with SpecInfoServer. '\
            'Startup requires a host name and a port number, '\
            'where SpecInfoServer should be listening.'
        return desc

    def content(self):
        return {'inputs':self.inputs, 'history':self.history, 'socket':self.sock}

    def socket_error(errmsg):
        msg = "SpecInfoClient socket error: {}".format(errmsg)
        self.history.append(msg)
        if self.message_callback:
            self.message_callback(msg)

    def stop(self):
        self.history.append("SpecInfoClient stop")
        self.sock.close()
        # TODO: Anything else for cleaning up the connections.

    def receiveLine(self):
        # Handle lines received from Spec server
        bfr = bytearray(b' ' * 1024) 
        #try:
        ln = self.sock.recv_into(bfr) 
        #except:
        #    self.socket_error(self.sock.error)
        #    return "ERRCOMM"
        bfr = bfr.strip()
        return bfr
    
    def sendLine(self, line):
        #try:
        self.sock.sendall(bytearray(line))
        #except:
        #    self.socket_error(self.sock.error)

    def sendCmd(self, cmd):
        reply = ""
        # TODO: implement delay and timeout 
        while reply == "" or reply.startswith("spec is busy!"):
            self.history.append('SEND: {}'.format(cmd))
            self.sendLine(cmd)
            reply = self.receiveLine()
        self.history.append('COMMAND: {} RESPONSE: {}'.format(cmd,reply))
        return reply

    def send_commands(self, cmd_list):
        for s in cmd_list:
            self.sendCmd(s)

#------------------------------------------------------------------------------
#    p.addCommand("!cmd slacx_mar_data_path = 'my_mar_data'")
#    p.addCommand("!cmd slacx_pd_filename = 'my_pd_filename'")
#    p.addCommand("!cmd slacx_loopscan_npoints = 2")
#    p.addCommand("!cmd slacx_loopscan_counting_time = 2")
#    p.addCommand("!cmd runme")
#    p.addCommand("?sta")
#




# General controls
# !rqc                  -> requests control
# !cmd mar_enable       -> enables mar det as a counter
# !cmd pd enable        -> enables pilatus as a counter


# Temperature control macro:
# macro definition: /usr/local/lib/spec.d/cryocon_ctrl.mac
#
# Direct SIS commands:
# !cmd ctemp_enable     -> establishes communication with CryoCon
# 
# !cmd csettemp 40      -> sets temperature
# !cmd cmeasuretemp     -> reads temperature, saves as 
#
# !cmd CRYO_DEGC        -> sets up a query on the CRYO_DEGC variable
# followed by:
# ?res                  -> gets result of CRYO_DEGC query


# Loop Scanning
#
# !cmd loopscan n_points exposure_time sleep_time


