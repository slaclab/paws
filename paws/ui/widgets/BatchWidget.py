import os
from functools import partial
from collections import OrderedDict

from PySide import QtGui, QtCore, QtUiTools

from .. import uitools
from .. import widgets
from ...core import pawstools
from ...core.operations import Operation as opmod
from ...core.models.ListModel import ListModel

class BatchWidget(QtGui.QWidget):
    """
    PAWS-based implementation of Xi-cam batch widgetry
    """

    def __init__(self,paws_api):
        super(BatchWidget,self).__init__()
        ui_file = QtCore.QFile(pawstools.sourcedir+"/ui/qtui/batch_widget.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.paw = paws_api
        self._wfname = 'img_process'
        self._batch_wfname = 'batch'
 
        # This is a dict to translate from on-screen operation names
        # to uris for locating the Operations in paws.
        self.ops = OrderedDict()
        self.ops['read_PONI'] = 'IO.CALIBRATION.ReadPONI'
        #self.ops['read_darkfield'] = 'INPUT.TIF.LoadTif'
        #self.ops['read_flatfield'] = 'INPUT.TIF.LoadTif'
        #self.ops['read_background'] = 'INPUT.TIF.LoadTif'
        self.ops['read_image'] = 'IO.IMAGE.FabIOOpen'
        self.ops['calibrate_image'] = 'PROCESSING.CALIBRATION.Calibrate'
        self.ops['integrate_image'] = 'PROCESSING.CALIBRATION.CalReduce'
        self.ops['log_I_2d'] = 'PROCESSING.BASIC.ArrayLog'
        self.ops['log_I_1d'] = 'PROCESSING.BASIC.LogY'
        self.ops['write_csv'] = 'IO.CSV.WriteArrayCSV'
        #self.ops['batch'] = 'EXECUTION.BATCH.BatchFromFiles'

        self.paw.activate_op('EXECUTION.BATCH.BatchFromFiles')
        for nm,opuri in self.ops.items():
            self.paw.activate_op(opuri)       

        # This is a dict for holding on to widgets,
        # so that they can be displayed in self.ui.output_tabs as needed.
        self.output_widgets = {} 

        self.build_ui()
        self.wf_setup()

    def build_ui(self):
        self.ui.output_tabs.clear()
        self.ui.setWindowTitle('batch widget')
        self.ui.wf_box.setTitle('workflow control')
        self.ui.batch_box.setTitle('batch control')
        self.ui.fs_box.setTitle('filesystem browser')
        self.ui.viewer_box.setTitle('viewer')
        self.ui.run_wf_button.setText('&Run') 
        self.ui.run_wf_button.clicked.connect(self.run_wf) 
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )
        self.ui.main_splitter.setSizes([1,2,1])
        self.ui.add_files_button.setText('Add selected files')
        self.ui.add_files_button.clicked.connect(self.add_files)
        self.ui.remove_files_button.setText('Remove selected files')
        self.ui.remove_files_button.clicked.connect(self.rm_files)
        # filesystem viewer setup
        fsmod = QtGui.QFileSystemModel()
        fsmod.setRootPath(QtCore.QDir.currentPath())
        self.ui.fs_browser.setModel(fsmod)
        self.ui.fs_browser.hideColumn(1)
        self.ui.fs_browser.hideColumn(3)
        self.ui.fs_browser.setColumnWidth(0,400)
        idx = fsmod.index(QtCore.QDir.currentPath())
        while idx.isValid():
            self.ui.fs_browser.setExpanded(idx,True)
            idx = idx.parent()
        #self.ui.fs_browser.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #self.ui.fs_browser.setSelectionModel(QtGui.QItemSelectionModel.Rows)
        self.ui.batch_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ui.fs_browser.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def add_files(self):
        idxs = self.ui.fs_browser.selectedIndexes()
        for idx in idxs:
            if idx.column() == 0:
                fpath = self.ui.fs_browser.model().filePath(idx)
                itm = QtGui.QListWidgetItem()
                itm.setText(fpath)
                self.ui.batch_list.addItem(itm)    

    def rm_files(self):
        itms = self.ui.batch_list.selectedItems()
        for itm in itms:
            self.ui.batch_list.takeItem(self.ui.batch_list.row(itm))

    def wf_setup(self):
        self.paw.add_wf(self._wfname)
        self.paw.connect_wf_input('image_path','read_image.inputs.path',self._wfname)
        self.paw.add_wf(self._batch_wfname)

        # Set up the batch execution Operation first
        self.paw.select_wf(self._batch_wfname)
        self.paw.add_op('batch','EXECUTION.BATCH.BatchFromFiles')
        self.paw.set_input('batch','workflow',self._wfname)
        self.paw.set_input('batch','input_name','image_path')

        # Set up the rest of the workflow
        self.paw.select_wf(self._wfname)
        for op_name,op_uri in self.ops.items():
            add_op_row = self.paw.op_count(self._wfname)+1
            op_tag = op_name

            # Add the op to the workflow
            self.paw.add_op(op_tag,op_uri,self._wfname)
            # Set up the inputs....
            self.default_op_setup(op_tag)

            # Add the op name in a text box
            op_tag_widget = QtGui.QLineEdit(op_tag)
            op_tag_widget.setReadOnly(True)
            self.ui.wf_layout.addWidget(op_tag_widget,add_op_row,0,1,1)

            # Add buttons to interact with op 
            op_edit_button = QtGui.QPushButton('edit')
            op_edit_button.clicked.connect( partial(self.edit_op,op_tag,op_name) )
            enable_toggle = QtGui.QCheckBox('enable')
            enable_toggle.setCheckState(QtCore.Qt.Checked)
            #enable_toggle.stateChanged.connect( partial(self.toggle_enabled,op_tag) )
            vis_toggle = QtGui.QCheckBox('view')
            vis_toggle.stateChanged.connect( partial(self.set_visualizer,op_tag) )
            self.ui.wf_layout.addWidget(enable_toggle,add_op_row,3,1,1)
            self.ui.wf_layout.addWidget(vis_toggle,add_op_row,4,1,1)
            self.ui.wf_layout.addWidget(op_edit_button,add_op_row,5,1,1)

    def default_op_setup(self,op_tag):
        if op_tag == 'read_PONI':
            # Ultimately this should be set by the user or taken from another part of the application
            #self.paw.set_input(op_tag,'poni_file','')
            self.paw.set_input(op_tag,'poni_file',os.path.join(pawstools.paws_scratch_dir,'test.poni'))

        elif op_tag == 'read_image':
            # This is where the batch operation will set its inputs
            self.paw.set_input(op_tag,'path','')

        elif op_tag == 'calibrate_image' or op_tag == 'integrate_image':
            self.paw.set_input(op_tag,'image_data','read_image.outputs.image_data')
            self.paw.set_input(op_tag,'poni_dict','read_PONI.outputs.poni_dict')

        elif op_tag == 'log_I_1d':
            self.paw.set_input(op_tag,'x_y','integrate_image.outputs.q_I')

        elif op_tag == 'log_I_2d':
            self.paw.set_input(op_tag,'x','calibrate_image.outputs.I_at_q_chi')

        elif op_tag == 'write_csv':
            self.paw.set_input(op_tag,'array','integrate_image.outputs.q_I')
            self.paw.set_input(op_tag,'headers',['q','I'])
            self.paw.set_input(op_tag,'dir_path','read_image.outputs.dir_path','workflow item')
            self.paw.set_input(op_tag,'filename','read_image.outputs.filename')
            self.paw.set_input(op_tag,'filetag','_processed')

    def set_visualizer(self,op_tag,state):
        if not state==0:
            # Find, create, or otherwise open the widget
            if not op_tag in self.output_widgets.keys():
                widg = self.make_widget(op_tag) 
                self.output_widgets[op_tag] = widg
            else:
                # The user closed the tab
                # instead of un-checking the visualizer box,
                # so the widget should still be in self.output_widgets
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

    def make_widget(self,op_tag):
        if op_tag == 'read_PONI':
            output_data = self.paw.get_output(op_tag,'poni_dict',self._wfname)
        elif op_tag == 'read_image':
            output_data = self.paw.get_output(op_tag,'image_data',self._wfname)
        elif op_tag == 'calibrate_image':
            output_data = self.paw.get_output(op_tag,'I_at_q_chi',self._wfname)
        elif op_tag == 'integrate_image':
            output_data = self.paw.get_output(op_tag,'q_I',self._wfname)
        elif op_tag == 'log_I_1d':
            output_data = self.paw.get_output(op_tag,'x_logy',self._wfname)
        elif op_tag == 'log_I_2d':
            output_data = self.paw.get_output(op_tag,'logx',self._wfname)
        elif op_tag == 'write_csv':
            output_data = self.paw.get_output(op_tag,'csv_path',self._wfname)
        # Form a widget from the output data 
        widg = widgets.make_widget(output_data)
        return widg

    def run_wf(self):
        self.paw.select_wf(self._batch_wfname)
        file_list = []
        nfiles = self.ui.batch_list.count()
        for r in range(nfiles):
            p = self.ui.batch_list.item(r).text()
            file_list.append(p)
        self.paw.set_input('batch','file_list',file_list)
        self.paw.execute()
        self.update_visuals()

    def update_visuals(self):
        for widg in self.output_widgets:
            if isinstance(widg,QtGui.QWidget):
                widg.repaint()

    def edit_op(self,op_tag,op_name):
        pass

