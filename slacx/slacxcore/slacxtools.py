import os
from datetime import datetime as dt

from PySide import QtCore, QtUiTools
from PySide import QtCore

version='0.0.2'

qdir = QtCore.QDir(__file__)
qdir.cdUp()
rootdir = os.path.split( qdir.absolutePath() )[0]#+'/slacx'

def throw_specific_error(msg):
    msg = 'something specific happened: ' + msg
    raise Exception(msg)

class LazyCodeError(Exception):
    def __init__(self,msg):
        super(LazyCodeError,self).__init__(self,msg)

def start_message_ui():
    ui_file = QtCore.QFile(rootdir+"/slacxui/message.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    msg_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    msg_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    msg_ui.setWindowModality(QtCore.Qt.WindowModal)
    #msg_ui.setMaximumHeight(200)
    msg_ui.message_box.setReadOnly(True)
    msg_ui.ok_button.setText('OK')
    msg_ui.ok_button.clicked.connect(msg_ui.close)
    msg_ui.ok_button.clicked.connect(msg_ui.deleteLater)
    msg_ui.ok_button.setDefault(True)
    return msg_ui

def dtstr():
    """Return date and time as a string"""
    return dt.strftime(dt.now(),'%Y %m %d, %H:%M:%S')

def timestr():
    """Return time as a string"""
    return dt.strftime(dt.now(),'%H:%M:%S')




