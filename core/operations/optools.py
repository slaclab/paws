##### DEFINITIONS OF SOURCES FOR OPERATION INPUTS
input_sources = ['Text','Images','Operations'] 
text_input_selection = 0
image_input_selection = 1
op_input_selection = 2
valid_sources = [text_input_selection,image_input_selection,op_input_selection]

input_types = ['unicode','int','float','array']
unicode_type_selection = 0
int_type_selection = 1
float_type_selection = 2
array_type_selection = 3
valid_types = [unicode_type_selection,int_type_selection,float_type_selection,array_type_selection]

##### CONVENIENCE METHOD FOR PRINTING DOCUMENTATION
def parameter_doc(name,val,doc):
    return "name: {} \nvalue: {} \ndoc: {}".format(name,val,doc) 

##### CONVENIENCE CLASS FOR STORING OR LOCATING OPERATION INPUTS
class InputLocator(object):
    """
    The presence of an object of this type as input to an Operation 
    indicates that this input has not yet been loaded or computed.
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

