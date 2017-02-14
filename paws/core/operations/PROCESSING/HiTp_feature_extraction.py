"""
Created on Mon Jun 06 18:02:32 2016

author: Fang Ren, Apurva Mehta
For details, refer to the recent paper submitted to ACS Combinatorial Science
Fang Ren implemented all the methods on scripting level, and originally contributed to slacx

Contributor: fangren (please add if there is more)
"""


import numpy as np

from ..operation import Operation
from .. import optools

class IntensityFeatures(Operation):
    """
    Extract the maximum intensity, average intensity, and a ratio of the two from data
    """

    def __init__(self):
        input_names = ['I']
        output_names = ['Imax', 'Iave', 'Imax_Iave_ratio']
        super(IntensityFeatures, self).__init__(input_names, output_names)
        self.input_doc['I'] = 'A 1d vector representing the intensity spectrum'
        self.input_src['I'] = optools.wf_input
        self.output_doc['Imax'] = 'The maximum intensity '
        self.output_doc['Iave'] = 'The average intensity'
        self.output_doc['Imax_Iave_ratio'] = 'The ratio of maximum to average intensity'

    def run(self):
        Imax = np.max(self.inputs['I'])
        Iave = np.mean(self.inputs['I'])
        ratio = Imax/Iave
        self.outputs['Imax'] = Imax
        self.outputs['Iave'] = Iave
        self.outputs['Imax_Iave_ratio'] = ratio

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
        self.input_src['q'] = optools.wf_input
        self.input_src['chi'] = optools.wf_input
        self.input_src['I'] = optools.wf_input 
        self.input_type['q'] = optools.ref_type
        self.input_type['chi'] = optools.ref_type
        self.input_type['I'] = optools.ref_type 
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

class PeakFeatures(Operation):
    """
    Extract the locations and intensities of peaks from a 1D spectrum
    """
    def __init__(self):
        input_names = ['q', 'I', 'delta_I']
        output_names = ['q_pk', 'I_pk']
        super(PeakFeatures,self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d vector for x-axis of spectrum, named q for momentum transfer vector'
        self.input_doc['I'] = '1d vector for spectral intensities at q values'
        self.input_doc['delta_I'] = str('Criterion for peak finding: point is a maximum '
            + 'that is more than delta-I larger than the next-lowest point')
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['delta_I'] = optools.text_input
        self.input_type['delta_I'] = optools.float_type
        self.inputs['delta_I'] = 0.0
        self.output_doc['q_pk'] = 'q values of found peaks'
        self.output_doc['I_pk'] = 'intensities of found peaks'

    def run(self):
        maxtab, mintab = self.get_extrema(self.inputs['q'], self.inputs['I'], self.inputs['delta_I'])
        q_pk = maxtab[:,0]
        I_pk = maxtab[:,1] 
        # save results to self.outputs
        self.outputs['q_pk'] = q_pk 
        self.outputs['I_pk'] = I_pk 

    def get_extrema(x, y, delta):
        """Given vectors x and y, return an n-by-2 array of x,y pairs for the minima and maxima of y(x)"""
        maxtab = []
        mintab = []
        x = np.array(x)
        y = np.array(y)
        y_min, y_max = np.Inf, -np.Inf
        x_min, x_max = np.NaN, np.NaN
        for i in arange(len(y)):
            if y[i] > y_max:
                x_max = x[i]
                y_max = y[i] 
            if y[i] < y_min:
                x_min = x[i]
                y_min = y[i] 
            lookformax = True
            if lookformax:
                if y[i] < y_max-delta:
                    maxtab.append((x_max, y_max))
                    y_min = y[i] 
                    x_min = x[i]
                    lookformax = False
            else:
                if y[i] > y_min+delta:
                    mintab.append((x_min, y_min))
                    y_max = y[i] 
                    x_max = x[i]
                    lookformax = True
        return np.array(maxtab), np.array(mintab)


class FindPeaksByWindow(Operation):
    """
    Walk a 1d array and find its local maxima.
    A maximum is found if it is the highest point within windowsize of itself.
    An optional threshold for the peak intensity relative to the window-average
    can be used to filter out peaks due to noise.
    """

    def __init__(self):
        input_names = ['x','y','windowsize','threshold']
        output_names = ['pk_idx','x_pk','y_pk']
        super(FindPeaksByWindow,self).__init__(input_names, output_names)
        self.input_doc['x'] = '1d array of x values (domain- optional)'
        self.input_doc['y'] = '1d array of y values (amplitudes)'
        self.input_doc['windowsize'] = 'the window is this many points in either direction of a given point'
        self.input_doc['threshold'] = 'threshold on Ipk/I(window) for being counted as a peak: set to zero to deactivate'
        self.input_src['x'] = optools.wf_input
        self.input_src['y'] = optools.wf_input
        self.input_src['windowsize'] = optools.text_input
        self.input_src['threshold'] = optools.text_input
        self.input_type['x'] = optools.ref_type
        self.input_type['y'] = optools.ref_type
        self.input_type['windowsize'] = optools.int_type
        self.input_type['threshold'] = optools.float_type
        self.inputs['windowsize'] = 10
        self.inputs['threshold'] = 0 
        self.output_doc['pk_idx'] = 'q values of found peaks'
        self.output_doc['x_pk'] = 'x values of found peaks'
        self.output_doc['y_pk'] = 'y values of found peaks'

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        w = self.inputs['windowsize']
        thr = self.inputs['threshold']
        pk_idx = []
        for idx in range(w,len(y)-w-1):
            pkflag = False
            ywin = y[idx-w:idx+w+1]
            if np.argmax(ywin) == w:
                if thr:
                    pkflag = ywin[w]/np.mean(ywin) > thr
                else:
                    pkflag = True
            if pkflag:
                pk_idx.append(idx)
        self.outputs['pk_idx'] = np.array(pk_idx)
        self.outputs['x_pk'] = np.array([x[idx] for idx in pk_idx])
        self.outputs['y_pk'] = np.array([y[idx] for idx in pk_idx])
    
