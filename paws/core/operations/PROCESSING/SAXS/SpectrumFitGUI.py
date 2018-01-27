from collections import OrderedDict
from functools import partial

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, RadioButtons 
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
        
slider_color = 'blue'

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
        self.q_I = self.inputs['q_I']
        self.feats = saxs_math.profile_spectrum(self.q_I)
        saxs_cls = SaxsClassifier()
        self.populations, certs = saxs_cls.classify(self.feats)
        self.saxs_reg = SaxsRegressor()
        self.params = self.predict_params()
        self.setup_plots()
        self.setup_populations()
        self.setup_params()
        plt.show()

    def setup_plots(self):
        n_pops = len(self.populations)
        self.fig = plt.figure(figsize=(15,8))
        self.ax_plot = plt.axes([0.15,0.05*(n_pops+2),0.45,0.95-0.05*(n_pops+2)])
        self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = saxs_math.compute_saxs(self.q_I[:,0],self.populations,self.params)
        self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.set_xlabel('q (1/Angstrom)')
        self.ax_plot.set_ylabel('Intensity (counts)')
        self.ax_plot.legend(['measured','estimated'])

    def setup_populations(self):
        n_pops = len(self.populations)
        self.ax_btn = plt.axes([0.1,0.1,0.1,0.1],facecolor = 'white')
        self.ax_btn.axis('off')
        self.btns = RadioButtons(self.ax_btn, ['identified','unidentified'], active=0, activecolor='red')
        self.btns.on_clicked(self.set_unidentified)
        if bool(self.populations['unidentified']):
            self.set_active(1)
            self.set_unidentified()
        self.pop_sliders = OrderedDict() 
        self.pop_axes = OrderedDict()
        for ip, pop_name in enumerate(self.populations.keys()):
            if not pop_name == 'unidentified':
                ax_pop = plt.axes([0.3,0.04*(1.5+ip),0.3,0.02],facecolor=slider_color)
                sldr = Slider(ax_pop,pop_name,0.,5.,valinit=self.populations[pop_name],valfmt="%i")
                sldr.on_changed(partial(self.set_pop,pop_name))
                self.pop_axes[pop_name] = ax_pop
                self.pop_sliders[pop_name] = sldr

    def setup_params(self):
        n_params = len(self.params)
        self.param_sliders = OrderedDict()
        self.param_axes = OrderedDict()
        ipar = 0
        for param_name,vals in self.params.items():
            self.param_axes[param_name] = []
            self.param_sliders[param_name] = []
            for ival,val in enumerate(vals):
                ax_param = plt.axes([0.7,0.9-0.04*(1+ipar),0.2,0.02],facecolor=slider_color) 
                sldr_name = param_name+str(ival)
                sldr = Slider(ax_param,sldr_name,
                    saxs_fit.param_limits[param_name][0],
                    saxs_fit.param_limits[param_name][1],
                    valinit=self.params[param_name][ival],
                    valfmt="%.3f")
                sldr.on_changed(partial(self.set_param,param_name,ival))
                self.param_axes[param_name].append(ax_param)
                self.param_sliders[param_name].append(sldr)
                ipar += 1

    def set_pop(self,pop_name,val):
        s = self.pop_sliders[pop_name]
        s.val = round(val)
        s.poly.xy[2] = s.val,1
        s.poly.xy[3] = s.val,0
        s.valtext.set_text(s.valfmt % s.val)
        self.populations[pop_name] = val

    def set_unidentified(self,label):
        if label == 'unidentified':
            if not bool(self.populations['unidentified']):
                self.populations['unidentified'] = 1
                for pop,sldr in self.pop_sliders.items():
                    sldr.set_val(0.)
        elif label == 'identified':
            if bool(self.populations['unidentified']):
                self.populations['unidentified'] = 0

    def set_slider(self,pop,val):
        s = self.sliders[pop]

    def set_param(self,param_name,val_idx,val):
        self.params[param_name][val_idx] = val
        self.update_plots()

    def update_plots(self):
        self.ax_plot.clear()
        self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = saxs_math.compute_saxs(self.q_I[:,0],self.populations,self.params)
        self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.redraw_in_frame()

    def predict_params(self):
        return self.saxs_reg.predict_params(self.populations,self.feats,self.q_I)


