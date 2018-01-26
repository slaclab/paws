from collections import OrderedDict
from functools import partial

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider 
from saxskit import saxs_math, saxs_fit
from saxskit.saxs_classify import SaxsClassifier
from saxskit.saxs_regression import SaxsRegressor 
from ... import Operation as opmod
from ...Operation import Operation

inputs = OrderedDict(q_I=None)
outputs = OrderedDict(
    populations=None,
    params=None,
    success_flag=False)

class SpectrumFitGUI(Operation):
    """Interactively fit a SAXS spectrum."""

    def __init__(self):
        super(SpectrumFitGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.output_doc['populations'] = 'Dict indicating the number of '\
            'each of a variety of potential scatterer populations.'
        self.output_doc['params'] = 'Dict of parameters '\
            'describing each population.'
        self.output_doc['success_flag'] = 'Boolean indicating whether '\
            'or not the user was satisfied with the fit.'

    def run(self):
        slider_color = 'blue'

        self.q_I = self.inputs['q_I']
        self.feats = saxs_math.profile_spectrum(q_I)
        saxs_cls = SaxsClassifier()
        self.pops, certs = saxs_cls.classify(feats)
        self.saxs_reg = SaxsRegressor()
        params = self.predict_params()
        n_pops = len(self.pops)
        n_params = len(self.params)

        fig,ax = plt.subplots(figsize=(20,10))
        plt.subplots_adjust(left=0.1,bottom=0.05*(n_pops+2))
        meas = plt.semilogy(q_I[:,0],q_I[:,1],lw=2,color='black')
        est = plt.semilogy(q_I[:,0],q_I[:,1],lw=2,color='red')
        #fit = plt.semilogy(q_I[:,0],q_I[:,1],lw=2,color='green')

        self.pop_sliders = OrderedDict() 
        self.pop_axes = OrderedDict()
        for ip, pop in enumerate(pops.keys()):
            ax_pop = plt.axes([0.25,0.05*(1+ip),0.6,0.03],facecolor=slider_color)
            sldr = Slider(ax_pop,pop,0.,5.,valinit=pops[pop],valfmt="%i")
            sldr.on_changed(partial(self.set_slider,pop))
            self.pop_axes[pop] = ax_pop
            self.pop_sliders[pop] = append(sldr)

        self.param_sliders = OrderedDict() 
        self.param_axes = OrderedDict()
        self.refresh_params(params)

        plt.show()

    def refresh_params(self,params=None):
        if params is None:
            params = self.predict_params()
        self.param_axes = OrderedDict()
        ipar = 0
        for param_name,vals in params.items():
            self.param_axes[param_name] = []
            for val in vals:
                ax_param = plt.axes([0.75,0.05*(1+ipar),1.2,0.03],facecolor=slider_color) 
                self.param_axes[param_name].append(ax_param)
                ipar += 1
        plt.show()

    def predict_params(self):
        self.saxs_reg.predict_params(self.pops,self.feats,self.q_I)

    def set_slider(self,pop,val):
        s = self.sliders[pop]
        s.val = round(val)
        s.poly.xy[2] = s.val,1
        s.poly.xy[3] = s.val,0
        s.valtext.set_text(s.valfmt % s.val)
        self.populations[pop] = val


