from PySide import QtCore

##### DEFINITIONS OF SOURCES FOR OPERATION INPUTS
input_sources = ['None','Filesystem','Operations','Text'] 
no_input = 0
fs_input = 1
op_input = 2
text_input = 3
valid_sources = [no_input,fs_input,op_input,text_input]

##### VALID TYPES FOR TEXT BASED OPERATION INPUTS 
input_types = ['None','string','integer','float','boolean']
none_type = 0
str_type = 1
int_type = 2
float_type = 3
bool_type = 4
valid_types = [none_type,str_type,int_type,float_type,bool_type]
# TODO: implement some kind of builder/loader for data structs, like arrays or dicts
#array_type = 5
        
##### IMAGE LOADER EXTENSIONS    
def loader_extensions():
    return str(
    "ALL (*.*);;"
    + "TIFF (*.tif *.tiff);;"
    + "RAW (*.raw);;"
    + "MAR (*.mar*)"
    )

##### CONVENIENCE METHOD FOR PRINTING DOCUMENTATION
def parameter_doc(name,value,doc):
    if type(value).__name__ == 'InputLocator':
        val_str = str(value.val)
    else:
        val_str = str(value)
    return "- name: {} \n- value: {} \n- doc: {}".format(name,val_str,doc) 

##### CONVENIENCE CLASS FOR STORING OR LOCATING OPERATION INPUTS
class InputLocator(object):
    """
    This object is used as a container for an input to an Operation.
    Objects of this class contain the information needed to find the relevant input data.
    If raw textual input is provided, it is stored in self.val after typecasting.
    """
    def __init__(self,src,val):
        if src < 0 or src > len(input_sources):
            msg = 'found input source {}, should be between 0 and {}'.format(
            src, len(input_sources))
            raise ValueError(msg)
        self.src = src
        self.val = val 
        self.data = None 

