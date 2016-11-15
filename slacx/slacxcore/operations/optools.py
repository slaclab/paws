from PySide import QtCore

##### DEFINITIONS OF SOURCES FOR OPERATION INPUTS
input_sources = ['None','User Input','Filesystem','Operations','Batch'] 
no_input = 0
user_input = 1
fs_input = 2
op_input = 3
batch_input = 4 
valid_sources = [no_input,user_input,fs_input,op_input,batch_input]

##### VALID TYPES FOR OPERATION INPUTS
input_types = ['None','auto','string','integer','float','boolean','list']
none_type = 0
auto_type = 1
str_type = 2
int_type = 3
float_type = 4
bool_type = 5
list_type = 6
valid_types = [none_type,auto_type,str_type,int_type,float_type,bool_type,list_type]
        
##### IMAGE LOADER EXTENSIONS    
def loader_extensions():
    return str(
    "ALL (*.*);;"
    + "TIFF (*.tif *.tiff);;"
    + "RAW (*.raw);;"
    + "MAR (*.mar*)"
    )

##### CONVENIENCE CLASS FOR STORING OR LOCATING OPERATION INPUTS
class InputLocator(object):
    """
    This object is used as a container for an input to an Operation.
    Objects of this class contain the information needed to find the relevant input data.
    If raw textual input is provided, it is stored in self.val after typecasting.
    """
    def __init__(self,src,tp,val):
        if src < 0 or src > len(input_sources):
            msg = 'found input source {}, should be between 0 and {}'.format(
            src, len(input_sources))
            raise ValueError(msg)
        self.src = src
        self.tp = tp
        self.val = val 
        self.data = None 

##### CONVENIENCE METHOD FOR PRINTING DOCUMENTATION
def parameter_doc(name,value,doc):
    #if type(value).__name__ == 'InputLocator':
    if isinstance(value, InputLocator):
        val_str = str(value.val)
    else:
        val_str = str(value)
    return "- name: {} \n- value: {} \n- doc: {}".format(name,val_str,doc) 

