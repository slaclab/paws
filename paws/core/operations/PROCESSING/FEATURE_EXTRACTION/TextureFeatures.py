import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

class TextureFeatures(Operation):
    """
    Analyzes the texture of an integrated diffractogram
    (q, chi, and I(q,chi)).

    Created on Mon Jun 06 2016.
    
    Originally contributed by Fang Ren.
    Citation:
    Fang Ren, et al.
    ACS Comb. Sci., 2017, 19(6), pp 377-385.
    """

    def __init__(self):
        input_names = ['q','chi','I']
        output_names = ['q_texture','texture','int_sqr_texture']
        super(TextureFeatures,self).__init__(input_names,output_names)
        self.input_doc['q'] = '1d array of momentum transfer values'
        self.input_doc['chi'] = '1d array of out-of-plane diffraction angles'
        self.input_doc['I'] = '2d array representing intensities at q,chi points'
        self.input_type['q'] = opmod.workflow_item
        self.input_type['chi'] = opmod.workflow_item
        self.input_type['I'] = opmod.workflow_item 
        self.output_doc['q_texture'] = 'q values at which the texture is analyzed'
        self.output_doc['texture'] = 'quantification of texture for each q'
        self.output_doc['int_sqr_texture'] = 'integral over q of the texture squared'

    def run(self):
        q = self.inputs['q']
        chi = self.inputs['chi']
        I = self.inputs['I']
        if q is None or chi is None or I is None:
            return
        q, chi = np.meshgrid(q,chi*np.pi/float(180))
        keep = (self.inputs['I'] != 0)
        I = keep.astype(int) * self.inputs['I']
        # TODO: This appears to be a binning operation.
        # Maybe the bin size should not be hard-coded. 
        I_sum = np.bincount((q.ravel()*100).astype(int), I.ravel().astype(int))
        count = np.bincount((q.ravel()*100).astype(int), keep.ravel().astype(int))
        I_ave = np.array(I_sum)/np.array(count)
        texsum = np.bincount((q.ravel()*100).astype(int), (I*np.cos(chi)).ravel())
        chi_count = np.bincount((q.ravel()*100).astype(int), (keep*np.cos(chi)).ravel())
        texture = np.array(texsum) / np.array(I_ave) / np.array(chi_count) - 1
        # TODO: remove this hard code
        step = 0.01
        q_texture = np.arange(step,np.max(q)+step,step)
        tsqr_int = np.nansum(texture ** 2)/float(q_texture[-1]-q_texture[0])
        self.outputs['q_texture'] = q_texture
        self.outputs['texture'] = texture
        self.outputs['int_sqr_texture'] = tsqr_int 



