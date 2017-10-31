import numpy as np
import pyFAI

def radial_index(image_data,center_index):
    """Compute radial indices for an array about a given center.

    Parameters
    ----------
    image_data : array
        2d array of image data
    center_index : array 
        1d array containing two values: x and y indices 
        of the pixel to be used as the center of the image 
 
    Returns
    -------
    idx_rad : array
        array of integer radial indices for image_data
    """
    x, y = np.indices(image_data.shape)
    idx_rad = np.sqrt((x-center_index[0])**2+(y-center_index[1])**2)
    return idx_rad.astype(np.int)

def radial_pixel_bin(image_data, center_index, mask=None):
    """Compute the radial intensity profile of an image.

    Parameters
    ----------
    image_data : array
        2d array of image data
    center_index : array 
        1d array containing two values: x and y indices 
        of the pixel to be used as the center of image_data 
    mask : array, optional
        array of same shape as image_data,
        where a value of true indicates
        that the pixel is to be counted
 
    Returns
    -------
    idx_rad : array
        1d array of radial indices generated for the image
    I_rad : array
        1d array of intensity values corresponding to idx_rad 
    """
    if mask is None:
        mask = np.ones_like(image_data)
    dmsk = image_data * (mask)
    
    # index the image radially, then bin-count intensity
    r = radial_index(dmsk,center_index)
    I_rad = np.bincount(r.ravel(), dmsk.ravel())
    # normalize counted intensity by the number of contributing pixels
    npts = np.bincount(r.ravel(), (mask).ravel())
    I_rad = I_rad / npts
    return np.range(0,len(I_rad),1),I_rad 


def azimuthal_pixel_bin(image_data, center_pixel, r_idx_limits=None, mask=None, chires=30):
    if mask is None:
        mask = np.ones_like(image_data)
    
    r = radial_index(dmsk,center_index)
    #rmask = ((r>rlo) & (r<rhi) & (x < cen[0])).astype(np.int)
    # NOTE: LAP removed this x<center limit.
    # was it there to speed up x-symmetric processing?
    rmask = ((r>r_idx_limits[0]) & (r<r_idx_limits[1])).astype(np.int)
    mask *= rmask
    dmsk = image_data * (mask)

    chi = azimuthal_index()

    chi = chires * np.arctan((y - cen[1]) / (x - cen[0]))
    chi += chires * np.pi / 2.
    chi = np.round(chi).astype(np.int)
    chi *= (chi > 0)

    tbin = np.bincount(chi.ravel(), data.ravel())
    npts = np.bincount(chi.ravel(), rmask.ravel())
    I_chi = I_chi / npts 
    return np.range(0,len(I_chi),1),I_chi 

    # vimodel = pymodelfit.builtins.GaussianModel()
    # vimodel.mu = np.pi / 2 * 100
    # vimodel.A = np.nanmax(angleprofile)
    # vimodel.fitData(x=np.arange(np.size(angleprofile)), y=angleprofile, weights=angleprofile)
    # vimodel.plot(lower=0, upper=np.pi * 100)
    # print ('len:',len(angleprofile))

    #x, y = np.indices(data.shape).astype(np.float)
    #r = np.sqrt((x - center_pixel[0]) ** 2 + (y - center_pixel[1]) ** 2)
    #r = r.astype(np.int)


def radialintegratepyFAI(data, mask=None, AIdict=None, cut=None, color=[255, 255, 255], requestkey = None, q_norm = None, q_par = None, nq=None):
    AI = pyFAI.AzimuthalIntegrator()
    AI.setPyFAI(**AIdict)

    if mask is not None:
        mask = mask.copy()

    if not mask.shape == data.shape:
        mask = np.ones_like(data)

    if cut is not None and type(cut) is np.ndarray:
        mask = mask.astype(bool) & cut.astype(bool)

    (q, radialprofile) = AI.integrate1d(data.T, nbins, mask=1 - mask.T, method='cython')  #pyfai uses 0-valid mask
    q = q/10.
    #return q.tolist(), radialprofile.tolist(), color, requestkey


def chiintegratepyFAI(data, mask, AIdict, cut=None, color=[255, 255, 255], requestkey = None, q_norm = None, q_par = None, nq = None, nchi = None):
    AI = pyFAI.AzimuthalIntegrator()
    AI.setPyFAI(**AIdict)
    # Always do mask with 1-valid, 0's excluded

    if mask is not None:
        mask = mask.copy()


    if not mask.shape == data.shape:
        mask = np.ones_like(data)

    if cut is not None:
        mask &= cut.astype(bool)
    # data *= cut


    cake, q, chi = AI.integrate2d(data.T, xres, yres, method='cython')
    mask, q, chi = AI.integrate2d(mask.T, xres, yres, method='cython')

    maskedcake = np.ma.masked_array(cake, mask=mask<=0)

    chiprofile = np.ma.average(maskedcake, axis=1)

    return chi.tolist(), chiprofile.tolist(), color, requestkey

