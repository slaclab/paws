from core.operations.slacxop import Operation

class Identity(Operation):

    def __init__(self,args):
        self.imgdata = args['img'] 
        
    def args(self):
        return {'imgdata':self.imgdata}

    def run(self):
        return {'imgdata':self.imgdata}

    def description(self):
        return str(
        "An Identity operation is constructed by: \n"
        + ">> op = Identity(args)\n"
        + "where args is a dict " 
        + "containing the image data (as a 2D array)"
        + "in a field named 'imgdata'.\n\n"
        + "For example, \n"
        + ">> op = Identity( {'imgdata':existing_2d_array} )\n"
        + "creates an Identity(Operation) object "
        + "and sets self.imgdata to existing_2d_array"
        )

