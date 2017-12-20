import os

from PySide import QtGui, QtCore, QtUiTools

from ....core import pawstools
from .PluginWidget import PluginWidget

class QCitrinationClient(PluginWidget):

    def __init__(self):
        super(QCitrinationClient,self).__init__()
        ui_file_path = os.path.join(pawstools.sourcedir,'qt','qtui','QCitrinationClient.ui') 
        ui_file = QtCore.QFile(ui_file_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.plugin = None

    def connect_plugin(self,plugin):
        self.plugin = plugin
        self.widget.address_header.setText('address:')
        self.widget.address_header.setReadOnly(True)
        self.widget.address_entry.setText(plugin.inputs['address'])
        self.widget.keyfile_entry.setText(plugin.inputs['api_key_file'])
        self.widget.keyfile_header.setText('api_key_file:')
        self.widget.keyfile_header.setReadOnly(True)
        self.widget.set_address_button.clicked.connect(self.set_address)  
        self.widget.set_keyfile_button.clicked.connect(self.set_keyfile)
        self.widget.start_button.clicked.connect(self.start_client)
        self.widget.test_button.clicked.connect(self.test_client)
        self.widget.status_report.setText('not connected')
        self.widget.status_report.setReadOnly(True)

    def set_address(self):
        adtxt = self.widget.address_entry.getText()
        self.plugin.inputs['address'] = adtxt

    def set_keyfile(self):
        kftxt = self.widget.keyfile_entry.getText()
        self.plugin.inputs['api_key_file'] = kftxt
        
    def start_client(self):
        self.plugin.start()

    def test_client(self):
        if isinstance(self.plugin.ctn_client,CitrinationClient):
            self.widget.status_report.setText('connected')
        else:
            self.widget.status_report.setText('not connected')



