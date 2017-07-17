import numpy as np

from ... import Operation as op
from ...Operation import Operation

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
        self.input_src['x'] = op.wf_input
        self.input_src['y'] = op.wf_input
        self.input_src['windowsize'] = op.text_input
        self.input_src['threshold'] = op.text_input
        self.input_type['x'] = op.ref_type
        self.input_type['y'] = op.ref_type
        self.input_type['windowsize'] = op.int_type
        self.input_type['threshold'] = op.float_type
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
    

