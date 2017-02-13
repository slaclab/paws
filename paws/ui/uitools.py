import os
import re
import platform
from functools import partial

from PySide import QtGui, QtCore, QtUiTools
import yaml

from ..slacxcore.operations import optools
from ..slacxcore.listmodel import ListModel
from ..slacxcore import slacxtools

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

def text_widget(text):
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignHCenter)
    return widg 

def toggle_expand(trview,idx):
    trview.setExpanded(idx, not trview.isExpanded(idx))

def type_selection_widget(src,widg=None):
    if not widg:
        widg = QtGui.QComboBox()
        lm = ListModel(optools.input_types,widg)
        widg.setModel(lm)
    else:
        lm = ListModel(optools.input_types,widg)
        widg.setModel(lm)
    for tp in optools.valid_types:
        lm.set_enabled(tp)
    for tp in optools.invalid_types[src]:
        lm.set_disabled(tp)
        #widg.model().set_disabled(tp)
    return widg 

def src_selection_widget():
    widg = QtGui.QComboBox()
    lm = ListModel(optools.input_sources,widg)
    #widg.addItems(optools.input_sources)
    widg.setModel(lm)
    maxlen = max([len(srctext) for srctext in optools.input_sources])
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

def bigtext_widget(text):
    #trunc_limit = 200
    #if len(text) > trunc_limit:
    #    text = text[:trunc_limit]+'...'
    widg = QtGui.QLineEdit(text)
    widg.setReadOnly(True)
    widg.setAlignment(QtCore.Qt.AlignLeft)
    ht = widg.sizeHint().height()
    widg.sizeHint = lambda: QtCore.QSize(20*len(text),ht)
    widg.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Fixed)
    return widg

def toggle_load_button(ui,txt):
    idx = ui.tree.model().index(txt)
    if (idx.isValid() and ui.tree.model().isDir(idx) 
    or not os.path.splitext(txt)[1] == '.wfl'):
        ui.load_button.setEnabled(False)
    else:
        ui.load_button.setEnabled(True)

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

def load_path(ui,idx=QtCore.QModelIndex()):
    if idx.isValid():
        p = ui.tree.model().filePath(idx)
        if (ui.tree.model().isDir(idx) 
        or not os.path.splitext(p)[1] == '.wfl'):
            ui.load_button.setEnabled(False)
        else:
            ui.load_button.setEnabled(True)
    
def save_to_file(d,filename):
    """
    Save the items in dict d as YAML in filename
    """
    f = open(filename, 'w')
    #yaml.dump(d, f, encoding='utf-8')
    yaml.dump(d, f)
    f.close()

def stop_save_ui(ui,uiman):
    fname = ui.filename.text()
    if not os.path.splitext(fname)[1] == '.wfl':
        fname = fname + '.wfl'
    uiman.msg_board_log( 'dumping current state to {}'.format(fname) )
    d = {} 
    wf_dict = {} 
    for itm in uiman.wfman.root_items:
        wf_dict[str(itm.tag())] = optools.op_dict(itm.data)
    pgin_dict = {}
    for itm in uiman.plugman.root_items:
        pgin_dict[str(itm.tag())] = optools.plugin_dict(itm.data)
    d['WORKFLOW'] = wf_dict
    d['PLUGINS'] = pgin_dict
    save_to_file(d,fname)
    ui.close()

def stop_load_ui(ui,uiman):
    #fname = ui.filename.text()
    fname = ui.tree.model().filePath(ui.tree.currentIndex())
    f = open(fname,'r')
    d = yaml.load(f)
    f.close()
    if 'WORKFLOW' in d.keys():
        uiman.wfman.load_from_dict(uiman.opman,d['WORKFLOW'])
    if 'PLUGINS' in d.keys():
        uiman.plugman.load_from_dict(d['PLUGINS'])
    ui.close()

def start_save_ui(uiman):
    """
    Start a modal window dialog to choose a save destination for the current workflow  
    """
    ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/qtui/save_browser.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    save_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    #save_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    trmod = QtGui.QFileSystemModel()
    trmod.setRootPath(QtCore.QDir.currentPath())
    #trmod.setRootPath('.')
    #trmod.setRootPath(slacxtools.rootdir)
    trmod.setNameFilters(['*.wfl'])
    save_ui.tree_box.setTitle('Select a file to save the current workflow')
    save_ui.tree.setModel(trmod)
    save_ui.tree.hideColumn(1)
    save_ui.tree.hideColumn(3)
    save_ui.tree.setColumnWidth(0,400)
    save_ui.tree.expandAll()
    save_ui.tree.clicked.connect( partial(save_path,save_ui) )
    save_ui.tree.expanded.connect( partial(save_path,save_ui) )
    #save_ui.tree.activated.connect( save_ui.tree.setCurrentIndex )
    #save_ui.tree.selectionModel().selectionChanged.connect( save_ui.tree.selectionChanged )
    save_ui.setParent(uiman.ui,QtCore.Qt.Window)
    #save_ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
    save_ui.setWindowModality(QtCore.Qt.ApplicationModal)
    save_ui.save_button.setText('&Save')
    save_ui.save_button.clicked.connect(partial(stop_save_ui,save_ui,uiman))
    #save_ui.filename.returnPressed.connect(partial(stop_save_ui,save_ui,uiman))
    save_ui.filename.textChanged.connect( partial(toggle_save_button,save_ui) )
    save_ui.filename.setText(trmod.rootPath())
    save_ui.show()
    save_ui.activateWindow()

