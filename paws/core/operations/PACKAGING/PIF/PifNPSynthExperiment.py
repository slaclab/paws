import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation

class PifNPSynthExperiment(Operation):
    """
    Analyze a series of PIFs generated in a nanoparticle synthesis experiment
    and produce a master PIF that describes the overall experiment. 
    """

    def __init__(self):
        input_names = ['pifs','recipe_file','reaction_id']
        output_names = ['master_pif']
        super(PifNPSynthExperiment,self).__init__(input_names,output_names)
        self.input_doc['pifs'] = 'list of pypif.obj.ChemicalSystem objects '\
        'describing a full nanoparticle synthesis experiment. '
        self.input_doc['recipe_file'] = 'path to a YAML file '\
        'describing the synthesis recipe with a set of standard keys (TODO: document). '
        self.input_doc['reaction_id'] = 'string identifying the reaction: '\
        'because this is used as the ChemicalSystem.uid, it must be unique '\
        'among the uids in the data set where the PIF will be stored.'
        self.output_doc['master_pif'] = 'pypif.obj.ChemicalSystem object '\
        'describing the overall experiment. '

    def run(self):
        pifs = self.inputs['pifs']
        rcpfile = self.inputs['recipe_file']
        rxnid = self.inputs['reaction_id']
        csys = pifobj.ChemicalSystem()
        csys.uid = rxnid 
        # Subsystems for solution ingredients
        # TODO: Quantity information for subsystems
        #if t_T is not None:
        #    # Process time,temperature profile as a property
        #    it = (t_T[:,0] <= t_utc)
        #    t0 = t_T[0,0]
        #    t_T_current = np.array(t_T[it,:])
        #    t_T_current[:,0] = t_T_current[:,0] - t0
        #    csys.properties.append(self.time_feature_property(t_T_current,'temperature','degrees C'))
        #    # Grab the temperature at t_utc, else raise exception
        #    if t_utc in t_T[:,0]:
        #        temp_C = t_T[:,1][list(t_T[:,0]).index(t_utc)]
        #    else:
        #        raise ValueError('utc time {} not found in t_T data ({})'
        #        .format(t_utc,t_T[:,0]))
        # Package features-vs-time up to now as properties
        #if t_f is not None and not bflag:
        #    # Process time,features profile into properties
        #    #for fname in ['r0_form','sigma_form','I0_pre','I0_form','I_at_0']:
        #    bflags = np.array([fi['bad_data_flag'] for fi in t_f[:,1]],dtype=bool)
        #    pflags = np.array([fi['precursor_flag'] for fi in t_f[:,1]],dtype=bool)   
        #    sflags = np.array([fi['structure_flag'] for fi in t_f[:,1]],dtype=bool)   
        #    fflags = np.array([fi['form_flag'] for fi in t_f[:,1]],dtype=bool)   
        #    t0 = t_f[0,0]

        #    f_idx = np.where( (t_f[:,0]<=t_utc) & fflags & np.invert(sflags) & np.invert(bflags) )[0]
        #    if any(f_idx):
        #        t_r0 = np.array([[t_f[i][0],t_f[i][1]['r0_form']] for i in f_idx])
        #        t_r0[:,0] = t_r0[:,0] - t0 
        #        csys.properties.append(self.time_feature_property(t_r0,'nanoparticle mean radius vs. time','Angstrom'))
        #    
        #        t_sig = np.array([[t_f[i][0],t_f[i][1]['sigma_form']] for i in f_idx])
        #        t_sig[:,0] = t_sig[:,0] - t0 
        #        csys.properties.append(self.time_feature_property(t_sig,'fractional standard deviation of nanoparticle radius vs. time',''))

        #        t_I0form = np.array([[t_f[i][0],t_f[i][1]['I0_form']] for i in f_idx])
        #        t_I0form[:,0] = t_I0form[:,0] - t0 
        #        csys.properties.append(self.time_feature_property(t_I0form,'form factor scattering intensity prefactor vs. time','counts'))
        #        # Decide whether or not these are equilibrium features
        #        eqm_flag = None
        #        if t_utc-t0 == t_r0[-1,0] and t_r0.shape[1]>2:
        #            tvals = t_r0[-3:,0]
        #            r0vals = t_r0[-3:,1]
        #            p = np.polyfit(tvals,r0vals,2)
        #            dp = np.array([p[0]*2,p[1]])
        #            dr0dt = np.polyval(dp,t_r0[-1,0])
        #            eqm_flag = dr0dt < 0.01
        #        if eqm_flag is not None:
        #            csys.tags.append('chemical equilibrium: {}'.format(eqm_flag))
        #        else: 
        #            csys.tags.append('chemical equilibrium: unclear')
        #        
        #    p_idx = np.where( (t_f[:,0]<=t_utc) & pflags & np.invert(sflags) & np.invert(bflags) )[0]
        #    if any(p_idx):
        #        t_I0pre = np.array([[t_f[i][0],t_f[i][1]['I0_pre']] for i in p_idx])
        #        t_I0pre[:,0] = t_I0pre[:,0] - t0 
        #        csys.properties.append(self.time_feature_property(t_I0pre,'precursor scattering intensity prefactor vs. time','counts'))

        #    I0_idx = np.where( (t_f[:,0]<=t_utc) & np.invert(bflags) )[0]
        #    if any(I0_idx):
        #        t_I0 = np.array([[t_f[i][0],t_f[i][1]['I_at_0']] for i in I0_idx])
        #        t_I0[:,0] = t_I0[:,0] - t0 
        #        csys.properties.append(self.time_feature_property(t_I0,'scattered intensity at q=0 vs. time','counts'))

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



