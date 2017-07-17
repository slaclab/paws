from PySide import QtCore, QtGui

from ...core.operations import Operation as op

class WorkflowGraphView(QtGui.QScrollArea):
    
    def __init__(self,wf,parent=None):
        super(WorkflowGraphView,self).__init__(parent)
        self.setWidget(WorkflowGraphWidget(wf,self))        
        #self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setWidgetResizable(True)
        #scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    def keyPressEvent(self,evnt):
        if evnt.key() == QtCore.Qt.Key_Plus:
            self.widget().zoom_in()
        elif evnt.key() == QtCore.Qt.Key_Minus:
            self.widget().zoom_out()
        else:
            super(WorkflowGraphView,self).keyPressEvent(evnt)

class WorkflowGraphWidget(QtGui.QWidget):

    def __init__(self,wf,parent=None):
        super(WorkflowGraphWidget,self).__init__(parent)        
        self.wf = wf
        # rendering scale:
        self._scale = float(1)
        # geometrical factors responsive to self._scale:
        # margins between adjacent objects
        self.hspace = 80
        self.vspace = 40
        # letter width factor?
        self.lwidth = 12 
        # letter height factor?
        self.lheight = 24 
        # letter point size?
        self.lptsize = 12 
        #self.wf.dataChanged.connect(self.update_region_by_idx) 
        self.op_coords = {}
        self.inp_coords = {}
        self.out_coords = {}
        self.update_coords()
        #h_policy = QtGui.QSizePolicy.Minimum
        #v_policy = QtGui.QSizePolicy.MinimumExpanding 
        #v_policy = QtGui.QSizePolicy.Minimum 
        #self.setSizePolicy(h_policy,v_policy)

    #@QtCore.Slot(float)
    def set_scale(self,scl):
        self._scale = float(scl)
        self.update_coords()

    #@QtCore.Slot()
    def zoom_in(self):
        self.set_scale(self._scale*1.2)

    #@QtCore.Slot()
    def zoom_out(self):
        self.set_scale(self._scale/1.2)

    def update_coords(self):
        stk,diag = optools.execution_stack(self.wf)
        self.op_coords, self.inp_coords, self.out_coords = self.get_op_coords(stk)
        if any(self.op_coords):
            stk_height = max([coords[1][1] for coords in self.op_coords.values()]) + self._scale*self.vspace
            stk_width = max([coords[1][0] for coords in self.op_coords.values()]) + self._scale*self.hspace
            self.wf_width = stk_width
            self.wf_height = stk_height 
            self.setMinimumSize(QtCore.QSize(self.wf_width,self.wf_height))
            self.repaint()

    def get_op_coords(self,stk):
        c = {}
        inp_c = {}
        out_c = {}
        # these h,v coords will track the top left corner 
        # of each operation while iterating through the stack.
        h = self._scale*self.hspace 
        v = self._scale*self.vspace 
        for lst in stk:
            v = self._scale*self.vspace
            first_op = self.wf.get_data_from_uri(lst[0])
            if isinstance(first_op,op.Batch) or isinstance(first_op,op.Realtime):
                b_coords, b_inp_coords, b_out_coords = self.get_op_coords(lst[1])
                for name,coords in b_coords.items():
                    topleft = coords[0]
                    bottomright = coords[1]
                    c[name] = [(h+topleft[0],v+topleft[1]),(h+bottomright[0],v+bottomright[1])] 
                if any(b_coords):
                    b_width = max([coords[1][0] for coords in b_coords.values()]) + self._scale*self.hspace 
                    b_height = max([coords[1][1] for coords in b_coords.values()]) + self._scale*self.vspace
                else:
                    b_width = 10 * len(lst[0].tag()) 
                    b_height = b_width 
                c[lst[0]] = [(h,v),(h+b_width,v+b_height)]
                h += b_width + self._scale*self.hspace
            else:
                layer_width = 0
                for name in lst:
                    op = self.wf.get_data_from_uri(name)
                    d = self.op_dims(op)
                    c[name] = [(h,v),(h+d[0],v+d[1])]
                    v += d[1] + self._scale*self.vspace
                    layer_width = max([layer_width,d[0]])
                h += layer_width + self._scale*self.hspace
        return c, inp_c, out_c

    def op_dims(self,op):
        # horizontal extent determined by longest in/out names
        hdim = max([ self.lwidth*max([len(name) for name in op.inputs.keys()] + [len(name) for name in op.outputs.keys()])+10,100])
        # vertical extent determined by number of ins and outs
        vdim = (len(op.inputs)+len(op.outputs))*self.lheight
        return (self._scale*hdim,self._scale*vdim)

    def paintEvent(self,evnt):

        #self.update_coords()

        # create a painter 
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        # give it a white pen 
        pen_w = QtGui.QPen()
        q_white = QtGui.QColor(255,255,255,255)
        pen_w.setColor(q_white)
        pen_w.setWidthF(self._scale)
        p.setPen(pen_w)
        f = QtGui.QFont()
        #print self.lptsize*self._scale
        #f.setPixelSize(self.lpxsize*self._scale)
        f.setPointSize(self.lptsize*self._scale)
        p.setFont(f)
 
        # TODO: Use this to make paintEvent more efficient.
        # QPaintEvent.region() specifies the QtGui.QRegion to paint
        #paint_region = evnt.region()

        for name,coords in self.op_coords.items():
            #print 'coords of {} are topleft = {}, bottomright = {}'.format(name,coords[0],coords[1])
            topleft = QtCore.QPoint(int(coords[0][0]),int(coords[0][1]))
            bottomright = QtCore.QPoint(int(coords[1][0]),int(coords[1][1]))
            op_rec = QtCore.QRectF(topleft,bottomright)
            p.drawRect(op_rec)
            title_rec = QtCore.QRectF(  QtCore.QPoint(int(coords[0][0]),int(coords[0][1])-self.lheight*self._scale),
                                        QtCore.QPoint(int(coords[1][0]),int(coords[0][1])) )
            p.drawText(title_rec,QtCore.Qt.AlignLeft,name)
        # Headers for input and output sides
        #inphdr = QtCore.QRectF(QtCore.QPoint(-1*(recthorz+30),-1*(rectvert+10)),
        #                        QtCore.QPoint(-1*(recthorz+10),-1*rectvert))
        #outhdr = QtCore.QRectF(QtCore.QPoint(recthorz+10,-1*(rectvert+10)),
        #                        QtCore.QPoint(recthorz+30,-1*rectvert))
        #outhdr = QtCore.QRectF(QtCore.QPoint(70,-90),QtCore.QPoint(90,-80))
        #f.setUnderline(True)
        #p.setFont(f)
        #p.drawText(inphdr,QtCore.Qt.AlignCenter,op.inputs_tag)
        #p.drawText(outhdr,QtCore.Qt.AlignCenter,op.outputs_tag)
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
        #    'source: {} \ntype: {} \nvalue: {}'.format(op.input_sources[il.src],op.input_types[il.tp],il.val))
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
       
    #def repaint_region_by_idx(self,topleft_idx,bottomright_idx):
    #    # assume topleft and bottomright are the same,
    #    # i.e. assume the workflow calls dataChanged()
    #    # on just one TreeItem at a time
    #    if not topleft_idx == bottomright_idx:
    #        msg = str('[{}] repaint event was called for a region. '.format(__name__)
    #        + 'Currently only single-index regions can be repainted.')
    #        raise ValueError(msg)
    #    idx = topleft_idx
    #    itm = self.get_item(idx)
    #    # get the coords for this item, call self.update() on that region
    

    #def update(self):