def start_load_ui(uiman):
    """
    Start a modal window dialog to load a previously saved workflow
    """
    ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/qtui/load_browser.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    load_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    trmod = QtGui.QFileSystemModel()
    trmod.setRootPath(QtCore.QDir.currentPath())
    trmod.setNameFilters(['*.wfl'])
    load_ui.tree_box.setTitle('Select a .wfl file to load a workflow')
    load_ui.setWindowTitle('workflow loader')
    load_ui.tree.setModel(trmod)
    load_ui.tree.hideColumn(1)
    load_ui.tree.hideColumn(3)
    load_ui.tree.setColumnWidth(0,400)
    load_ui.tree.expandAll()
    load_ui.tree.clicked.connect( partial(load_path,load_ui) )
    load_ui.setParent(uiman.ui,QtCore.Qt.Window)
    #load_ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
    load_ui.setWindowModality(QtCore.Qt.ApplicationModal)
    load_ui.load_button.setText('&Load')
    load_ui.load_button.clicked.connect(partial(stop_load_ui,load_ui,uiman))
    load_ui.show()
    load_ui.activateWindow()

def message_ui(parent=None):
    ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/qtui/message.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    msg_ui = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    msg_ui.setParent(parent,QtCore.Qt.Window)
    msg_ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
    msg_ui.setWindowModality(QtCore.Qt.WindowModal)
    #msg_ui.setMaximumHeight(200)
    msg_ui.message_box.setReadOnly(True)
    msg_ui.ok_button.setText('OK')
    msg_ui.ok_button.clicked.connect(msg_ui.close)
    msg_ui.ok_button.clicked.connect(msg_ui.deleteLater)
    msg_ui.ok_button.setFocus()
    msg_ui.ok_button.setDefault(True)
    return msg_ui

#def start_list_builder(src,lm,parent=None):
#    """Start list builder for data source src and ListModel lm"""
#    ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/qtui/list_builder.ui")
#    ui_file.open(QtCore.QFile.ReadOnly)
#    list_ui = QtUiTools.QUiLoader().load(ui_file)
#    ui_file.close()
#    list_ui.setParent(parent,QtCore.Qt.Window)
#    #list_ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
#    #list_ui.setWindowModality(QtCore.Qt.WindowModal)
#    list_ui.setWindowTitle("build list from {}".format(optools.input_sources[src]))
#    list_ui.value_header.setText('value')
#    list_ui.value_header.setStyleSheet( "QLineEdit { background-color: transparent }" + list_ui.value_header.styleSheet() )
#    list_ui.type_header.setText('type')
#    list_ui.type_header.setStyleSheet( "QLineEdit { background-color: transparent }" + list_ui.type_header.styleSheet() )
#    list_ui.list_view.setModel(lm)
#    list_ui.browse_button.setText('browse...')
#    list_ui.type_selector = type_selection_widget(src,list_ui.type_selector)
#    list_ui.type_selector.model().set_disabled(optools.list_type)
#    if src == optools.text_input:
#        list_ui.browse_button.setEnabled(False)
#        if have_qt47:
#            list_ui.value_entry.setPlaceholderText('(enter value)')
#        else:
#            list_ui.value_entry.setText('')
#    else:
#        list_ui.load_button.setEnabled(False)
#        list_ui.value_entry.setReadOnly(True)
#        list_ui.type_selector.model().set_disabled(optools.none_type)
#        list_ui.type_selector.model().set_disabled(optools.auto_type)
#    list_ui.type_selector.setCurrentIndex(optools.str_type)
#    list_ui.load_button.setText('Load')
#    list_ui.finish_button.setText('Finish')
#    list_ui.remove_button.setText('Remove')
#    list_ui.load_button.clicked.connect( partial(load_value_to_list,list_ui) )
#    list_ui.remove_button.clicked.connect( partial(rm_from_list,list_ui) )
#    return list_ui

#def load_value_to_list(list_ui):
#    # typecast and load the value_entry.text()
#    # only typecast if tp is not auto_type
#    tp = list_ui.type_selector.currentIndex()
#    if tp == optools.auto_type:
#        val = list_ui.value_entry.text()
#    else:
#        val = optools.cast_type_val(tp,list_ui.value_entry.text())
#    list_ui.list_view.model().append_item(val)

#def rm_from_list(list_ui):
#    idx = list_ui.list_view.currentIndex()
#    if idx.isValid():
#        row = idx.row()
#        list_ui.list_view.model().remove_item(row)

#def data_fetch_ui(parent=None):
#    ui_file = QtCore.QFile(slacxtools.rootdir+"/slacxui/qtui/load_browser.ui")
#    ui_file.open(QtCore.QFile.ReadOnly)
#    src_ui = QtUiTools.QUiLoader().load(ui_file)
#    ui_file.close()
#    src_ui.setParent(parent,QtCore.Qt.Window)
#    #src_ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
#    #src_ui.setWindowModality(QtCore.Qt.WindowModal)
#    src_ui.load_button.setText('&Load')
#    return src_ui

