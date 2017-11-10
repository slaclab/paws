from collections import OrderedDict

import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_classify,saxs_fit 

inputs=OrderedDict(
    uid_prefix=None,
    t_utc=None,
    temperature=None,
    q_I=None,
    flags=None,
    params=None,
    report=None)
outputs=OrderedDict(pif=None)

class PifNPSolutionSAXS(Operation):
    """Build a PIF record for a nanoparticle solution SAXS experiment"""
    # TODO: include the scattering equation in this record somehow

    def __init__(self):
        super(PifNPSolutionSAXS,self).__init__(inputs,outputs)
        self.input_doc['uid_prefix'] = 'string for pif uid prefix '\
            '(pif uid = uid_prefix+t_utc), and also the '
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.input_doc['flags'] = 'dict of boolean flags indicating scatterer populations'
        self.input_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.input_doc['report'] = 'dict reporting key results '\
            'for the SAXS processing workflow, including fitting objectives, etc.'
        self.output_doc['pif'] = 'pif object representing the input data'
        self.input_type['t_utc'] = opmod.workflow_item
        self.input_type['temperature'] = opmod.workflow_item
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.input_type['params'] = opmod.workflow_item
        self.input_type['report'] = opmod.workflow_item

    def run(self):
        uid_pre = self.inputs['uid_prefix']
        t_utc = self.inputs['t_utc']
        uid_full = 'tmp'
        if uid_pre is not None:
            uid_full = uid_pre
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        temp_C = self.inputs['temperature']
        q_I = self.inputs['q_I']
        f = self.inputs['flags']
        p = self.inputs['params']
        r = self.inputs['report']

        # ChemicalSystem record construction begins here
        csys = pifobj.ChemicalSystem()
        csys.uid = uid_full
        csys.properties = []
        csys.tags = []
        csys.ids = []
        if uid_pre is not None:
            csys.ids.append(id_tag('EXPERIMENT_ID',uid_pre))
        if t_utc is not None:
            csys.tags.append('time (utc): '+str(int(t_utc)))

        if q_I is not None:
            # Process measured q_I into a property
            pI = q_I_property(q_I,temp_C)
            csys.properties.append(pI)

        if q_I is not None and p is not None and f is not None:
            if not f['bad_data'] and not f['diffraction_peaks']:
                I_computed = saxs_fit.compute_saxs(q_I[:,0],f,p)
                pI_computed = q_I_property(
                    np.array([q_I[:,0],I_computed]).T,
                    propname='computed SAXS intensity')
                csys.properties.append(pI_computed)

        if q_I is not None:
            # featurization of measured spectrum
            prof = saxs_fit.profile_spectrum(q_I)
            prof_props = profile_properties(prof)
            csys.properties.extend(prof_props)

            # ML flags for this featurization
            sxc = saxs_classify.SaxsClassifier()
            ml_flags = sxc.classify(np.array(list(prof.values())).reshape(1,-1))
            ml_flag_props = ml_flag_properties(ml_flags)
            csys.properties.extend(ml_flag_props)

        if f is not None:
            fprops = ground_truth_flag_properties(f)
            csys.properties.extend(fprops)

        if p is not None:
            pprops = param_properties(p)
            csys.properties.extend(pprops)

        if r is not None:
            rprops = fitreport_properties(p)
            csys.properties.extend(rprops)
        import pdb; pdb.set_trace()
        self.outputs['pif'] = csys

def id_tag(idname,idval,tags=None):
    return pifobj.Id(idname,idval,tags)

def q_I_property(q_I,temp_C=None,Iunits='arb',qunits='1/Angstrom',propname='SAXS intensity'):
    pI = pifobj.Property()
    n_qpoints = q_I.shape[0]
    pI.scalars = [pifobj.Scalar(q_I[i,1]) for i in range(n_qpoints)]
    pI.units = Iunits 
    pI.conditions = []
    pI.conditions.append( pifobj.Value('scattering vector', 
                        [pifobj.Scalar(q_I[i,0]) for i in range(n_qpoints)],
                        None,None,None,qunits) )
    if temp_C is not None:
        pI.conditions.append(pifobj.Value('temperature',
            [pifobj.Scalar(temp_C)],None,None,None,'degrees Celsius'))
    pI.name = propname 
    return pI 

def profile_properties(prof):
    props = []
    for fnm,fval in prof.items():
        props.append(scalar_property(
        fnm,fval,'','spectrum profiling quantity'))
    return props

def ml_flag_properties(ml_flags):
    props = []
    for fnm,fval in ml_flags.items():
        props.append(scalar_property(
            fnm+'_ML_flag',float(fval[0]),
            '{} ML flag'.format(fnm),'MACHINE_LEARNING'))
        props.append(scalar_property(
            fnm+'_ML_flag_prob',fval[1],
            '{} ML flag probability'.format(fnm),'MACHINE_LEARNING'))
    return props

def ground_truth_flag_properties(flags):
    props = []
    for fnm,fval in flags.items():
        props.append(scalar_property(
            fnm+'_flag',float(fval),
            '{} ground truth flag'.format(fnm),'EXPERIMENTAL'))
    return props

def param_properties(params):
    props = []
    if 'I0_floor' in params:
        props.append(scalar_property(
        'I0_floor',params['I0_floor'],
        'arb','flat background intensity','FIT'))
    if 'G_precursor' in params:
        props.append(scalar_property(
        'G_precursor',params['G_precursor'],
        'arb','precursor Guinier factor','FIT'))
    if 'rg_precursor' in params:
        props.append(scalar_property(
        'rg_precursor',params['rg_precursor'],
        'Angstrom','precursor radius of gyration','FIT'))
    if 'I0_sphere' in params:
        props.append(scalar_property(
        'I0_sphere',params['I0_sphere'],
        'arb','spherical scatterer intensity','FIT'))
    if 'r0_sphere' in params:
        props.append(scalar_property(
        'r0_sphere',params['r0_sphere'],
        'Angstrom','spherical scatterer mean radius','FIT'))
    if 'sigma_sphere' in params:
        props.append(scalar_property(
        'sigma_sphere',params['sigma_sphere'],
        '','fractional standard deviation of spherical scatterer radii','FIT'))
    return props

def fitreport_properties(r):
    props = []
    for rptnm,rptval in r.items():
        #if isinstance(rptval,float):
        props.append(scalar_property(
        rptnm,rptval,'','spectrum fitting quantity','FIT'))
    return props

def scalar_property(fname,fval,funits='',desc='',data_type=''):
    pf = pifobj.Property()
    pf.name = fname
    pf.scalars = [pifobj.Scalar(fval)]
    if funits:
        pf.units = funits
    if desc:
        pf.tags = [desc]
    if data_type:
        pf.dataType = data_type 
    return pf

