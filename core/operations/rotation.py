import numpy as np

from core.operations.slacxop import Operation

class Rotation(Operation):

    def __init__(self):
        input_vars = ['image_data','rotation_deg']
        output_vars = ['image_data']
        super(Rotation,self).__init__(input_vars,output_vars)        

    def run(self):
        """Rotate self.input_vars['image_data'] and save as self.output_vars['image_data']"""
        # load self.inputs into local vars 
        img = self.inputs['image_data']
        rot_deg = self.inputs['rotation_deg']
        if rot_deg==90:
            img_rot = np.rot90(img)
        elif rot_deg==180:
            img_rot = np.rot90(np.rot90(img))
        elif rot_deg==270:
            img_rot = np.rot90(np.rot90(np.rot90(img)))
        else:
            msg = '[{}] expected rot_deg = 90, 180, or 270, got {}'.format(__name__,rot_deg)
            raise ValueError(msg)
        # save results to self.outputs
        self.outputs['image_data'] = img_rot

    def description(self):
        return str(
        "A Rotation operation takes two input arguments: "
        + "inputs['image_data'] (2d pixel array), "
        + "and inputs['rotation_deg'] (angle in degrees). "
        + "Calling run() populates the outputs['image_data'] "
        + "with a pixel array that is rotated CCW from the input. "
        + "Rotation angle must be 90, 180, or 270 degrees."
        )

