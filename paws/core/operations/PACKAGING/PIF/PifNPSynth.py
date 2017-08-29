import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class PifNPSynth(Operation):
    """
    Package results from nanoparticle solution synthesis into a pypif.obj.ChemicalSystem object.
    """

    def __init__(self):
        input_names = ['uid_prefix','date_time','t_utc','q_I','t_T','t_features','recipe']
        output_names = ['pif']
        super(PifNPSynth,self).__init__(input_names,output_names)
        self.input_doc['uid_prefix'] = 'text string to prepend to pif uid (pif uid = uid_prefix+t_utc'
        self.input_doc['date_time'] = 'string date/time from measurement header file, used for pif record tags'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities for saxs spectrum'
        self.input_doc['t_T'] = 'n-by-2 array of time (in seconds utc) and corresponding temperatures'
        self.input_doc['t_features'] = str('n-by-2 array of time (in seconds utc) '
        + 'and the corresponding dicts of spectral features, where the dicts are in the format of '
        + 'PROCESSING.SAXS.[SpectrumProfiler,SpectrumParameterization,SpectrumFit].outputs.features.')
        self.input_doc['recipe'] = 'dict describing recipe, in the format of IO.MISC.ReadNPSynthRecipe. Not yet implemented.'
        self.output_doc['pif'] = 'pif object representing the input data'
        self.input_type['uid_prefix'] = opmod.auto_type
        self.input_type['date_time'] = opmod.workflow_item
        self.input_type['t_utc'] = opmod.workflow_item
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['t_T'] = opmod.workflow_item
        self.input_type['t_features'] = opmod.workflow_item
        self.input_type['recipe'] = opmod.workflow_item
        # all inputs default to none: an empty pif should be produced in this case.
        self.inputs['uid_prefix'] = None
        self.inputs['date_time'] = None
        self.inputs['t_utc'] = None
        self.inputs['q_I'] = None
        self.inputs['t_T'] = None
        self.inputs['t_features'] = None
        self.inputs['recipe'] = None

    def run(self):
        uid_pre = self.inputs['uid_prefix']
        t_str = self.inputs['date_time']
        t_utc = self.inputs['t_utc']
        uid_full = 'tmp'
        if uid_pre is not None:
            uid_full = uid_pre
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        #temp_C = self.inputs['temp_C']
        q_I = self.inputs['q_I']
        t_T = self.inputs['t_T']
        t_f = self.inputs['t_features']
        rcp = self.inputs['recipe']
        # Subsystems for solution ingredients
        #colloid_sys = pifobj.ChemicalSystem(uid_pre+'_pd_colloid',['colloidal Pd nanoparticles'],None,None,None,'Pd') 
        #acid_sys = pifobj.ChemicalSystem(uid_pre+'_oleic_acid',['oleic acid'],None,None,None,'C18H34O2') 
        #amine_sys = pifobj.ChemicalSystem(uid_pre+'_oleylamine',['oleylamine'],None,None,None,'C18H35NH2') 
        #TOP_sys = pifobj.ChemicalSystem(uid_pre+'_trioctylphosphine',['trioctylphosphine'],None,None,None,'P(C8H17)3')
        #subsys = [colloid_sys,acid_sys,amine_sys,TOP_sys]
        # TODO: Quantity information for subsystems
        csys = pifobj.ChemicalSystem()
        csys.uid = uid_full
        #csys.sub_systems = subsys
        csys.properties = []
        csys.tags = []
        if uid_pre is not None:
            csys.tags.append('reaction id: '+uid_pre)
        if t_str is not None:
            csys.tags.append('date: '+t_str)
        if t_utc is not None:
            csys.tags.append('utc: '+str(int(t_utc)))

        if t_f is not None:
            # Grab the features at t_utc, else raise exception
            if t_utc in t_f[:,0]:
                f = t_f[:,1][list(t_f[:,0]).index(t_utc)]
            else:
                raise ValueError('utc time {} not found in t_f data ({})'
                .format(t_utc,t_f[:,0]))

            bflag = f['bad_data_flag']
            sflag = f['structure_flag']
            pflag = f['precursor_flag']
            fflag = f['form_flag']
            if bflag:
                csys.tags.append('unidentified scattering')
            if sflag:
                csys.tags.append('structure factor scattering')
            if fflag:
                csys.tags.append('precursor scattering')
            if pflag:
                csys.tags.append('form factor scattering')

        temp_C = None
        if t_T is not None:
            # Process time,temperature profile as a property
            it = (t_T[:,0] <= t_utc)
            t0 = t_T[0,0]
            t_T_current = np.array(t_T[it,:])
            t_T_current[:,0] = t_T_current[:,0] - t0
            csys.properties.append(self.time_feature_property(t_T_current,'temperature','degrees C'))
            # Grab the temperature at t_utc, else raise exception
            if t_utc in t_T[:,0]:
                temp_C = t_T[:,1][list(t_T[:,0]).index(t_utc)]
            else:
                raise ValueError('utc time {} not found in t_T data ({})'
                .format(t_utc,t_T[:,0]))

        if q_I is not None and temp_C is not None:
            # Process measured q_I into a property
            pI = self.saxs_pif_property(q_I)
            pI.conditions.append(pifobj.Value('temperature',[pifobj.Scalar(temp_C)],None,None,None,'degrees Celsius'))
            csys.properties.append(pI)
        elif q_I is not None:
            # Process measured q_I into a property
            pI = self.saxs_pif_property(q_I)
            csys.properties.append(pI)

        if t_f is not None:
            if fflag and not sflag and not bflag:
                csys.properties.append(self.feature_property(f['r0_form'],'nanoparticle mean radius','Angstrom'))
                csys.properties.append(self.feature_property(f['sigma_form'],'fractional standard deviation of nanoparticle radius',''))
                csys.properties.append(self.feature_property(f['I0_form'],'form factor scattering intensity prefactor','counts'))
            if pflag and not sflag and not bflag:
                csys.properties.append(self.feature_property(f['r0_pre'],'precursor effective radius','Angstrom'))
                csys.properties.append(self.feature_property(f['I0_pre'],'precursor scattering intensity prefactor','counts'))
            if not bflag and not sflag:
                csys.properties.append(self.feature_property(f['I_at_0'],'scattered intensity at q=0','counts'))
                # Compute the saxs spectrum, package it
                qI_computed = saxstools.compute_saxs(q_I[:,0],f)
                pI_computed = self.saxs_pif_property(np.array( [[q_I[i,0],qI_computed[i]] for i in range(len(qI_computed))] ))
                pI_computed.name = 'computed SAXS intensity'
                csys.properties.append(pI_computed)

        # Package features-vs-time up to now as properties
        if t_f is not None and not bflag:
            # Process time,features profile into properties
            #for fname in ['r0_form','sigma_form','I0_pre','I0_form','I_at_0']:
            bflags = np.array([fi['bad_data_flag'] for fi in t_f[:,1]],dtype=bool)
            pflags = np.array([fi['precursor_flag'] for fi in t_f[:,1]],dtype=bool)   
            sflags = np.array([fi['structure_flag'] for fi in t_f[:,1]],dtype=bool)   
            fflags = np.array([fi['form_flag'] for fi in t_f[:,1]],dtype=bool)   
            t0 = t_f[0,0]

            f_idx = np.where( (t_f[:,0]<=t_utc) & fflags & np.invert(sflags) & np.invert(bflags) )[0]
            if any(f_idx):
                t_r0 = np.array([[t_f[i][0],t_f[i][1]['r0_form']] for i in f_idx])
                t_r0[:,0] = t_r0[:,0] - t0 
                csys.properties.append(self.time_feature_property(t_r0,'nanoparticle mean radius vs. time','Angstrom'))
            
                t_sig = np.array([[t_f[i][0],t_f[i][1]['sigma_form']] for i in f_idx])
                t_sig[:,0] = t_sig[:,0] - t0 
                csys.properties.append(self.time_feature_property(t_sig,'fractional standard deviation of nanoparticle radius vs. time',''))

                t_I0form = np.array([[t_f[i][0],t_f[i][1]['I0_form']] for i in f_idx])
                t_I0form[:,0] = t_I0form[:,0] - t0 
                csys.properties.append(self.time_feature_property(t_I0form,'form factor scattering intensity prefactor vs. time','counts'))
                # Decide whether or not these are equilibrium features
                eqm_flag = None
                if t_utc-t0 == t_r0[-1,0] and t_r0.shape[1]>2:
                    tvals = t_r0[-3:,0]
                    r0vals = t_r0[-3:,1]
                    p = np.polyfit(tvals,r0vals,2)
                    dp = np.array([p[0]*2,p[1]])
                    dr0dt = np.polyval(dp,t_r0[-1,0])
                    eqm_flag = dr0dt < 0.01
                if eqm_flag is not None:
                    csys.tags.append('chemical equilibrium: {}'.format(eqm_flag))
                else: 
                    csys.tags.append('chemical equilibrium: unclear')
                
            p_idx = np.where( (t_f[:,0]<=t_utc) & pflags & np.invert(sflags) & np.invert(bflags) )[0]
            if any(p_idx):
                t_I0pre = np.array([[t_f[i][0],t_f[i][1]['I0_pre']] for i in p_idx])
                t_I0pre[:,0] = t_I0pre[:,0] - t0 
                csys.properties.append(self.time_feature_property(t_I0pre,'precursor scattering intensity prefactor vs. time','counts'))

            I0_idx = np.where( (t_f[:,0]<=t_utc) & np.invert(bflags) )[0]
            if any(I0_idx):
                t_I0 = np.array([[t_f[i][0],t_f[i][1]['I_at_0']] for i in I0_idx])
                t_I0[:,0] = t_I0[:,0] - t0 
                csys.properties.append(self.time_feature_property(t_I0,'scattered intensity at q=0 vs. time','counts'))

        self.outputs['pif'] = csys

    def feature_property(self,fval,fname,funits=''):
        pf = pifobj.Property()
        pf.name = fname
        pf.scalars = [pifobj.Scalar(fval)]
        if funits:
            pf.units = funits
        return pf

    def time_feature_property(self,t_f,fname,funits=''):
        pf = pifobj.Property()
        pf.name = fname 
        npts = t_f.shape[0]
        pf.scalars = [pifobj.Scalar(t_f[i,1]) for i in range(npts)]
        if funits:
            pf.units = funits 
        pf.conditions = []
        pf.conditions.append( pifobj.Value('reaction time',
                        [pifobj.Scalar(t_f[i,0]) for i in range(npts)],
                        None,None,None,'seconds') )
        return pf 

    #def time_temp_pif_property(self,t_T,t):
    #    ptT = pifobj.Property()
    #    ptT.name = 'time-temperature profile'
    #    it = (t_T[:,0] <= t)
    #    t0 = t_T[0,0]
    #    t_T_current = np.array(t_T[it,:])
    #    t_T_current[:,0] = t_T_current[:,0] - t0
    #    npts = t_T_current.shape[0]
    #    ptT.scalars = [pifobj.Scalar(t_T_current[i,1]) for i in range(npts)]
    #    ptT.units = 'degrees C'
    #    ptT.conditions = []
    #    ptT.conditions.append( pifobj.Value('reaction time',
    #                        [pifobj.Scalar(t_T_current[i,0]) for i in range(npts)],
    #                        None,None,None,'seconds') )
    #    return ptT

    def saxs_pif_property(self,q_I):
        pI = pifobj.Property()
        pI.name = 'SAXS intensity'
        n_qpoints = q_I.shape[0]
        pI.scalars = [pifobj.Scalar(q_I[i,1]) for i in range(n_qpoints)]
        pI.units = 'counts'
        pI.conditions = []
        pI.conditions.append( pifobj.Value('SAXS scattering vector', 
                            [pifobj.Scalar(q_I[i,0]) for i in range(n_qpoints)],
                            None,None,None,'1/Angstrom') )
        return pI 
        
#    def make_piftemperature(self,t):
#        v = pifobj.Value()
#        v.name = 'temperature'
#        tscl = pifobj.Scalar()
#        tscl.value = str(t)
#        v.scalars = [tscl]
#        v.units = 'degrees Celsius'
#        return v
#
#    def make_pifvector(self,v):
#        pifv = []
#        for n in v:
#            s = pifobj.Scalar()
#            s.value = str(n)
#            pifv.append(s)
#        return pifv
#
#    def pifscalar(self,scl,errlo,errhi):
#        s = pifobj.Scalar()
#        s.value = str(scl) 
#        s.minimum = str(scl) 
#        s.maximum = str(scl) 
#        s.inclusiveMinimum = True
#        s.inclusiveMaximum = True
#        s.uncertainty = '+{},-{}'.format(errlo,errhi)
#        s.approximate = True
#        return s


