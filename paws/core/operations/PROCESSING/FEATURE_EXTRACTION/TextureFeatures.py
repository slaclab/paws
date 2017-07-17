"""
Created on Mon Jun 06 18:02:32 2016

author(s): Fang Ren, Apurva Mehta
Module originally contributed by Fang Ren.
For details, refer to the recent paper submitted to ACS Combinatorial Science.
TODO: Get this citation
"""

import numpy as np

from ... import Operation as op
from ...Operation import Operation

class TextureFeatures(Operation):
    """
    Analyze the texture 
    """

    def __init__(self):
        input_names = ['q','chi','I']
        output_names = ['q_texture','texture','int_sqr_texture']
        super(TextureFeatures,self).__init__(input_names,output_names)
        self.input_doc['q'] = '1d array of momentum transfer values'
        self.input_doc['chi'] = '1d array of out-of-plane diffraction angles'
        self.input_doc['I'] = '2d array representing intensities at q,chi points'
        self.input_src['q'] = op.wf_input
        self.input_src['chi'] = op.wf_input
        self.input_src['I'] = op.wf_input 
        self.input_type['q'] = op.ref_type
        self.input_type['chi'] = op.ref_type
        self.input_type['I'] = op.ref_type 
        self.output_doc['q_texture'] = 'q values at which the texture is analyzed'
        self.output_doc['texture'] = 'quantification of texture for each q'
        self.output_doc['int_sqr_texture'] = 'integral over q of the texture squared'

    def run(self):
        q, chi = np.meshgrid(self.inputs['q'], self.inputs['chi']*np.pi/float(180))
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
        step = 0.01
        q_texture = np.arange(step,np.max(q)+step,step)
        tsqr_int = np.nansum(texture ** 2)/float(q_texture[-1]-q_texture[0])
        self.outputs['q_texture'] = q_texture
        self.outputs['texture'] = texture
        self.outputs['int_sqr_texture'] = tsqr_int 



