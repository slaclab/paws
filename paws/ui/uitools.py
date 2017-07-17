"""
Configuration flags, widgets, and functions for paws gui control.
"""

import os
import re
import platform
from functools import partial

from PySide import QtGui, QtCore, QtUiTools
import yaml

from ..core.operations import Operation as op
from ..core import pawstools
from ..core.models.ListModel import ListModel

## Test whether we have Qt >= 4.7 
have_qt47 = True
versionReq = [4, 7]
QtVersion = QtCore.__version__ 
m = re.match(r'(\d+)\.(\d+).*', QtVersion)
if m is not None and list(map(int, m.groups())) < versionReq:
    have_qt47 = False

## Test whether we are using Windows
if platform.system() == 'Windows':
    have_windows = True
else:
    have_windows = False

class QSourceEdit(QtGui.QTextEdit):
    
    def __init__(self):
        super(QSourceEdit,self).__init__()

    def keyPressEvent(self,evnt):
        if evnt.key() == QtCore.Qt.Key_Tab:
            # insert 4 spaces
            # TODO: Make this a user-configurable thing?
            super(QSourceEdit,self).insertPlainText('    ')
        else:
            super(QSourceEdit,self).keyPressEvent(evnt)

def text_widget(text):
    """
    Produce a Read-only Center-aligned QtGui.QLineEdit from input text.
    """
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignHCenter)
    return widg 

def toggle_expand(trview,idx):
    trview.setExpanded(idx, not trview.isExpanded(idx))

def type_selection_widget(src,widg=None):
    if not widg:
        widg = QtGui.QComboBox()
        lm = ListModel(op.input_types,widg)
        widg.setModel(lm)
    else:
        lm = ListModel(op.input_types,widg)
        widg.setModel(lm)
    for tp in op.valid_types:
        lm.set_enabled(tp)
    for tp in op.invalid_types[src]:
        lm.set_disabled(tp)
        #widg.model().set_disabled(tp)
    return widg 

def src_selection_widget():
    widg = QtGui.QComboBox()
    lm = ListModel(op.input_sources,widg)
    #widg.addItems(op.input_sources)
    widg.setModel(lm)
    maxlen = max([len(srctext) for srctext in op.input_sources])
    widg.setMinimumWidth(20*maxlen)
    return widg 
        
def r_hdr_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignRight)
    widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
    return widg 

def hdr_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignLeft)
    widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
    return widg 

def smalltext_widget(text):
    widg = text_widget(text)
    widg.setMaximumWidth(20*len(text))
    widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
    return widg

def name_widget(name):
    name_widget = QtGui.QLineEdit(name)
    name_widget.setReadOnly(True)
    name_widget.setAlignment(QtCore.Qt.AlignRight)
    ht = name_widget.sizeHint().height()
    name_widget.sizeHint = lambda: QtCore.QSize(10*len(name_widget.text()),ht)
    name_widget.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
    return name_widget

def bigtext_widget(text=None):
    #trunc_limit = 200
    #if len(text) > trunc_limit:
    #    text = text[:trunc_limit]+'...'
    if text is None:
        text = ''
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignLeft)
    ht = widg.sizeHint().height()
    widg.sizeHint = lambda: QtCore.QSize(20*len(text),ht)
    #widg.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Fixed)
    widg.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
    return widg

def start_save_ui(parent,fspath=None):
    ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/save_browser.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    save_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    # set ui to be deleted and to emit destroyed() signal when its window is closed
    save_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    trmod = QtGui.QFileSystemModel()
    trmod.setNameFilters(['*.wfl'])
    #save_ui.tree_box.setTitle('Select or enter a .wfl file to save current workflow'.format(wfname))
    save_ui.tree.setModel(trmod)
    save_ui.tree.hideColumn(1)
    save_ui.tree.hideColumn(3)
    save_ui.tree.setColumnWidth(0,400)
    save_ui.tree.expandAll()
    save_ui.tree.clicked.connect( partial(save_path,save_ui) )
    save_ui.tree.expanded.connect( partial(save_path,save_ui) )
    trmod.setRootPath(QtCore.QDir.currentPath())
    idx = trmod.index(QtCore.QDir.currentPath())
    if fspath is not None:
        try:
            trmod.setRootPath(fspath)
            idx = trmod.index(fspath)
        except:
            pass
    while idx.isValid():
        save_ui.tree.setExpanded(idx,True)
        idx = idx.parent()
    save_ui.setParent(parent,QtCore.Qt.Window)
    save_ui.setWindowModality(QtCore.Qt.ApplicationModal)
    save_ui.save_button.setText('&Save')
    #save_ui.filename.returnPressed.connect(partial(stop_save_ui,save_ui))
    save_ui.filename.textChanged.connect( partial(toggle_save_button,save_ui) )
    save_ui.filename.setText(trmod.rootPath())
    return save_ui

def toggle_save_button(ui,txt):
    idx = ui.tree.model().index(ui.filename.text())
    if idx.isValid() and ui.tree.model().isDir(idx):
        ui.save_button.setEnabled(False)
    else:
        ui.save_button.setEnabled(True)

def save_path(ui,idx=QtCore.QModelIndex(),oldidx=QtCore.QModelIndex()):
    if idx.isValid():
        p = ui.tree.model().filePath(idx)
        ui.filename.setText(p)

def start_load_ui(parent,fspath=None):
    ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/load_browser.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    load_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    # set ui to be deleted and to emit destroyed() signal when its window is closed
    load_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    trmod = QtGui.QFileSystemModel()
    trmod.setNameFilters(['*.wfl'])
    #load_ui.tree_box.setTitle('Select a .wfl file from which to load a workflow')
    load_ui.tree.setModel(trmod)
    load_ui.tree.hideColumn(1)
    load_ui.tree.hideColumn(3)
    load_ui.tree.setColumnWidth(0,400)
    load_ui.tree.expandAll()
    load_ui.tree.clicked.connect( partial(load_path,load_ui) )
    trmod.setRootPath(QtCore.QDir.currentPath())
    idx = trmod.index(QtCore.QDir.currentPath())
    if fspath is not None:
        try:
            trmod.setRootPath(fspath)
            idx = trmod.index(fspath)
        except:
            pass
    while idx.isValid():
        load_ui.tree.setExpanded(idx,True)
        idx = idx.parent()
    load_ui.setParent(parent,QtCore.Qt.Window)
    #load_ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
    load_ui.setWindowModality(QtCore.Qt.ApplicationModal)
    load_ui.load_button.setText('&Load')
    return load_ui

def load_path(ui,idx=QtCore.QModelIndex()):
    if idx.isValid():
        p = ui.tree.model().filePath(idx)
        if (ui.tree.model().isDir(idx) 
        or not os.path.splitext(p)[1] == '.wfl'):
            ui.load_button.setEnabled(False)
        else:
            ui.load_button.setEnabled(True)
    
def message_ui(parent):
    ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/message.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    msg_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    msg_ui.setParent(parent,QtCore.Qt.Window)
    msg_ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
    msg_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    msg_ui.setWindowModality(QtCore.Qt.WindowModal)
    #msg_ui.setMaximumHeight(200)
    msg_ui.message_box.setReadOnly(True)
    msg_ui.ok_button.setText('OK')
    msg_ui.ok_button.clicked.connect(msg_ui.close)
    msg_ui.ok_button.clicked.connect(msg_ui.deleteLater)
    msg_ui.ok_button.setFocus()
    msg_ui.ok_button.setDefault(True)
    return msg_ui


