from __future__ import print_function
import socket 

from .PawsPlugin import PawsPlugin
from ..operations import Operation as op

class SpecClientPlugin(PawsPlugin):

    def __init__(self):
        input_names = ['host','port']
        super(SpecClientPlugin,self).__init__(input_names)
        self.input_src['host'] = op.text_input
        self.input_src['port'] = op.text_input
        self.input_type['host'] = op.str_type
        self.input_type['port'] = op.int_type
        self.input_doc['host'] = 'string representing host name or IP address'
        self.input_doc['port'] = 'integer port number at which SpecInfoServer should be listening on host' 
        self.history = []
        self.cmd_list = []
       
    def start(self):
        self.host = self.inputs['host'] 
        self.port = self.inputs['port'] 
        try:
            self.sock = socket.create_connection((self.host, self.port)) 
        except:
            self.sock = None
            print("Spec info server connection problem: {}".format(socket.error))
            pass

    def stop(self):
        print("PawsSpecClient stop")
        self.sock.close()
        # TODO: Anything else for cleaning up the connections.

    def description(self):
        desc = str('SpecInfoServer Client Plugin: '
            + 'This is a TCP Client used to communicate with SpecInfoServer. '
            + 'Startup requires a host name and a port number, '
            + 'where it is expected that SpecInfoServer will be listening.')
        return desc

    def content(self):
        return {'inputs':self.inputs, 'history':self.history, 'socket':self.sock}

    def receiveLine(self):
        # Handle lines received from Spec server
        buffer = bytearray(b' ' * 1024) 
        try:
            len = self.sock.recv_into(buffer) 
        except:
            print("Spec info server connection problem: {}".format(socket.error))
            return "ERRCOMM"

        buffer = buffer.strip(' ')
        return buffer
    
    def sendLine(self, line):
        try:
            self.sock.sendall(bytearray(line))
        except:
            print("Spec info server connection problem: {}".format(socket.error))
            self.history.append('NO CONNECTION TO SPEC INFO SERVER')

    def sendCmd(self, cmd):
        reply = ""
        # Will need timeout
        while reply == "" or reply.startswith("spec is busy!"):
            self.history.append('SEND: {}'.format(cmd))
            self.sendLine(cmd)
            reply = self.receiveLine()
        self.history.append('COMMAND: {} RESPONSE: {}'.format(cmd,reply))

    def send_commands(self, cmd_list):
        self.cmd_list = cmd_list
        if self.cmd_list == []:
            self.history.append('COMMAND LIST EMPTY')
        else:
            for s in self.cmd_list:
                self.sendCmd(s)

    def send_text(self, txt):
        self.cmd_list = [txt]
        send_commands(self.cmd_list)

#--------------------------------------------------------------------------------------------------------------------------#
#    p.addCommand("!cmd slacx_mar_data_path = 'my_mar_data'")
#    p.addCommand("!cmd slacx_pd_filename = 'my_pd_filename'")
#    p.addCommand("!cmd slacx_loopscan_npoints = 2")
#    p.addCommand("!cmd slacx_loopscan_counting_time = 2")
#    p.addCommand("!cmd runme")
#    p.addCommand("?sta")
