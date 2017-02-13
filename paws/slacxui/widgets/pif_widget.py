from PySide import QtCore, QtGui
import pypif.obj as pifobj

from text_widgets import display_text, unit_indent

# TODO: Make an (editable?) PIF Widget

class PifWidget(QtGui.QTextEdit):
    
    def __init__(self,itm):
        t = self.print_pif(itm,unit_indent)
        super(PifWidget,self).__init__()
        self.setText(t) 

    def print_pif(self,itm,indent):
        t = '(pypif.obj.System)'
        if itm.uid: 
            #string
            t += '<br>' + indent + 'uid: {}'.format(display_text(itm.uid,indent+unit_indent))
        if isinstance(itm,pifobj.ChemicalSystem):
            if itm.chemical_formula: 
                #string
                t += '<br>' + indent + 'chemical_formula: {}'.format(
                display_text(itm.chemical_formula,indent+unit_indent))
            if itm.composition is not None:
                #array of pypif.obj.Composition
                t += '<br>' + indent + 'composition: (array)'
                for i,comp in zip(range(len(itm.composition)),itm.composition):
                    t += '<br>' + indent + unit_indent + '{}: {}'.format(
                    i,self.print_comp(comp,indent+unit_indent+unit_indent))
        if itm.names is not None: 
            #array of string
            t += '<br>' + indent + 'names: (array)'
            for i,nm in zip(range(len(itm.names)),itm.names):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, display_text(nm,indent+unit_indent+unit_indent))
        if itm.quantity: 
            #pypif.obj.Quantity
            t += '<br>' + indent + 'quantity: {}'.format(self.print_qty(itm.quantity,indent+unit_indent))
        if itm.source: 
            #pypif.obj.Source
            t += '<br>' + indent + 'source: {}'.format(self.print_src(itm.source,indent+unit_indent))
        if itm.preparation is not None: 
            #array of pypif.obj.ProcessStep
            t += '<br>' + indent + 'preparation: (array)'
            for i,procstep in zip(range(len(itm.preparation)),itm.preparation):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_procstep(procstep,indent+unit_indent+unit_indent))
        if itm.properties is not None: 
            #array of pypif.obj.Property
            t += '<br>' + indent + 'properties: (array)'
            for i,prop in zip(range(len(itm.properties)),itm.properties):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_prop(prop,indent+unit_indent+unit_indent))
        if itm.tags is not None: 
            #array of string
            t += '<br>' + indent + 'tags: (array)'
            for i,tg in zip(range(len(itm.tags)),itm.tags):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, display_text(tg,indent+unit_indent+unit_indent))
        if itm.ids is not None: 
            #array of pypif.obj.Id
            t += '<br>' + indent + 'ids: (array)'
            for i,id_ in zip(range(len(itm.ids)),itm.ids):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_id(id_,indent+unit_indent+unit_indent))
        if itm.sub_systems is not None: 
            #array of pypif.obj.System
            t += '<br>' + indent + 'sub_systems: (array)'
            for i,sys in zip(range(len(itm.sub_systems)),itm.sub_systems):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_pif(sys,indent+unit_indent+unit_indent))
        return t    

    def print_id(self,id_,indent):
        t = '(pypif.obj.Id)'
        return t
    
    def print_comp(self,itm,indent):    
        t = '(pypif.obj.Composition)'
        return t
    
    def print_qty(self,itm,indent):    
        t = '(pypif.obj.Quantity)'
        return t

    def print_src(self,itm,indent):    
        t = '(pypif.obj.Source)'
        return t

    def print_procstep(self,itm,indent):
        t = '(pypif.obj.ProcessStep)'
        return t

    def print_prop(self,itm,indent):
        t = '(pypif.obj.Property)'
        t += '<br>' + indent + 'name: {}'.format(display_text(itm.name,indent+unit_indent))
        if itm.conditions is not None:
            t += '<br>' + indent + 'conditions: (array)' 
            for i,val in zip(range(len(itm.conditions)),itm.conditions):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_value(val,indent+unit_indent+unit_indent))
        if itm.scalars is not None:
            t += '<br>' + indent + 'scalars: (array)' 
            for i,scl in zip(range(len(itm.scalars)),itm.scalars):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_scalar(scl,indent+unit_indent+unit_indent))
        return t

    def print_value(self,itm,indent):
        t = '(pypif.obj.Value)'
        t += '<br>' + indent + 'name: {}'.format(display_text(itm.name,indent+unit_indent))
        if itm.scalars is not None:
            t += '<br>' + indent + 'scalars: (array)'
            for i,scl in zip(range(len(itm.scalars)),itm.scalars):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_scalar(scl,indent+unit_indent+unit_indent))
        elif itm.vectors is not None:
            t += '<br>' + indent + 'vectors: (array)'
            for i,vec in zip(range(len(itm.vectors)),itm.vectors):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_vector(vec,indent+unit_indent+unit_indent))
        elif itm.matrices is not None:
            t += '<br>' + indent + 'matrices: (array)'
            for i,mat in zip(range(len(itm.matrices)),itm.matrices):
                t += '<br>' + indent + unit_indent + '{}: {}'.format(
                i, self.print_matrix(mat,indent+unit_indent+unit_indent))
        return t

    def print_scalar(self,itm,indent):
        t = '(pypif.obj.Scalar)'
        t += '<br>' + indent + 'value: {}'.format(itm.value) 
        return t

    def print_vector(self,itm,indent):
        t = '(array)'
        for i,scl in zip(range(len(itm)),itm):
            t += '<br>' + indent + unit_indent + '{}: {}'.format(
            i, self.print_scalar(scl,indent+unit_indent+unit_indent))
        return t

    def print_matrix(self,itm,indent):
        t = '(array)'
        for i,vec in zip(range(len(itm)),itm):
            t += '<br>' + indent + unit_indent + '{}: {}'.format(
            i, self.print_vector(vec,indent+unit_indent+unit_indent))
        return t

