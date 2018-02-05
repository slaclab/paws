from collections import OrderedDict
from functools import partial

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons 
import saxskit
from saxskit import saxs_math, saxs_fit
from saxskit.saxs_classify import SaxsClassifier
from saxskit.saxs_regression import SaxsRegressor 
from ... import Operation as opmod
from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    populations=None,
    params=None)
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
        self.input_doc['populations'] = 'Dict indicating the number of '\
            'each of a variety of potential scatterer populations (optional). '\
            'If not provided, the populations are estimated by saxskit.'
        self.input_doc['params'] = 'Dict of parameters '\
            'describing scattering characteristics of each population (optional). '\
            'If not provided, the parameters are estimated by saxskit.'
        self.output_doc['populations'] = 'The output `populations`, '\
            'as represented in the GUI when the Operation is finished.' 
        self.output_doc['params'] = 'The output `params`, '\
            'as represented in the GUI when the Operation is finished.' 
        self.output_doc['success_flag'] = 'Boolean indicating whether '\
            'or not the user was satisfied with the fit.'

    def run(self):
        self.q_I = self.inputs['q_I']
        self.feats = saxs_math.profile_spectrum(self.q_I)
        self.populations = self.inputs['populations']
        self.saxs_cls = SaxsClassifier()
        if self.populations is None:
            self.populations, certs = self.saxs_cls.classify(self.feats)
        self.params = self.inputs['params']
        self.saxs_reg = SaxsRegressor()
        self.saxs_fitter = saxs_fit.SaxsFitter(self.q_I,self.populations)
        if self.params is None:
            self.params = self.predict_params()
        self.setup_plots()
        self.pop_axes = OrderedDict()
        self.pop_sliders = OrderedDict()
        self.param_axes = OrderedDict()
        self.param_sliders = OrderedDict()
        self.ax_fit_btn = None
        self.ax_success_btn = None
        self.ax_finish_btn = None
        self.fit_btn = None
        self.finish_btn = None
        self.success_btn = None
        self.setup_populations()
        self.reset_params()
        plt.show()

    def finish(self,event):
        self.outputs['populations'] = self.populations
        self.outputs['params'] = self.params
        self.outputs['success_flag'] = self._success_flag
        plt.close()

    def setup_plots(self):
        n_pops = len(self.populations)
        self.fig = plt.figure(figsize=(15,8))
        self.ax_plot = plt.axes([0.15,0.05*(n_pops+2),0.45,0.9-0.05*(n_pops+2)])
        self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = saxs_math.compute_saxs(self.q_I[:,0],self.populations,self.params)
        self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.set_xlabel('q (1/Angstrom)')
        self.ax_plot.set_ylabel('Intensity (counts)')
        self.ax_plot.legend(['measured','estimated'])

    def setup_populations(self):
        self.ax_btn = plt.axes([0.15,0.07,0.1,0.16],facecolor = 'white')
        self.ax_btn.axis('off')
        self.btns = RadioButtons(self.ax_btn, 
            ['identified','unidentified'], active=0, activecolor='red')
        self.btns.on_clicked(self._set_unidentified)
        if bool(self.populations['unidentified']):
            self.set_active(1)
            self._set_unidentified()
        self.pop_sliders = OrderedDict() 
        self.pop_axes = OrderedDict()
        max_pop = 5
        for ip, pop_name in enumerate(saxskit.population_keys):
            if not pop_name == 'unidentified':
                ax_pop = plt.axes([0.35,0.04*(1.5+ip),0.2,0.02],facecolor=slider_color)
                ax_pop.set_xticks(range(max_pop),True)
                sldr = Slider(ax_pop,pop_name,0.,max_pop,valinit=self.populations[pop_name],valfmt="%i")
                sldr.on_changed(partial(self._set_pop,pop_name))
                self.pop_axes[pop_name] = ax_pop
                self.pop_sliders[pop_name] = sldr

    def reset_params(self):
        for param_name,axs in self.param_axes.items():
            for ax in axs:
                self.fig.delaxes(ax)
        if self.ax_fit_btn is not None:
            self.fig.delaxes(self.ax_fit_btn)
        if self.ax_finish_btn is not None:
            self.fig.delaxes(self.ax_finish_btn)
        if self.ax_success_btn is not None:
            self.fig.delaxes(self.ax_success_btn)
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
                llim = saxs_fit.param_limits[param_name][0]
                ulim = saxs_fit.param_limits[param_name][1]
                vinit = val
                vfmt = "%.3f" 
                param_change_func = partial(self._set_param,param_name,ival)
                log_slider = param_name in ['r0_sphere','rg_gp','I0_floor',\
                    'G_gp','I0_sphere','I_pkcenter']\
                    and not vinit < llim\
                    and not vinit < 1.E-6
                if log_slider:
                    sldr_name = sldr_name + ' (log)' 
                    if llim <= 0.:
                        llim = 1.E-6
                    if ulim is None:
                        ulim = 1.E7
                    llim = np.log10(llim)
                    ulim = np.log10(ulim)
                    vinit = np.log10(vinit)
                    vfmt = "%.2e"
                    param_change_func = partial(self._set_param_logarithmic,param_name,ival)
                sldr = Slider(ax_param,sldr_name,
                    llim,ulim,valinit=vinit,valfmt=vfmt)
                if log_slider: 
                    sldr.valtext.set_text(sldr.valfmt % 10.**vinit)
                sldr.on_changed(param_change_func)
                self.param_axes[param_name].append(ax_param)
                self.param_sliders[param_name].append(sldr)
                ipar += 1
        self.ax_fit_btn = plt.axes([0.7,0.88-0.04*(1+ipar),0.2,0.03],facecolor='white')
        self.fit_btn = Button(self.ax_fit_btn,'Fit')
        self.fit_btn.on_clicked(self.fit)
        self.ax_success_btn = plt.axes([0.7,0.7-0.04*(1+ipar),0.12,0.18],facecolor='white')
        self.ax_success_btn.axis('off')
        self.success_btn = RadioButtons(self.ax_success_btn, 
            ['good fit','bad fit'], active=0, activecolor='red')
        self._success_flag = True
        self.success_btn.on_clicked(self._set_success_flag)
        self.ax_finish_btn = plt.axes([0.8,0.74-0.04*(1+ipar),0.1,0.1],facecolor='white')
        self.finish_btn = Button(self.ax_finish_btn,'Finish')
        self.finish_btn.on_clicked(self.finish)

    def fit(self,event):
        self.message_callback('fitting...')
        self.params,rpt = self.saxs_fitter.fit(self.params)
        self.reset_params()
        self.update_plots()
        self.message_callback('fit complete (obj:{})'.format(rpt['final_objective']))
        #I_opt = saxs_math.compute_saxs(self.q_I[:,0],self.populations,self.opt_params)
        #self.ax_plot.semilogy(self.q_I[:,0],I_opt,lw=2,color='green')
        #self.ax_plot.legend(['measured',
        #    'estimated (obj: {:.2f})'.format(rpt['initial_objective']),
        #    'fit (obj: {:.2f})'.format(rpt['final_objective'])])
        #self.ax_plot.redraw_in_frame()
        #for param_name,axs in self.param_axes.items():
        #    pars = self.opt_params[param_name]
        #    for ax,par in zip(axs,pars):
        #        ax.plot(par,0.,'r*')
        #        ax.redraw_in_frame()

    def _set_unidentified(self,label):
        if label == 'unidentified':
            if not bool(self.populations['unidentified']):
                self.populations['unidentified'] = 1
                for pop,sldr in self.pop_sliders.items():
                    sldr.set_val(0.)
        elif label == 'identified':
            if bool(self.populations['unidentified']):
                self.populations['unidentified'] = 0

    def _set_success_flag(self,label):
        if label == 'yes':
            self._success_flag = True
        elif label == 'no':
            self._success_flag = False

    def _set_pop(self,pop_name,val):
        s = self.pop_sliders[pop_name]
        s.val = int(round(val))
        s.poly.xy[2] = s.val,1
        s.poly.xy[3] = s.val,0
        s.valtext.set_text(s.valfmt % s.val)
        self.set_population(pop_name,s.val)
        #dp = self.predict_params()
        #self.params = saxs_fit.update_params(dp,self.params)

    def set_population(self,pop_name,val):
        self.populations[pop_name] = int(val)
        self.saxs_fitter = saxs_fit.SaxsFitter(self.q_I,self.populations)
        self.params = self.predict_params()
        self.reset_params()
        self.update_plots()

    def _set_param(self,param_name,val_idx,val):
        self.params[param_name][val_idx] = val
        self.update_plots()

    def _set_param_logarithmic(self,param_name,val_idx,val):
        self.params[param_name][val_idx] = 10.**val
        self.update_plots()
        s = self.param_sliders[param_name][val_idx]
        s.valtext.set_text(s.valfmt % 10.**val)

    def predict_params(self):
        p = self.saxs_reg.predict_params(self.populations,self.feats,self.q_I)
        if bool(self.populations['diffraction_peaks']):
            p = self.saxs_fitter.estimate_peak_params(p)
        p,r = self.saxs_fitter.fit_intensity_params(p)
        return p

    def update_plots(self):
        self.ax_plot.clear()
        self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = saxs_math.compute_saxs(self.q_I[:,0],self.populations,self.params)
        self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.legend(['measured','computed'])
        self.ax_plot.redraw_in_frame()


