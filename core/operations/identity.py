from core.operations.slacxop import Operation

class Identity(Operation):
    """The Identity(Operation) class: a container for doing nothing"""

    def __init__(self):
        input_names = ['image_data']
        output_names = ['image_data']
        super(Identity,self).__init__(input_names,output_names)        
        self.input_doc['image_data'] = '2d array representing intensity for each pixel'
        self.output_doc['image_data'] = 'same 2d array as input'
        
    def run(self):
        self.outputs['image_data'] = self.inputs['image_data']
        return self

#    def description(cls):
#        return str(
#        "An Identity operation takes one input argument: "
#        + "inputs['image_data'] (a 2d pixel array). "
#        + "When Identity.run() is called, "
#        + "it saves the same pixel array in outputs['image_data']. "
#        )

#    def tag(self):
#        return "Image-Identity"

