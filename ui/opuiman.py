import os
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

class OpUiManager(object):
    """
    Stores a reference to the op_builder QGroupBox, 
    performs operations on it
    """

    input_sources = ['(select source)','','',''] 
    raw_input_selection = 1
    image_input_selection = 2
    op_input_selection = 3
    input_sources[raw_input_selection] = 'Raw Input'
    input_sources[image_input_selection] = 'Images'
    input_sources[op_input_selection] = 'Operations'

    def __init__(self,ui_file):
        # Load the op_builder popup
        ui_file.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        # Set up the ui widget to delete itself when closed
        self.ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.imgman = None
        self.wfman = None
        self.op = None
        #self.nameval_dict = {}
        #self.op_input_widgets = {} 
        self.setup_ui()

    def set_op_manager(self,opman):
        """
        Set self.opman to input OpManager. 
        Connect op_selector drop-down menu 
        as a view for QAbstractListModel opman.
        """
        self.opman = opman
        # Load initial op and args
        if self.opman.rowCount() > 0:
            self.create_op(0)
        # Connect self.ui.op_selector to opman (QAbstractListModel).
        self.ui.op_selector.setModel(self.opman)

    def set_op(self,op):
        """
        Set self.op to input Operation.
        Set op_selector to the proper Operation subclass.
        Load op.inputs and op.outputs into self.ui.arg_frame.
        """
        self.op = op
        self.ui.op_se

    def setup_ui(self):
        self.ui.setWindowTitle("slacx operation builder")
        self.ui.arg_frame.setMinimumWidth(700)
        self.ui.op_frame.setMinimumWidth(300)
        self.ui.op_frame.setMaximumWidth(300)
        # Connect op selection with a slot that populates ui.op_info and ui.arg_frame
        self.ui.op_selector.activated.connect(self.create_op)
        # Connect ui.finish_button with self.load_op 
        self.ui.finish_button.setText("Finish / Load to Workflow")
        self.ui.finish_button.clicked.connect(self.load_op)
        self.ui.setStyleSheet( "QLineEdit { border: none }" + self.ui.styleSheet() )

    def create_op(self,selection_indx):
        # TODO: align / distribute the widgets nicerly. 
        # Clear description window 
        self.ui.op_info.setPlainText(' ')
        # Create op currently selected in ui.op_selector
        self.op = self.opman.get_op(self.opman.index(selection_indx,0))()
        # Set self.ui.op_info to op.description
        self.ui.op_info.setPlainText(self.op.description())
        # Clear the view of name-value widgets
        self.clear_nameval_list()
        self.build_nameval_list()
        #print 'opuiman.create_op: created new op. description:'
        #print self.op.description()

    def load_op(self):
        """
        Package self.op(Operation), ship to self.wfman
        """ 
        #print 'loading {}(Operation)'.format(type(self.op).__name__)        
        # Parse the inputs saved in self.op_input_widgets 
        #for name, val in self.op.inputs.items():
        #    print 'input {}: {}'.format(name,val)
        #print self.op.description()
        self.wfman.add_op(self.op) 
        self.ui.close()

    def clear_nameval_list(self):
        #self.nameval_dict = {}
        # Count the items in the current layout
        n_val_widgets = self.ui.nameval_layout.count()
        # Loop through them, last to first, clear the frame
        for i in range(n_val_widgets-1,-1,-1):
            # QLayout.takeAt returns a LayoutItem
            widg = self.ui.nameval_layout.takeAt(i)
            # get the QWidget of that LayoutItem and set it to deleteLater()
            widg.widget().deleteLater()

    def build_nameval_list(self):
        #self.op_input_widgets = {}
        # Count the items in the current layout
        n_val_widgets = self.ui.nameval_layout.count()
        # Loop through them, last to first, clear the frame
        for i in range(n_val_widgets-1,-1,-1):
            # QLayout.takeAt returns a LayoutItem- set its widget to deleteLater()
            item = self.ui.nameval_layout.takeAt(i)
            item.widget().deleteLater()
        i=0
        self.ui.nameval_layout.addWidget(self.text_widget('--- INPUTS ---'),i,0,1,5) 
        i+=1
        self.ui.nameval_layout.addWidget(self.hdr_widget('(name)'),i,0,1,1) 
        self.ui.nameval_layout.addWidget(self.hdr_widget('(source)'),i,2,1,1) 
        self.ui.nameval_layout.addWidget(self.hdr_widget('(value)'),i,3,1,1) 
        i+=1 
        for name, val in self.op.inputs.items():
            src_widg,val_widg = self.add_nameval_widgets(name,val,i)
            #self.op_input_widgets[name] = val_widg
            i+=1 
        self.ui.nameval_layout.addWidget(self.smalltext_widget(' '),i,0,1,4) 
        i+=1 
        self.ui.nameval_layout.addWidget(self.text_widget('--- OUTPUTS ---'),i,0,1,5) 
        i+=1 
        self.ui.nameval_layout.addWidget(self.hdr_widget('(name)'),i,0,1,1) 
        self.ui.nameval_layout.addWidget(self.hdr_widget('(value)'),i,2,1,2) 
        i+=1 
        for name, val in self.op.outputs.items():
            self.add_nameval_widgets(name,val,i,output=True)
            i+=1 

    def add_nameval_widgets(self,name,val,row,output=False):
        """a set of widgets for setting or reading input or output data"""
        #widg = QtGui.QWidget()
        name_widget = QtGui.QLineEdit(name)
        name_widget.setReadOnly(True)
        name_widget.setAlignment(QtCore.Qt.AlignRight)
        name_widget.setMinimumWidth(10*len(name))
        self.ui.nameval_layout.addWidget(name_widget,row,0)
        eq_widget = self.smalltext_widget('=')
        self.ui.nameval_layout.addWidget(eq_widget,row,1)
        val_widget = QtGui.QLineEdit(str(val))
        val_widget.setReadOnly(True)
        if output:
            src_widget = None
            self.ui.nameval_layout.addWidget(val_widget,row,2,1,2)
        else:
            src_widget = self.src_selection_widget() 
            src_widget.setMinimumWidth(120)
            self.ui.nameval_layout.addWidget(src_widget,row,2,1,1)
            src_widget.activated.connect( partial(self.render_input_widgets,name,row) )
        return src_widget,val_widget

    def render_input_widgets(self,name,row,src_selection): 
        #src_text = self.ui.nameval_layout.itemAtPosition(row,2).widget().currentText()
        # If input widgets exist, close them.
        for col in [3,4]:
            if self.ui.nameval_layout.itemAtPosition(row,col):
                self.ui.nameval_layout.itemAtPosition(row,col).widget().destroy()
        if not src_selection == 0: 
            if src_selection == self.raw_input_selection:
                val_widget = QtGui.QLineEdit()
                val_widget.setPlaceholderText('(enter value)')
                val_widget.returnPressed.connect( partial(self.load_raw_input,name,val_widget) )
                val_widget.textChanged.connect( partial(self.load_raw_input,name,val_widget) )
                val_widget.textEdited.connect( partial(self.load_raw_input,name,val_widget) )
            elif (src_selection == self.image_input_selection
                or src_selection == self.op_input_selection):
                btn_text = 'Select from Image data...'
                if src_selection == self.op_input_selection:
                    btn_text = 'Select from Operation data...'
                val_widget = QtGui.QLineEdit('None')
                val_widget.setReadOnly(True)
                btn_widget = QtGui.QPushButton(btn_text)
                self.ui.nameval_layout.addWidget(btn_widget,row,4,1,1)
                btn_widget.clicked.connect( partial(self.fetch_data,name,src_selection,val_widget) )
            self.ui.nameval_layout.addWidget(val_widget,row,3,1,1)

    def load_raw_input(self,name,val_widg,edit_text=None):
        self.op.inputs[name] = val_widg.text()
        self.ui.op_info.setPlainText(self.op.description())

    def fetch_data(self,name,src_selection,val_widg):
        """Use a QtGui.QTreeView popup to select the requested input data"""
        # TODO: Allow only one of these popups to exist (one per val widget).
        ui_file = QtCore.QFile(os.getcwd()+"/ui/tree_browser.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        src_ui = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        src_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        src_ui.setParent(self.ui,QtCore.Qt.Window)
        if src_selection == self.image_input_selection:
            trmod = self.imgman
        elif src_selection == self.op_input_selection:
            trmod = self.wfman
        src_ui.tree.setModel(trmod)
        src_ui.tree.resizeColumnToContents(0)
        src_ui.tree.resizeColumnToContents(1)
        for idx in trmod.iter_indexes():
            src_ui.tree.setExpanded(idx,True)
        src_ui.load_button.setText('Load selected data')
        src_ui.load_button.clicked.connect(partial(self.load_from_tree,name,trmod,src_ui,val_widg))
        src_ui.show()

    def load_from_tree(self,name,trmod,src_ui,val_widg):
        """
        Load the item selected in QTreeView src_ui.tree.
        Construct a unique resource identifier (uri) for that item.
        Set self.op.inputs[name] to be that uri.
        Also set that uri to be the text of val_widg.
        Finally, reset self.ui.op_info to reflect the changes.
        """
        trview = src_ui.tree
        # Get the selected item in QTreeView trview:
        tree_item = trmod.get_item(trview.currentIndex())
        # Build a unique URI for this item
        #parent_stack = []
        item_ref = tree_item
        item_uri = item_ref.tag()
        while item_ref.parent.isValid():
            #parent_stack.append(item_ref.parent)
            item_ref = trmod.get_item(item_ref.parent)
            item_uri = item_ref.tag()+"."+item_uri
        val_widg.setText(item_uri)
        val_widg.setMinimumWidth(10*len(item_uri))
        self.op.inputs[name] = item_uri
        #print self.op.inputs
        src_ui.close()
        self.ui.nameval_layout.update()
        self.ui.op_info.setPlainText(self.op.description())

    def text_widget(self,text):
        widg = QtGui.QLineEdit(text)
        widg.setReadOnly(True)
        widg.setAlignment(QtCore.Qt.AlignHCenter)
        return widg 

    def src_selection_widget(self):
        widg = QtGui.QComboBox()
        widg.addItems(self.input_sources)
        #widg.setMinimumContentsLength(20)
        return widg 

    def item_selection_widget(self):
        widg = QtGui.QPushButton('Select...')
        return widg

    def hdr_widget(self,text):
        widg = QtGui.QLineEdit(text)
        widg.setReadOnly(True)
        widg.setAlignment(QtCore.Qt.AlignHCenter)
        widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
        return widg 

    def smalltext_widget(self,text):
        widg = self.text_widget(text)
        widg.setMaximumWidth( 20 )
        widg.setStyleSheet( "QLineEdit { background-color: transparent }" + widg.styleSheet() )
        return widg


