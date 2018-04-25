from collections import OrderedDict
from functools import partial

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkinter
from tkinter import Tk, \
Frame, Canvas, Button, Label, Entry, StringVar, OptionMenu, Scrollbar, Checkbutton
import numpy as np
#from matplotlib import pyplot as plt
#from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
import xrsdkit
from xrsdkit.fitting.xrsd_fitter import XRSDFitter
from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    populations=None,
    fixed_params=None,
    param_bounds=None,
    param_constraints=None,
    source_wavelength=None)
outputs = OrderedDict(
    populations=None,
    report=None,
    q_I_opt=None,
    success_flag=False)
        
class XRSDFitGUI(Operation):
    """Interactively fit a XRSD spectrum."""
    
    # TODO: make widgets resize when the main window is resized

    def __init__(self):
        super(XRSDFitGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.input_doc['populations'] = 'dict defining populations, xrsdkit format'
        self.output_doc['populations'] = 'populations with parameters optimized'
        self.output_doc['success_flag'] = 'Boolean indicating whether '\
            'or not the user was satisfied with the fit.'

    def run(self):
        self.q_I = self.inputs['q_I']
        self.populations = self.inputs['populations']
        self.src_wl = self.inputs['source_wavelength']
        self.pf = self.inputs['fixed_params']
        self.pb = self.inputs['param_bounds']
        self.pc = self.inputs['param_constraints']
        self.fit_report = None
        self.q_I_opt = None
        self.success_flag = False
        self.xrsd_fitter = XRSDFitter(self.q_I,self.populations,self.src_wl)

        self.fit_gui = Tk()
        self.fit_gui.title('xrsd profile fitter')
       
        # data structures for maintaining refs
        self.pop_frames = OrderedDict()
        self.pop_frame_rows = OrderedDict()
        self.structure_vars = OrderedDict()
        self.param_frames = OrderedDict()
        self.setting_frames = OrderedDict()
        self.site_frames = OrderedDict()
        self.specie_frames = OrderedDict()
        self.specie_param_frames = OrderedDict()
        self.new_site_frames = OrderedDict() 
        self.new_specie_frames = OrderedDict()
        self.new_pop_frame = None
        self.fitting_frame = None

        self.fit_report = None
        self.q_I_opt = None

        # create the plots
        self.build_plot_widgets()
        
        # create the widgets for population control
        self.build_entry_widgets()

        # start the tk loop
        self.fit_gui.mainloop()

        # after tk loop exits, finish Operation
        self.finish() 

    def build_plot_widgets(self):
        self.plot_frame = Frame(self.fit_gui,bd=4,relief=tkinter.SUNKEN)#, background="green")
        self.plot_frame.pack(side=tkinter.LEFT, expand=tkinter.YES,padx=2,pady=2)

        self.fig = Figure(figsize=(8,7))
        self.ax_plot = self.fig.add_subplot(111)
        self.plot_canvas = FigureCanvasTkAgg(self.fig,self.plot_frame)
        self.plot_canvas.get_tk_widget().pack()
        self.draw_plots()

    def build_entry_widgets(self):
        self.scroll_frame = Frame(self.fit_gui)
        self.scroll_frame.pack(side=tkinter.RIGHT,fill='y')
        self.pops_canvas = Canvas(self.scroll_frame, width=450)
        self.scroll_frame.bind_all("<MouseWheel>", self.on_mousewheel)
        self.scroll_frame.bind_all("<Button-4>", self.on_trackpad)
        self.scroll_frame.bind_all("<Button-5>", self.on_trackpad)
        scr = Scrollbar(self.scroll_frame,orient='vertical',command=self.pops_canvas.yview)
        scr.pack(side=tkinter.RIGHT,fill='y')
        self.pops_frame = Frame(self.pops_canvas)
        scroll_canvas_config = lambda ev: self.pops_canvas.configure(scrollregion=self.pops_canvas.bbox("all"))
        self.pops_frame.bind("<Configure>",scroll_canvas_config)
        self.pops_frame.pack(side=tkinter.LEFT,fill='y')
        self.pops_canvas.create_window((0,0),window=self.pops_frame,anchor='nw')
        self.pops_canvas.configure(yscrollcommand=scr.set)
        self.pops_canvas.pack(side=tkinter.LEFT,fill='y')
        self.create_entry_widgets()

    def on_mousewheel(self, event):
        if event.delta == 0:
            # TODO: explain this
            event.delta += 100
        self.pops_canvas.yview_scroll(-1 * event.delta, 'units')

    def on_trackpad(self, event):
        if event.num == 4:
            d = -2
        elif event.num == 5:
            d = 2
        self.pops_canvas.yview_scroll(d, 'units')

    def finish(self):
        # TODO: check whether the user is satisfied with the result, 
        # and include this as an output or as a part of the report
        self.outputs['populations'] = self.populations
        self.outputs['report'] = self.fit_report
        self.outputs['q_I_opt'] = self.q_I_opt
        self.outputs['success_flag'] = self.success_flag

    def draw_plots(self):
        self.ax_plot.clear()
        #n_pops = len(self.populations)
        #if self.ax_plot is not None:
        #    self.fig.delaxes(self.ax_plot)
        #    #self.ax_plot.remove()
        #    self.ax_plot = None
        #self.ax_plot = plt.axes([0.08,0.05*(n_pops+2),0.45,0.9-0.05*(n_pops+2)])
        #self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        self.ax_plot.loglog(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = xrsdkit.scattering.compute_intensity(self.q_I[:,0],self.populations,self.src_wl)
        #self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.loglog(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.set_xlabel('q (1/Angstrom)')
        self.ax_plot.set_ylabel('Intensity (counts)')
        self.ax_plot.legend(['measured','computed'])
        self.plot_canvas.draw()

    def hi(self):
        print('test-test')

    def remove_population(self,pop_nm):
        self.destroy_pop_frame(pop_nm)
        self.populations.pop(pop_nm)
        self.draw_plots()
        self.repack_entry_widgets()

    def update_structure(self,pop_nm,var_nm,dummy,mode):
        s = self.structure_vars[pop_nm].get() 
        self.populations[pop_nm]['structure'] = s

        new_params = OrderedDict.fromkeys(xrsdkit.structure_params[s])
        for pnm in new_params: new_params[pnm] = xrsdkit.param_defaults[pnm]
        self.populations[pop_nm]['parameters'] = new_params
        self.destroy_param_frames(pop_nm)
        self.create_param_frames(pop_nm)

        new_settings = OrderedDict.fromkeys(xrsdkit.structure_settings[s])
        for snm in new_settings: new_settings[snm] = xrsdkit.setting_defaults[snm]
        self.populations[pop_nm]['settings'] = new_settings
        self.destroy_setting_frames(pop_nm)
        self.create_setting_frames(pop_nm)

        # if the new structure is crystalline, ensure coordinates are set
        # and ensure that noncrystalline form factors are not present
        new_basis = self.populations[pop_nm]['basis']
        if s in xrsdkit.crystalline_structure_names:
            for site_item_nm, site_def in new_basis.items():
                site_def_keys = list(site_def.keys())
                for nm in site_def_keys:
                    if nm in xrsdkit.noncrystalline_ff_names:
                        site_def.pop(nm) 
                if not 'coordinates' in site_def:
                    site_def['coordinates'] = [0.,0.,0.]
        self.draw_plots()
        self.destroy_site_frames(pop_nm)
        self.create_site_frames(pop_nm)

    #def _rename_population(self,old_name,new_name):
    #    popd = self.populations.pop(old_name)
    #    self.populations[new_name] = popd
    #    self.setup_plots()
    #    self.setup_populations()

    #def _new_population(self,new_pop_name):
    #    self.populations[new_pop_name] = OrderedDict()
    #    self.populations[new_pop_name]['structure'] = 'diffuse' 
    #    self.populations[new_pop_name]['parameters'] = OrderedDict()
    #    self.populations[new_pop_name]['basis'] = OrderedDict()
    #    self.setup_plots()
    #    self.setup_populations()

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




    def destroy_entry_widgets(self):
        pop_nm_list = list(self.pop_frames.keys())
        for pop_nm in pop_nm_list:
            self.destroy_pop_frame(pop_nm)
            self.structure_vars.pop(pop_nm)

    def destroy_pop_frame(self,pop_nm):
        self.destroy_setting_frames(pop_nm)
        self.destroy_param_frames(pop_nm)
        self.destroy_site_frames(pop_nm)
        popfrm = self.pop_frames.pop(pop_nm)
        popfrm.pack_forget()
        popfrm.destroy()

    def destroy_setting_frames(self,pop_nm):
        setting_nm_list = list(self.setting_frames[pop_nm].keys())
        for setting_nm in setting_nm_list:
            setting_frm = self.setting_frames[pop_nm].pop(setting_nm)
            setting_frm.pack_forget()
            setting_frm.destroy()

    def destroy_param_frames(self,pop_nm):
        param_nm_list = list(self.param_frames[pop_nm].keys())
        for param_nm in param_nm_list:
            param_frm = self.param_frames[pop_nm].pop(param_nm)
            param_frm.pack_forget()
            param_frm.destroy()

    def destroy_site_frames(self,pop_nm):
        site_nm_list = list(self.site_frames[pop_nm].keys())
        for site_nm in site_nm_list: 
            self.destroy_site_frame(pop_nm,site_nm)

    def destroy_site_frame(self,pop_nm,site_nm):
        self.destroy_specie_frames(pop_nm,site_nm)
        site_frm = self.site_frames[pop_nm].pop(site_nm)
        site_frm.pack_forget()
        site_frm.destroy()

    def destroy_specie_frames(self,pop_nm,site_nm):
        specie_nm_list = list(self.specie_frames[pop_nm][site_nm].keys())
        for specie_nm in specie_nm_list: 
            self.destroy_specie_frame(pop_nm,site_nm,specie_nm)

    def destroy_specie_frame(self,pop_nm,site_nm,specie_nm):
        specie_frms = self.specie_frames[pop_nm][site_nm][specie_nm]
        for ispec in range(len(specie_frms))[::-1]:
            self.destroy_specie_param_frames(pop_nm,site_nm,specie_nm,ispec)
            specie_frm = self.specie_frames[pop_nm][site_nm][specie_nm].pop(ispec)
            specie_frm.pack_forget()
            specie_frm.destroy()

    def destroy_specie_param_frames(self,pop_nm,site_nm,specie_nm,ispec):
        sparam_frms = self.specie_param_frames[pop_nm][site_nm][specie_nm][ispec]
        sparam_nm_list = list(self.specie_param_frames[pop_nm][site_nm][specie_nm][ispec].keys())
        for sparam_nm in sparam_nm_list:
            sparam_frm = sparam_frms.pop(sparam_nm)
            sparam_frm.pack_forget()
            sparam_frm.destroy()

    def create_entry_widgets(self):
        self.pop_frames = OrderedDict() 
        # create a frame for every population
        for ipop,pop_nm in enumerate(self.populations.keys()):
            self.create_pop_frame(ipop,pop_nm)
        #self.create_new_pop_frame()
        #self.create_control_frame()

    def create_pop_frame(self,ipop,pop_nm):
        popd = self.populations[pop_nm]
        pf = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED) 
        self.pop_frames[pop_nm] = pf

        popl = Label(pf,text='population name:',anchor='e')
        popl.grid(row=0,column=0,sticky=tkinter.E)
        pope = Entry(pf,width=20)
        pope.insert(0,pop_nm)
        pope.grid(row=0,column=1,sticky=tkinter.W)
        # TODO: connect entry to renaming population
        rmb = Button(pf,text='Remove',command=partial(self.remove_population,pop_nm))
        rmb.grid(row=0,column=2)

        strl = Label(pf,text='structure:',width=12,anchor='e')
        strl.grid(row=1,column=0,sticky=tkinter.E)
        strvar = StringVar(pf)
        str_option_dict = OrderedDict.fromkeys(xrsdkit.structure_names)
        strcb = OptionMenu(pf,strvar,*str_option_dict)
        strvar.set(popd['structure'])
        strvar.trace('w',partial(self.update_structure,pop_nm))
        strcb.grid(row=1,column=1,sticky=tkinter.W)
        self.structure_vars[pop_nm] = strvar

        self.create_setting_frames(pop_nm)
        self.create_param_frames(pop_nm)
        self.create_site_frames(pop_nm)
        pf.pack(side=tkinter.TOP,pady=2,padx=2)

    def create_setting_frames(self,pop_nm):
        self.setting_frames[pop_nm] = OrderedDict()
        pf = self.pop_frames[pop_nm]
        popd = self.populations[pop_nm]
        settingsl = Label(pf,text='------- SETTINGS -------')
        settingsl.grid(row=2,column=0,columnspan=3)
        for istg,stg_nm in enumerate(xrsdkit.structure_settings[popd['structure']]):
            stgf = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE) 
            self.setting_frames[pop_nm][stg_nm] = stgf
        
            stgl = Label(stgf,text='{}:'.format(stg_nm),width=12,anchor='e')
            stgl.grid(row=0,column=0,sticky=tkinter.E)
            stge = Entry(stgf,width=20)

            stg_val = xrsdkit.setting_defaults[stg_nm]
            if stg_nm in popd['settings']:
                stg_val = popd['settings'][stg_nm]
            stge.insert(0,str(stg_val))
            stge.grid(row=0,column=1,columnspan=2,sticky=tkinter.W)
            stgf.grid(row=3+istg,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)

    def create_param_frames(self,pop_nm):
        self.param_frames[pop_nm] = OrderedDict()
        pf = self.pop_frames[pop_nm]
        popd = self.populations[pop_nm]
        paramsl = Label(pf,text='------ PARAMETERS ------')
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        paramsl.grid(row=3+nstgs,column=0,columnspan=3)
        for ip,param_nm in enumerate(xrsdkit.structure_params[popd['structure']]):
            paramf = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE) 
            self.param_frames[pop_nm][param_nm] = paramf
            
            pl = Label(paramf,text='{}:'.format(param_nm),width=12,anchor='e')
            pl.grid(row=0,column=0,sticky=tkinter.E)
            pe = Entry(paramf,width=20)

            param_val = xrsdkit.param_defaults[param_nm]
            if param_nm in popd['parameters']:
                param_val = popd['parameters'][param_nm]
            pe.insert(0,str(param_val))
            pe.grid(row=0,column=1,columnspan=2,sticky=tkinter.W)

            psw = Checkbutton(paramf,text="variable")
            varparam = not xrsdkit.fixed_param_defaults[param_nm]
            # TODO: check for param in fixed_params 
            if varparam: psw.select()
            psw.grid(row=0,column=3,sticky=tkinter.W)
            pbndl = Label(paramf,text='bounds:',width=10,anchor='e')
            pbndl.grid(row=1,column=0,sticky=tkinter.E)
            pbnde1 = Entry(paramf,width=8) 
            pbnde2 = Entry(paramf,width=8)
            pbnde1.grid(row=1,column=1,sticky=tkinter.W) 
            pbnde2.grid(row=1,column=2,sticky=tkinter.W) 
            lbnd = xrsdkit.param_bound_defaults[param_nm][0]
            ubnd = xrsdkit.param_bound_defaults[param_nm][1] 
            # TODO: check for param in param_bounds 
            pbnde1.insert(0,str(lbnd))  
            pbnde2.insert(0,str(ubnd))
            pexpl = Label(paramf,text='expression:',width=10,anchor='e')
            pexpl.grid(row=2,column=0,sticky=tkinter.E)
            pexpe = Entry(paramf,width=16)
            # TODO: check for param in param_constraints 
            pexpe.grid(row=2,column=1,columnspan=3,sticky=tkinter.E+tkinter.W) 
            # TODO: connect pe to param entry
            # TODO: connect psw to changing fixed_params
            # TODO: connect pbnde to changing param_bounds
            # TODO: connect pexpe to setting param_constraints
            paramf.grid(row=4+nstgs+ip,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)

    def create_site_frames(self,pop_nm):
        self.site_frames[pop_nm] = OrderedDict()
        self.specie_frames[pop_nm] = OrderedDict()
        self.specie_param_frames[pop_nm] = OrderedDict()
        pf = self.pop_frames[pop_nm]
        popd = self.populations[pop_nm]
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        basisl = Label(pf,text='--------- BASIS ---------')
        basisl.grid(row=4+nstgs+npars,column=0,columnspan=3)
        for ist,site_nm in enumerate(popd['basis'].keys()):
            self.create_site_frame(pop_nm,site_nm,ist)
        # TODO: frame for adding a new site

    def create_site_frame(self,pop_nm,site_nm,ist):
        popd = self.populations[pop_nm] 
        pf = self.pop_frames[pop_nm] 
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        sitef = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE) 
        self.site_frames[pop_nm][site_nm] = sitef

        stl = Label(sitef,text='site name:',width=14,anchor='e')
        stl.grid(row=0,column=0,sticky=tkinter.E)
        ste = Entry(sitef,width=20)
        ste.insert(0,site_nm)
        ste.grid(row=0,column=1,columnspan=3,sticky=tkinter.W)
        rmb = Button(sitef,text='Remove')
        rmb.grid(row=0,column=4)
        # TODO: connect the entry to renaming the site 
        # TODO: connect rmb to deleting the site 

        site_def = popd['basis'][site_nm]
        if popd['structure'] in xrsdkit.crystalline_structure_names:
            coordl = Label(sitef,text='coordinates:',width=12,anchor='e')
            coorde1 = Entry(sitef,width=6)
            coorde2 = Entry(sitef,width=6)
            coorde3 = Entry(sitef,width=6)
            coordl.grid(row=1,column=0,sticky=tkinter.E)
            coorde1.grid(row=1,column=1)
            coorde2.grid(row=1,column=2)
            coorde3.grid(row=1,column=3)
            if 'coordinates' in site_def:
                c = site_def['coordinates']
            else:
                c = [0,0,0]
            coorde1.insert(0,str(c[0]))
            coorde2.insert(0,str(c[1]))
            coorde3.insert(0,str(c[2]))
            # TODO: connect the entries to setting the coordinates
            # TODO: controls for varying or constraining coords

        self.create_specie_frames(pop_nm,site_nm)
        sitef.grid(row=5+npars+nstgs+ist,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)

    def create_specie_frames(self,pop_nm,site_nm):
        self.specie_frames[pop_nm][site_nm] = OrderedDict()
        self.specie_param_frames[pop_nm][site_nm] = OrderedDict()
        popd = self.populations[pop_nm]
        site_def = popd['basis'][site_nm]
        for ispec, specie_nm in enumerate(site_def.keys()):
            if not specie_nm == 'coordinates':
                self.create_specie_frame(pop_nm,site_nm,specie_nm,ispec)
        # TODO: frame for adding a new specie

    def create_specie_frame(self,pop_nm,site_nm,specie_nm,ispec):
        self.specie_frames[pop_nm][site_nm][specie_nm] = []
        popd = self.populations[pop_nm]
        site_def = popd['basis'][site_nm]
        specie_def = site_def[specie_nm]
        if not isinstance(specie_def,list):
            specie_def = [specie_def]
        self.specie_param_frames[pop_nm][site_nm][specie_nm] = [OrderedDict() for specd in specie_def]
        sitef = self.site_frames[pop_nm][site_nm]
        for iispec,specd in enumerate(specie_def):
            specf = Frame(sitef,bd=2,padx=10,pady=4,relief=tkinter.GROOVE) 
            self.specie_frames[pop_nm][site_nm][specie_nm].append(specf)
            specl = Label(specf,text='specie:',width=12,anchor='e')
            specl.grid(row=0,column=0,sticky=tkinter.E)
            specvar = StringVar(sitef)
            spec_option_dict = OrderedDict.fromkeys(xrsdkit.form_factor_names)
            speccb = OptionMenu(specf,specvar,*spec_option_dict)
            specvar.set(specie_nm)
            speccb.grid(row=0,column=1,sticky=tkinter.W+tkinter.E)
            rmspecb = Button(specf,text='Remove')
            rmspecb.grid(row=0,column=2)
            # TODO: connect speccb to changing the specie
            # TODO: connect rmspecb to removing the specie
            self.create_specie_param_frames(pop_nm,site_nm,specie_nm,iispec)
            specf.grid(row=2+ispec+iispec,column=0,columnspan=5,pady=4,sticky=tkinter.E+tkinter.W)

    def create_specie_param_frames(self,pop_nm,site_nm,specie_nm,iispec):
        popd = self.populations[pop_nm]
        site_def = popd['basis'][site_nm]
        specie_def = site_def[specie_nm]
        if not isinstance(specie_def,list):
            specie_def = [specie_def]
        specd = specie_def[iispec]
        specief = self.specie_frames[pop_nm][site_nm][specie_nm][iispec]
        for isp,sparam_nm in enumerate(xrsdkit.form_factor_params[specie_nm]):
            sparf = Frame(specief,bd=2,padx=4,pady=4,relief=tkinter.GROOVE) 
            self.specie_param_frames[pop_nm][site_nm][specie_nm][iispec][sparam_nm] = sparf
            sparf.grid(row=1+isp,column=0,columnspan=3,sticky=tkinter.E+tkinter.W)
            sparl = Label(sparf,text='{}:'.format(sparam_nm),width=10,anchor='e')
            sparl.grid(row=0,column=0,sticky=tkinter.E)
            spare = Entry(sparf,width=16)
            sparam_val = xrsdkit.param_defaults[sparam_nm] 
            if sparam_nm in specd: sparam_val = specd[sparam_nm] 
            spare.insert(0,str(sparam_val))
            spare.grid(row=0,column=1,columnspan=2,sticky=tkinter.E+tkinter.W)
            sparsw = Checkbutton(sparf,text="variable")
            sparsw.grid(row=0,column=3,sticky=tkinter.W)
            sparvar = not xrsdkit.fixed_param_defaults[sparam_nm]
            # TODO: check for sparam in fixed_params 
            if sparvar: sparsw.select()
            sparbndl = Label(sparf,text='bounds:',width=10,anchor='e')
            sparbndl.grid(row=1,column=0,sticky=tkinter.E)
            sparbnde1 = Entry(sparf,width=8) 
            sparbnde2 = Entry(sparf,width=8)
            lbnd = xrsdkit.param_bound_defaults[sparam_nm][0]
            ubnd = xrsdkit.param_bound_defaults[sparam_nm][1] 
            # TODO: check for sparam in param_bounds 
            sparbnde1.insert(0,str(lbnd))  
            sparbnde2.insert(0,str(ubnd))
            sparbnde1.grid(row=1,column=1,sticky=tkinter.W) 
            sparbnde2.grid(row=1,column=2,sticky=tkinter.W) 
            sparexpl = Label(sparf,text='expression:',width=10,anchor='e')
            sparexpl.grid(row=2,column=0,sticky=tkinter.E)
            sparexpe = Entry(sparf,width=16) 
            # TODO: check for sparam in param_constraints 
            sparexpe.grid(row=2,column=1,columnspan=3,sticky=tkinter.E+tkinter.W) 
            # TODO: connect sparame to setting the param
            # TODO: connect sparsw to changing fixed_params
            # TODO: connect sparbnde to changing param_bounds
            # TODO: connect sparexpe to setting param_constraints

    def create_new_pop_frame(self):
        new_pop = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        new_pop.pack(side=tkinter.TOP,pady=2,padx=2, fill="both", expand=True)
        add_pop = Label(new_pop,text='add population:',anchor='e')
        add_pop.grid(row=0,column=0,sticky=tkinter.E)
        name = Entry(new_pop,width=20)
        name.insert(0,'unique name')
        name.grid(row=0,column=1,sticky=tkinter.W)
        add_button = Button(new_pop, text='Add', width = 10, command=self.hi)
        add_button.grid(row=0,column=2)

    def create_control_frame(self):
        fitting_control = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        fitting_control.pack(side=tkinter.TOP, pady=2,padx=2, fill="both", expand=True)
        error_weighted_box = Checkbutton(fitting_control,text="error weighted")
        error_weighted = True
        if error_weighted: error_weighted_box.select()
        error_weighted_box.grid(row=0,column=0)
        logI_weighted_box = Checkbutton(fitting_control, text="logI weighted")
        logI_weighted = True
        if logI_weighted: logI_weighted_box.select()
        logI_weighted_box.grid(row=0,column=1)
        #finish_button = Button(finish,text='Finish',command=partial(self.remove_population,pop_name))
        fit_button = Button(fitting_control,text='Fit',width = 10,  command=self.hi)
        fit_button.grid(row=0,column=2)
        obj = Label(fitting_control,text='obj:',anchor='e')
        obj.grid(row=1,column=0,sticky=tkinter.E)
        result = Entry(fitting_control,width=20)
        result.insert(0,'some number')
        result.grid(row=1,column=1,sticky=tkinter.W)

        finish = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        finish.pack(side=tkinter.TOP, pady=2,padx=2, fill="both", expand=True)
        fit = Checkbutton(finish,text="Good fit")
        if self.success_flag: fit.select()
        fit.grid(row=0,column=0)
        #finish_button = Button(finish,text='Finish',command=partial(self.remove_population,pop_name))
        finish_button = Button(finish,text='Finish',width = 10, command=self.hi)
        finish_button.grid(row=0,column=1)
        # TODO: frame for fitting controls: 
        #   # fit button, objective readout
        #   # toggles for logI-weighted and error-weighted
        #   # toggle for user satisfaction, button for finishing

    def repack_entry_widgets(self):
        for ipop,pop_nm in enumerate(self.populations.keys()):
            pf = self.pop_frames[pop_nm]
            pf.pack_forget()
            pf.pack(side=tkinter.TOP,pady=2,padx=2)
            self.repack_basis_widgets(pop_nm)

    def repack_basis_widgets(self,pop_nm):
        popd = self.populations[pop_nm]
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        for ist,site_nm in enumerate(popd['basis'].keys()):
            sitef = self.site_frames[pop_nm][site_nm]
            sitef.pack_forget()
            sitef.grid(row=5+npars+nstgs+ist,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)
            self.repack_site_widgets(pop_nm,site_nm)

    def repack_site_widgets(self,pop_nm,site_nm):
        popd = self.populations[pop_nm]
        site_def = popd['basis'][site_nm]
        for ispec, specie_nm in enumerate(site_def.keys()):
            if not specie_nm == 'coordinates':
                specie_def = site_def[specie_nm]
                if not isinstance(specie_def,list):
                    specie_def = [specie_def]
                for iispec,specd in enumerate(specie_def):
                    specf = self.specie_frames[pop_nm][site_nm][specie_nm][iispec]
                    specf.pack_forget()
                    specf.grid(row=2+ispec+iispec,column=0,columnspan=5,pady=4,sticky=tkinter.E+tkinter.W)