def xintegrate(data, mask, AIdict, cut=None, color=[255, 255, 255], requestkey = None, q_norm = None, q_par = None):
    if mask is not None:
        mask = mask.copy()


    if not mask.shape == data.shape:
        mask = np.ones_like(data)

    if cut is not None:
        mask &= cut.astype(bool)
    # data *= cut


    maskeddata = np.ma.masked_array(data, mask=1-mask)

    xprofile = np.ma.average(maskeddata, axis=1)

    AI = pyFAI.AzimuthalIntegrator()
    AI.setPyFAI(**AIdict)
    qx = AI.qArray(data.shape[::-1])[int(AI.getFit2D()['centerY']),:]/10
    qx[:qx.argmin()]*=-1

    return qx.tolist(), xprofile.tolist(), color, requestkey


def zintegrate(data, mask, AIdict, cut=None, color=[255, 255, 255], requestkey = None, q_norm = None, q_par = None):
    if mask is not None:
        mask = mask.copy()


    if not mask.shape == data.shape:
        mask = np.ones_like(data)

    if cut is not None:
        mask &= cut.astype(bool)
    # data *= cut


    maskeddata = np.ma.masked_array(data, mask=1-mask)

    xprofile = np.ma.average(maskeddata, axis=0)

    AI = pyFAI.AzimuthalIntegrator()
    AI.setPyFAI(**AIdict)
    qz = AI.qArray(data.shape[::-1])[:,int(AI.getFit2D()['centerX'])]/10
    qz[:qz.argmin()]*=-1

    return qz.tolist(), xprofile.tolist(), color, requestkey


def cake(imgdata, experiment, mask=None,  xres=None, yres=None):
    if mask is None:
        mask = np.zeros_like(imgdata)
    #AI = experiment.getAI()

    return AI.integrate2d(imgdata.T, xres, yres, mask=1-mask.T)


def GetArc(Imagedata, center, radius1, radius2, angle1, angle2):
    mask = np.zeros_like(Imagedata)

    centerx = center[0]
    centery = center[1]
    y, x = np.indices(Imagedata.shape)
    r = np.sqrt((x - centerx) ** 2 + (y - centery) ** 2)
    mask = (r > radius1) & (r < radius2)
    theta = np.arctan2(y - centery, x - centerx) / 2 / np.pi * 360
    mask &= (theta > angle1) & (theta < angle2)

    mask = np.flipud(mask)
    return mask * Imagedata

def qintegrate(*args,**kwargs):
    # if dimg.cakemode:
    #     return xintegrate(dimg.cake, cut, callbackcolor)
    # else:
    return radialintegratepyFAI(*args,**kwargs)

def cakexintegrate(data, mask=None, cut=None, q_norm = None, q_par = None, npts_chi = None):
    if mask is None: 
        mask = np.ones_like(data)
    if cut is not None:
        mask &= cut.astype(bool)

    chi = np.arange(-180,180,360./npts_chi)
    maskeddata = np.ma.masked_array(data, mask=1-mask)
    xprofile = np.ma.average(maskeddata, axis=1)

    return chi.tolist(), xprofile.tolist(), color, requestkey

def cakezintegrate(data, mask=None, cut=None, q_norm = None, q_par = None, npts_q=None):
    if mask is None: 
        mask = np.ones_like(data)
    if cut is not None:
        mask &= cut.astype(bool)
    q = np.arange(npts_q)*np.max(q_par)/ 10./npts_q

    maskeddata = np.ma.masked_array(data, mask=1-mask)
    zprofile = np.ma.average(maskeddata, axis=0)

    return q, zprofile

def calc_q_range(image_shape, pixel_shape, image_center, geom_pyfai, alpha_i):
    """Compute the q-range represented by an image, given geometric parameters.

    Parameters
    ----------
    image_shape : array
        array of two integers, representing 
        the horizontal and vertical image dimensions
    pixel_shape : array
        array of two floats, representing
        the horizontal and vertical pixel shape,
        in meters
    image_center : array
        array of two integers, representing
        the indices of the central pixel of the image
    geom_pyfai : PyFAI.Geometry
        a PyFAI.Geometry object 
        defining the sample/detector geometry.
    alpha_i : float
        beam-to-surface incident angle

    Returns
    -------
    q_range : array
        four floats representing the minima and maxima
        of the q-ranges represented by the image:
        [min(q_par),max(q_par),min(q_norm),max(q_norm)]
    """

    # PyFAI geometry params are in meters, radians 
    sdd = geom_pyfai.get_dist() 
    wavelen = geometry.get_wavelength() 
    pixel1 = geometry.get_pixel1() 
    pixel2 = geometry.get_pixel2() 

    # calculate q-range for the image
    y = np.array([0, image_shape[1] - 1], dtype=np.float) * pixel_shape[1] 
    z = np.array([0, image_shape[0] - 1], dtype=np.float) * pixel_shape[2]
    y, z = np.meshgrid(y, z)
    y -= cen[0]
    z -= cen[1]

    # calculate angles 
    tmp = np.sqrt(y ** 2 + sdd ** 2)
    cos2theta = sdd / tmp
    sin2theta = y / tmp
    tmp = np.sqrt(z ** 2 + y ** 2 + sdd ** 2)
    cosalpha = sdd / tmp
    sinalpha = z / tmp
    k0 = 2. * np.pi / wavelen

    # calculate q-values of each corner
    qx = k0 * (cosalpha * cos2theta - np.cos(alpha_i))
    qy = k0 * cosalpha * sin2theta
    qz = k0 * (sinalpha + np.sin(alpha_i))
    qp = np.sign(qy) * np.sqrt(qx ** 2 + qy ** 2)
    q_range = [qp.min(), qp.max(), qz.min(), qz.max()]
    return q_range

