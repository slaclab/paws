import datetime
import tzlocal

from ..operation import Operation
from .. import optools

class TestTCP(Operation):
    """
    Given a filename and a TCP client,
    this operation sends some stuff to the TCP client. 
    """

    def __init__(self):
        input_names = ['client']
        output_names = ['response']
        super(TestTCP, self).__init__(input_names, output_names)
        self.input_doc['client'] = 'reference to a running tcp client.'
        self.output_doc['response'] = 'if the client receives a response, it will be stored here.'
        self.input_src['client'] = optools.plugin_input
        self.input_type['client'] = optools.ref_type

    def run(self):
        tcpcl = self.inputs['client']
        tz = tzlocal.get_localzone()
        t = datetime.datetime.now(tz)
        msg = ['!rqc', "!cmd slacx_mar_data_path = 'my_mar_data'", "!cmd slacx_pd_filename = 'my_pd_filename'"]
        msg.extend(["!cmd slacx_loopscan_npoints = 2", "!cmd slacx_loopscan_counting_time = 2"])
        msg.extend(["!cmd runme", "?sta"])
        tcpcl.send_commands(msg)
        self.outputs['response'] = 'response handling is not yet implemented.'

