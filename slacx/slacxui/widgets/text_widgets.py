from ...slacxcore.operations import optools 
from ...slacxcore.operations.slacxop import Operation
from ...slacxcore.slacxtools import FileSystemIterator

unit_indent='&nbsp;&nbsp;&nbsp;&nbsp;'

def display_text(itm,indent=unit_indent):
    if type(itm).__name__ in ['str','unicode']:
        t = '(str) <br>' + indent + '{}'.format(itm)
    elif isinstance(itm,dict):
        t = '(dict)'
        for k,v in itm.items():
            t += '<br>' + indent + '{}: {}'.format(k,display_text(v,indent+unit_indent))
    elif isinstance(itm,list):
        t = '(list)'
        for i in range(len(itm)):
            t += '<br>' + indent + '{}: {}'.format(i,display_text(itm[i],indent+unit_indent))
    elif isinstance(itm,Operation):
        t = '(Operation)'
        t += '<br>' + indent + 'inputs: {}'.format(display_text(itm.inputs,indent+unit_indent))
        t += '<br>' + indent + 'outputs: {}'.format(display_text(itm.outputs,indent+unit_indent))
    elif isinstance(itm,optools.InputLocator):
        t = '(InputLocator)'
        t += '<br>' + indent + 'src: {}'.format(optools.input_sources[itm.src])
        t += '<br>' + indent + 'type: {}'.format(optools.input_types[itm.tp])
        t += '<br>' + indent + 'val: {}'.format(itm.val)
        t += '<br>' + indent + 'data: {}'.format(type(itm.data).__name__)
    elif isinstance(itm,FileSystemIterator):
        t = '(FileSystemIterator)'
        for ip,p in zip(range(len(itm.paths_done)),itm.paths_done):
            t += '<br>' + indent + '{}: {}'.format(ip,p)
    else:
        t = '('+type(itm).__name__+')' + '<br>' + indent + '{}'.format(itm)
    return t
    

