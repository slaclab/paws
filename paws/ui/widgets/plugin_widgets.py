from PySide import QtGui

from ...core.plugins.plugin import PawsPlugin
from ...core.workflow.wf_plugin import WorkflowPlugin 

def plugin_widget(pgin):
    """
    Produce a widget that interacts with the contents of a plugin.
    """
    w = None
    if isinstance(pgin,WorkflowPlugin):
        scroll_area = QtGui.QScrollArea()
        #w = QtGui.QTextEdit(scroll_area)
        #msg = 'selected plugin is a WorkflowPlugin. Producing this text widget.'
        #w.setText(msg)
        w = WorkflowGraphView(pgin.wf)
        scroll_area.setWidget(w)
        return scroll_area 
    else:
        w = QtGui.QTextEdit()
        msg = str('selected plugin is a {}. '.format(type(pgin).__name__)
                + 'No display widgets exist for this plugin. '
                + 'Add a display method to {} to view this plugin.'.format(__name__))
        w.setText(msg)
        return w 

class WorkflowGraphView(QtGui.QWidget):

    def __init__(self,wf):
        super(WorkflowGraphView,self).__init__()
        self.wf = wf
        self.wf.dataChanged.connect(self.repaint_region_by_idx) 
        self.scale = float(1)
        self.op_coords = {}
        self.inp_coords = {}
        self.out_coords = {}

    def repaint_region_by_idx(self,topleft_idx,bottomright_idx):
        # assume topleft and bottomright are the same,
        # i.e. assume the workflow calls dataChanged()
        # on just one TreeItem at a time
        if not topleft_idx == bottomright_idx:
            msg = str('[{}] repaint event was called for a region. '.format(__name__)
            + 'Currently only single-index regions can be repainted.')
            raise ValueError(msg)
        idx = topleft_idx
        itm = self.get_item(idx)
        # get the coords for this item, call self.update() on that region

    def paintEvent(self,evnt):
        # QPaintEvent.region() specifies the QtGui.QRegion to paint
        paint_region = evnt.region()
        # Create a painter and give it a white pen 
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        pen_w = QtGui.QPen()
        q_white = QtGui.QColor(255,255,255,255)
        pen_w.setColor(q_white)
        p.setPen(pen)
        #p.setBrush()...
        #p.translate(w/2, h/2)
        #p.scale(widgdim/200,widgdim/200)
        #rectvert = 80 
        #recthorz = 50
        #topleft = QtCore.QPoint(int(-1*recthorz),int(-1*rectvert))
        #bottomright = QtCore.QPoint(int(recthorz),int(rectvert))
        # Large rectangle representing the Operation
        #mainrec = QtCore.QRectF(topleft,bottomright)
        #p.drawRect(mainrec)
        #title_hdr = QtCore.QRectF(QtCore.QPoint(-100,-1*(rectvert+10)),
        #                        QtCore.QPoint(100,-1*rectvert))
        #title_hdr = QtCore.QRectF(QtCore.QPoint(-30,-10),QtCore.QPoint(30,10))
        #f.setPixelSize(10)
        #f = QtGui.QFont()
        #f.setPointSize(5)
        #p.setFont(f)
        #p.drawText(title_hdr,QtCore.Qt.AlignCenter,type(self.op).__name__)
        #f.setPointSize(4)
        #p.setFont(f)
        # Headers for input and output sides
        #inphdr = QtCore.QRectF(QtCore.QPoint(-1*(recthorz+30),-1*(rectvert+10)),
        #                        QtCore.QPoint(-1*(recthorz+10),-1*rectvert))
        #outhdr = QtCore.QRectF(QtCore.QPoint(recthorz+10,-1*(rectvert+10)),
        #                        QtCore.QPoint(recthorz+30,-1*rectvert))
        #outhdr = QtCore.QRectF(QtCore.QPoint(70,-90),QtCore.QPoint(90,-80))
        #f.setUnderline(True)
        #p.setFont(f)
        #p.drawText(inphdr,QtCore.Qt.AlignCenter,optools.inputs_tag)
        #p.drawText(outhdr,QtCore.Qt.AlignCenter,optools.outputs_tag)
        #f.setUnderline(False)
        #p.setFont(f)
        # Label the inputs
        #n_inp = len(self.op.inputs)
        #ispc = 2*rectvert/(2*n_inp) 
        #vcrd = -1*rectvert+ispc
        #for name in self.op.inputs.keys():
        #    il = self.op.input_locator[name]
        #    rec = QtCore.QRectF(QtCore.QPoint(-1*(recthorz-10),vcrd-5),QtCore.QPoint(0,vcrd+5))
        #    p.drawText(rec,QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,name)
        #    p.drawLine(QtCore.QPoint(-1*(recthorz-5),vcrd),QtCore.QPoint(-1*(recthorz+10),vcrd))
        #    p.drawLine(QtCore.QPoint(-1*(recthorz+10),vcrd-10),QtCore.QPoint(-1*(recthorz+10),vcrd+10))
        #    ilrec = QtCore.QRectF(QtCore.QPoint(-100,vcrd-10),QtCore.QPoint(-1*(recthorz+12),vcrd+10))
        #    p.drawText(ilrec,QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter,#|QtCore.Qt.TextWordWrap,
        #    'source: {} \ntype: {} \nvalue: {}'.format(optools.input_sources[il.src],optools.input_types[il.tp],il.val))
        #    vcrd += 2*ispc
        ## Label the outputs
        #n_out = len(self.op.outputs)
        #ispc = 2*rectvert/(2*n_out)
        #vcrd = -1*rectvert+ispc
        #for name,val in self.op.outputs.items():
        #    rec = QtCore.QRectF(QtCore.QPoint(0,vcrd-5),QtCore.QPoint(recthorz-10,vcrd+5))
        #    p.drawText(rec,QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter,name)
        #    p.drawLine(QtCore.QPoint(recthorz-5,vcrd),QtCore.QPoint(recthorz+10,vcrd))
        #    p.drawLine(QtCore.QPoint(recthorz+10,vcrd-10),QtCore.QPoint(recthorz+10,vcrd+10))
        #    outrec = QtCore.QRectF(QtCore.QPoint(recthorz+12,vcrd-10),QtCore.QPoint(100,vcrd+10))
        #    p.drawText(outrec,QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,type(val).__name__)
        #    #p.drawText(outrec,QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,str(val))
        #    #|QtCore.Qt.TextWordWrap,str(val))
        #    vcrd += 2*ispc

       
    #def update(self):



