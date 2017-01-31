import datetime
import tzlocal

from ..slacxop import Operation
from .. import optools

class FilePingTCP(Operation):
    """
    Given a filename and a TCP client,
    this operation asks the client to write a message to its server
    reporting the time and filename.
    """

    def __init__(self):
        input_names = ['client','file']
        output_names = ['response']
        super(FilePingTCP, self).__init__(input_names, output_names)
        self.input_doc['client'] = 'reference to a running tcp client.'
        self.input_doc['file'] = 'input file name, probably handed down from a RealtimeFromFiles controller.'
        self.output_doc['response'] = 'if the client receives a response to its ping, it will be stored here.'
        self.input_src['client'] = optools.plugin_input
        self.input_src['file'] = optools.fs_input
        self.input_type['client'] = optools.auto_type
        self.input_type['file'] = optools.str_type

    def run(self):
        tcpcl = self.inputs['client']
        fname = self.inputs['file']
        tz = tzlocal.get_localzone()
        t = datetime.datetime.now(tz)
        msg = str('hello hello! \n\nthe current time is {}. \n\n'.format(t)
        + 'I hear there is a file at {}.'.format(fname))
        tcpcl.send_text(msg)
        self.outputs['response'] = 'response handling is not implemented.'

