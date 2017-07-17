from functools import partial
from collections import OrderedDict

from PySide import QtGui, QtCore, QtUiTools

from .. import uitools
from .. import widgets
from ...core import pawstools
from ...core.operations import Operation as op
from ...core.models.ListModel import ListModel

class PipelineWidget(QtGui.QWidget):
    """
    Stores a reference to a QMainWindow,
    performs operations on it
    """

    def __init__(self,paws_api):
        super(PipelineWidget,self).__init__()
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/pipeline_widget.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.paw = paws_api
        self._wfname = 'pipeline'
        self.paw.add_wf(self._wfname)
    
        # This is a dict to translate from on-screen operation names
        # to uris for locating the Operations in paws.
        self.ops = OrderedDict()
        self.ops['read_PONI'] = 'INPUT.CALIBRATION.ReadPONI'
        self.ops['read_background'] = 'INPUT.TIF.LoadTif'
        self.ops['read_image'] = 'INPUT.TIF.LoadTif'
        self.ops['calibrate_background'] = 'PROCESSING.CALIBRATION.Calibrate'
        self.ops['calibrate_image'] = 'PROCESSING.CALIBRATION.Calibrate'
        self.ops['subtract_background'] = 'PROCESSING.BACKGROUND.SubtractMaximumBackground'
        self.ops['saxs_profile'] = 'PROCESSING.SAXS.SAXSProfile'

        # This is a dict for declaring the dependencies of operations.
        # An operation should only be added to the pipeline
        # when all of its dependencies are already in there.
        self.deps = dict.fromkeys(self.ops.keys()) 
        self.deps['calibrate_background'] = ['read_background']
        self.deps['calibrate_image'] = ['read_image']
        self.deps['subtract_background'] = ['calibrate_background','calibrate_image']
        self.deps['saxs_profile'] = ['subtract_background']

        # This is a dict for specifying inputs that need to be set by the user
        # when an operation is loaded.
        self.required_inputs = dict.fromkeys(self.ops.keys())
        self.required_inputs['read_PONI'] = ['poni_file']
        self.required_inputs['read_background'] = ['path']
        self.required_inputs['read_image'] = ['path']

        # This is a dict for holding on to widgets,
        # so that they can be displayed in self.ui.output_tabs as needed.
        self.output_widgets = {} 

        self.build_ui()
        self.set_wf_widgets()

    def build_ui(self):
        self.ui.output_tabs.clear()
        self.ui.setWindowTitle('pipeline widget')
        self.ui.wf_groupBox.setTitle('workflow control')
        self.ui.output_groupBox.setTitle('output inspector')
        self.ui.run_wf_button.setText('&Run') 
        self.ui.run_wf_button.clicked.connect(self.run_wf) 
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )
        self.ui.splitter.setSizes([1,1])

    def set_wf_widgets(self):
        add_op_row = self.paw.op_count(self._wfname)+1
        self.ui.wf_layout.addWidget(self.add_op_button(),add_op_row,0,1,1)

    def add_op_button(self):
        btn = QtGui.QPushButton('&+...',self)
        btn.setMaximumWidth(60)
        # TODO: btn.setIcon(icon_image)
        btn.clicked.connect(self.add_op)
        return btn

    def add_op(self):
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/list_selector.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        add_op_ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        add_op_ui.selector_box.setTitle('select operation')
        add_op_ui.setWindowTitle('operation setup')
        op_list_model = ListModel(self.ops.keys())
        self.refresh_op_list(op_list_model)
        add_op_ui.op_list.setModel(op_list_model)
        add_op_ui.add_button.setText('&OK')
        add_op_ui.op_list.doubleClicked.connect( partial(self.finish_add_op,add_op_ui) )
        add_op_ui.add_button.clicked.connect( partial(self.finish_add_op,add_op_ui) )
        add_op_ui.done_button.setText('&Cancel')
        add_op_ui.done_button.clicked.connect(add_op_ui.close)
        add_op_ui.setParent(self.ui,QtCore.Qt.Window)
        add_op_ui.show()

    def finish_add_op(self,ui,op_idx=None):
        add_op_row = self.paw.op_count(self._wfname)+1
        if op_idx is None:
            # Get selection ui.op_list
            op_idx = ui.op_list.currentIndex()
        op_name = self.ops.keys()[op_idx.row()]
        op_tag = op_name
        if op_tag in self.paw.get_wf(self._wfname).list_op_tags():
            op_tag = self.paw.get_wf(self._wfname).make_unique_uri(op_name)
        op_uri = self.ops[op_name]
        # Add the op to the workflow
        # TODO: ensure op names are unique before wf loading.
        # TODO: then, make sure unique op names are still recognized upstream during automatic input loading.
        self.paw.add_op(op_tag,op_uri,self._wfname)
        # Set the default input structure
        self.default_op_setup(op_tag)
        # If op has inputs to set, whip out some widgets
        if self.required_inputs[op_name] is not None:
            for inpname in self.required_inputs[op_name]:
                print 'fetch {}.{}'.format(op_tag,inpname) 
                self.fetch_data(op_tag,inpname,ui)

        print 'proceed with op loading'
        # Add the op name in a text box
        op_tag_widget = QtGui.QLineEdit(op_tag)
        op_tag_widget.setReadOnly(True)
        self.ui.wf_layout.addWidget(op_tag_widget,add_op_row,0,1,1)
        
        # Add buttons to edit, remove, or toggle visualization
        op_edit_button = QtGui.QPushButton('edit')
        op_edit_button.clicked.connect( partial(self.edit_op,op_tag,op_name) )
        rm_op_button = QtGui.QPushButton('remove')
        rm_op_button.clicked.connect( partial(self.rm_op,op_tag) )
        vis_toggle = QtGui.QCheckBox('display')
        vis_toggle.stateChanged.connect( partial(self.set_visualizer,op_tag) )
        self.ui.wf_layout.addWidget(op_edit_button,add_op_row,1,1,1)
        self.ui.wf_layout.addWidget(rm_op_button,add_op_row,2,1,1)
        self.ui.wf_layout.addWidget(vis_toggle,add_op_row,3,1,1)

        # Refresh the ops list
        self.refresh_op_list(ui.op_list.model())
        ui.repaint()

        # Prepare workflow building widgets for whatever is next
        self.set_wf_widgets()
        print 'close add_op ui'
        ui.close()

    def edit_op(self,op_tag,op_name):
        for inpname in self.required_inputs[op_name]:
            self.fetch_data(op_tag,inpname,self.ui)
        #ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/op_quicksetup.ui")
        #ui_file.open(QtCore.QFile.ReadOnly)
        #op_setup_ui = QtUiTools.QUiLoader().load(ui_file)
        #ui_file.close()
        #op_setup_ui.inputs_box.setTitle('operation: {}'.format(op_tag))
        #op_setup_ui.setWindowTitle('operation setup')
        ## Get a reference to the Operation by name...
        ## TODO: this sort of op inspection should be rolled into the api
        #op = self.paw.get_op(op_tag)
        #val_widgets = {}
        #for inprow,inpnm in zip(range(len(op.inputs.keys())),op.inputs.keys()):
        #    inp_tag_widget = uitools.name_widget(inpnm)
        #    op_setup_ui.inputs_layout.addWidget(inp_tag_widget,inprow,0,1,1)
        #    eq_widget = uitools.smalltext_widget('=')
        #    op_setup_ui.inputs_layout.addWidget(eq_widget,inprow,1,1,1)
        #    val_widget = uitools.bigtext_widget(op.input_locator[inpnm].val) 
        #    val_widget.setReadOnly(False)
        #    op_setup_ui.inputs_layout.addWidget(val_widget,inprow,2,1,1)
        #    val_widgets[inpnm] = val_widget
        #    btn_widget = QtGui.QPushButton('browse...')
        #    btn_widget.setMaximumWidth(80)
        #    btn_widget.clicked.connect( partial(self.fetch_data,op_tag,inpnm,op_setup_ui) )
        #    inpsrc = op.input_sources[op.input_locator[inpnm].src]
        #    if inpsrc == op.text_input:
        #        btn_widget.setEnabled(False)
        #    op_setup_ui.inputs_layout.addWidget(btn_widget,inprow,3,1,1)
        #op_setup_ui.finish_button.setText('&OK')
        #op_setup_ui.finish_button.clicked.connect( partial(self.finish_edit_op,op_tag,val_widgets,op_setup_ui) )
        #op_setup_ui.setParent(self.ui,QtCore.Qt.Window)
        #op_setup_ui.show()

    def fetch_data(self,op_tag,input_name,parent_ui):
        print 'now fetching for {}.{}'.format(op_tag,input_name)
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/tree_selector.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        data_fetch_ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        data_fetch_ui.setParent(parent_ui,QtCore.Qt.Window)
        #data_fetch_ui.setWindowModality(QtCore.Qt.WindowModal)
        data_fetch_ui.setWindowModality(QtCore.Qt.ApplicationModal)
        data_fetch_ui.setWindowTitle('browse for {}.{}'.format(op_tag,input_name))
        op = self.paw.get_op(op_tag)
        src = op.input_locator[input_name].src 
        if src == op.wf_input:
            # TODO: add a workflow selector?
            wf = self.paw.get_wf(self._wfname)
            data_fetch_ui.source_treeview.setModel(wf)
        elif src == op.fs_input:
            fs_trmod = QtGui.QFileSystemModel()
            data_fetch_ui.source_treeview.setModel(fs_trmod)
            fs_trmod.setRootPath(QtCore.QDir.currentPath())
            idx = fs_trmod.index(QtCore.QDir.currentPath())
            while idx.isValid():
                data_fetch_ui.source_treeview.setExpanded(idx,True)
                idx = idx.parent()
            data_fetch_ui.source_treeview.setExpanded(fs_trmod.index(pawstools.sourcedir),True)
            data_fetch_ui.source_treeview.hideColumn(1)
            data_fetch_ui.source_treeview.hideColumn(3)
            data_fetch_ui.source_treeview.setColumnWidth(0,250)
        data_fetch_ui.finish_button.setText('&OK')
        data_fetch_ui.source_treeview.doubleClicked.connect( 
        partial(self.finish_fetch_data,op_tag,input_name,data_fetch_ui) )        
        data_fetch_ui.finish_button.clicked.connect( 
        partial(self.finish_fetch_data,op_tag,input_name,data_fetch_ui) )        
        print 'bringing up data_fetch ui'
        data_fetch_ui.show()

    def finish_fetch_data(self,op_tag,input_name,src_ui,idx=None):
        if idx is None:
            idx = src_ui.source_treeview.currentIndex()
        op = self.paw.get_op(op_tag)
        src = op.input_locator[input_name].src 
        if src == op.wf_input:
            v = str(src_ui.source_treeview.model().get_uri_of_index(idx)).strip()
        elif src == op.fs_input:
            v = str(src_ui.source_treeview.model().filePath(idx)).strip()
        self.paw.set_input(op_tag,input_name,val=v)
        #dest_widget.setText(v)
        src_ui.close()

    #def finish_edit_op(self,op_tag,val_widgets,ui):
    #    op = self.paw.get_op(op_tag)
    #    for input_name in op.inputs.keys():
    #        self.paw.set_input(op_tag,input_name,val=val_widgets[input_name].text())
    #    ui.close()
    #    ui.deleteLater()

    def refresh_op_list(self,op_list_model):
        loaded_op_tags = self.paw.list_op_tags(self._wfname)
        for op_row,op_name in zip(range(len(self.ops.keys())),self.ops.keys()):
            if self.deps[op_name] is not None:
                if all(self.op_tag_match(nm,loaded_op_tags) for nm in self.deps[op_name]):
                    op_list_model.set_enabled(op_row)
                else:
                    op_list_model.set_disabled(op_row)

    @staticmethod
    def op_tag_match(op_name,op_tags):
        if isinstance(op_tags,str):
            op_tags = [op_tags]
        for op_tag in op_tags:
            if len(op_tag) >= len(op_name):
                if op_name == op_tag[:len(op_name)]:
                    return True
        return False

    def latest_op_tag(self,op_name):
        for op_tag in self.paw.list_op_tags(self._wfname):
            if self.op_tag_match(op_name,op_tag):
                return op_tag
        return None

    def default_op_setup(self,op_tag):
        if self.op_tag_match('read_PONI',op_tag):
            self.paw.set_input(op_tag,'poni_file',
            src='filesystem',tp='path',val='')

        elif self.op_tag_match('read_background',op_tag):
            self.paw.set_input(op_tag,'path',
            src='filesystem',tp='path',val='')

        elif self.op_tag_match('read_image',op_tag):
            self.paw.set_input(op_tag,'path',
            src='filesystem',tp='path',val='')

        elif self.op_tag_match('calibrate_background',op_tag):
            bg_op_tag = self.latest_op_tag('read_background')
            poni_op_tag = self.latest_op_tag('read_PONI')
            self.paw.set_input(op_tag,'image_data',
            src='workflow',tp='reference',val=bg_op_name+'.outputs.image_data')
            self.paw.set_input(op_tag,'poni_dict',
            src='workflow',tp='reference',val=poni_op_name+'.outputs.poni_dict')

        elif self.op_tag_match('calibrate_image',op_tag):
            img_op_name = self.latest_op_tag('read_image') 
            poni_op_name = self.latest_op_tag('read_PONI') 
            self.paw.set_input(op_tag,'image_data',
            src='workflow',tp='reference',val=img_op_name+'.outputs.image_data')
            self.paw.set_input(op_tag,'poni_dict',
            src='workflow',tp='reference',val=poni_op_name+'.outputs.poni_dict')

        elif self.op_tag_match('subtract_background',op_tag):
            imgcal_op_name = self.latest_op_tag('calibrate_image') 
            bgcal_op_name = self.latest_op_tag('calibrate_background') 
            self.paw.set_input(op_tag,'I',
            src='workflow',tp='reference',val=imgcal_op_name+'.outputs.I')
            self.paw.set_input(op_tag,'I_bg',
            src='workflow',tp='reference',val=bgcal_op_name+'.outputs.I')

        elif self.op_tag_match('saxs_profile',op_tag):
            bgsub_op_name = self.latest_op_tag('subtract_background')
            self.paw.set_input(op_tag,'q',
            src='workflow',tp='reference',val=bgsub_op_name+'.outputs.q')
            self.paw.set_input(op_tag,'I',
            src='workflow',tp='reference',val=bgsub_op_name+'.outputs.I_at_q')
            
    def rm_op(self,op_name):
        print 'remove {}'.format(op_name)

    def set_visualizer(self,op_tag,state):
        if not state==0:
            # Find, create, or otherwise open the widget
            if not op_tag in self.output_widgets.keys():
                # Get the interesting piece of data from this op
                output_data = self.get_output_data(op_tag)
                # Form a widget from the output data 
                widg = widgets.make_widget(output_data)
                self.output_widgets[op_tag] = widg
            else:
                # The user has closed a tab
                # instead of unchecking the visualizer box
                widg = self.output_widgets[op_tag]
            if self.ui.output_tabs.indexOf(widg) == -1:
                # Add a tab to self.ui.output_tabs 
                tab_idx = self.ui.output_tabs.addTab(widg,op_tag) 
            self.ui.output_tabs.setCurrentWidget(widg)
        else:
            widg = self.output_widgets.pop(op_tag)
            if widg is not None:
                tab_idx = self.ui.output_tabs.indexOf(widg)  
                widg.close() 
                if not tab_idx == -1: 
                    self.ui.output_tabs.removeTab(tab_idx)

    def update_visuals(self):
        for widg in self.output_widgets:
            if isinstance(widg,QtGui.QWidget):
                widg.repaint()

    def get_output_data(self,op_tag):
        if self.op_tag_match('read_PONI',op_tag):
            return self.paw.get_output(op_tag,'poni_dict',self._wfname)
        elif ( self.op_tag_match('read_background',op_tag)
        or self.op_tag_match('read_image',op_tag) ):
            return self.paw.get_output(op_tag,'image_data',self._wfname)
        elif ( self.op_tag_match('calibrate_background') 
        or self.op_tag_match('calibrate_image',op_tag) ):
            return self.paw.get_output(op_tag,'q_I',self._wfname)
        elif self.op_tag_match('subtract_background',op_tag):
            return self.paw.get_output(op_tag,'q_I',self._wfname)
        elif self.op_tag_match('saxs_profile',op_tag):
            return self.paw.get_output(op_tag,'results',self._wfname)
                
    def run_wf(self):
        self.paw.execute()
        self.update_visuals()