def remeshqarray(image, geometry, alpha_i):
    shape = image.shape
    center = np.zeros(2, dtype=np.float)
    pixel = np.zeros(2, dtype=np.float)

    # get calibrated parameters
    nanometer = 1.0E+09
    pixel[0] = geometry.get_pixel1() * nanometer
    pixel[1] = geometry.get_pixel2() * nanometer
    center[0] = geometry.get_poni2() * nanometer
    center[1] = shape[0] * pixel[0] - geometry.get_poni1() * nanometer

    # calculate q values
    qrange = calc_q_range(image.shape, geometry, alpha_i, center)

    # uniformly spaced q-values for remeshed image
    nqz = image.shape[0]
    dqz = (qrange[3] - qrange[2]) / (nqz - 1)
    nqp = np.int((qrange[1] - qrange[0]) / dqz)
    qvrt = np.linspace(qrange[2], qrange[3], nqz)
    qpar = qrange[0] + np.arange(nqp) * dqz
    qpar, qvrt = np.meshgrid(qpar, qvrt)

    return np.rot90(qpar, 3), np.rot90(qvrt, 3)


def remeshqintegrate(data, AIdict, mask=None, cut=None, q_norm = None, q_par = None, alpha_i = None):

    if q_norm is None or q_par is None:
        q_par, q_norm = remeshqarray(data, AI, np.deg2rad(alpha_i))
    
    AI = pyFAI.AzimuthalIntegrator()
    AI.setPyFAI(**AIdict)

    if mask is None:
        mask = np.ones_like(data)
    else:
        mask = mask.copy()
    if cut is not None:
        mask &= cut.astype(bool)

    #q_par, q_norm = remesh.remeshqarray(data, None, AI, np.deg2rad(alpha_i))
    qsquared=q_par**2 + q_norm**2
    remeshcenter=np.unravel_index(qsquared.argmin(),qsquared.shape)

    print 'center?:',remeshcenter

    f2d=AI.getFit2D()
    f2d['centerX']=remeshcenter[0]
    f2d['centerY']=remeshcenter[1]
    AI.setFit2D(**f2d)
    AIdict=AI.getPyFAI()

    AI._cached_array["q_center"]=np.sqrt(qsquared).T/10   # This is cheating! pyFAI may give unexpected results here

    (q, radialprofile) = AI.integrate1d(data.T, npts_q, mask=1 - mask.T, method='cython')  #pyfai uses 0-valid mask

    return q, radialprofile, color, requestkey

def remeshchiintegrate(data, AIdict, mask=None,cut=None, q_norm = None, q_par = None, alpha_i=None):
    AI = pyFAI.AzimuthalIntegrator()
    AI.setPyFAI(**AIdict)

    #alpha_i=config.activeExperiment.getvalue('Incidence Angle (GIXS)')

    qsquared=q_par**2 + q_norm**2

    remeshcenter=np.unravel_index(qsquared.argmin(),qsquared.shape)

    f2d=AI.getFit2D()
    f2d['centerX']=remeshcenter[0]
    f2d['centerY']=remeshcenter[1]
    AI.setFit2D(**f2d)
    AIdict=AI.getPyFAI()

    return chiintegratepyFAI(data,mask,AIdict,cut,color,requestkey, q_norm = None, q_par = None)

def remeshxintegrate(data, mask, AIdict, cut=None, color=[255, 255, 255], requestkey=None, q_norm = None, q_par = None):
    AI = pyFAI.AzimuthalIntegrator()
    AI.setPyFAI(**AIdict)

    if not mask.shape == data.shape:
        mask = np.ones_like(data)

    if cut is not None:
        mask &= cut.astype(bool)

    center = np.where(np.abs(q_par) == np.abs(q_par).min())
    qx = q_par[:,center[0][0]]/10.

    maskeddata = np.ma.masked_array(data, mask=1 - mask)
    xprofile = np.ma.average(maskeddata, axis=1)

    return qx.tolist(), xprofile.tolist(), color, requestkey

def remeshzintegrate(image_data, mask=None, cut=None, q_norm=None, q_par=None):

    if mask is None: 
        mask = np.ones_like(image_data)
    if cut is not None:
        mask &= cut.astype(bool)
    center = np.where(np.abs(q_norm) == np.abs(q_norm).min())
    qx = -q_norm[center[1][0]]#/10.

    maskeddata = np.ma.masked_array(data, mask=1 - mask)
    I_qx = np.ma.average(maskeddata, axis=0)

    return qx, I_qx 
