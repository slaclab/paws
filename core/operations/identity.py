from core.operations.slacxop import Operation

class Identity(Operation):

    def __init__(self):
        input_vars = ['image_data']
        output_vars = ['image_data']
        super(Identity,self).__init__(input_vars,output_vars)        
        
    def run(self):
        self.outputs['image_data'] = self.inputs['image_data']

    def description(self):
        return str(
        "An Identity operation takes one input argument: "
        + "inputs['image_data'] (a 2d pixel array). "
        + "When Identity.run() is called, "
        + "it saves the same pixel array in outputs['image_data']. "
        )

