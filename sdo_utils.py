from sunpy.net import Fido
from sunpy.net import attrs
import astropy
import astropy.units as U
import astropy.time as T
from sunpy.visualization.colormaps import color_tables as ct

import sunpy.map
import aiapy.data.sample as sample_data
from aiapy.calibrate import normalize_exposure, register, update_pointing
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def rescale(data, imin, imax, omin, omax):
    odif = omax-omin
    idif = imax-imin
    data = (data-imin)*(odif/idif) + omin
    return data.clip(omin, omax)

def bytescale(data, imin=None, imax=None):
    if not imin:
        imin = np.min(data)
    if not imax:
        imax = np.max(data)
    data = rescale(data, imin, imax, omin=0, omax=255)
    return data.astype(np.uint8)

def down_aia(start, end, wavelnth):
    start = T.Time(start)
    end = T.Time(end)

    TimeRange = attrs.Time(start=start, end=end, near=start)
    Provider = attrs.Provider('JSOC')
    Instrument = attrs.Instrument('AIA')
    Wavelength = attrs.Wavelength(wavelnth * U.angstrom)

    Q = Fido.search(TimeRange, Provider, Instrument, Wavelength)
    F = Fido.fetch(Q, progress=False)
    E = F.errors
    while len(E) > 0 :
        F = Fido.fetch(F, progress=False)
        E = F.errors
    return F

def down_hmi(start, end, wavelnth):
    start = T.Time(start) - 90/86400.
    end = T.Time(end) - 45/86400.

    TimeRange = attrs.Time(start=start, end=end, near=start)
    Provider = attrs.Provider('JSOC')
    Instrument = attrs.Instrument('HMI')
    Physobs = attrs.Physobs('INTENSITY')

    Q = Fido.search(TimeRange, Provider, Instrument, Physobs)
    F = Fido.fetch(Q, progress=False)
    E = F.errors
    while len(E) > 0 :
        F = Fido.fetch(F, progress=False)
        E = F.errors
    return F


def prep(file_fits):
    m = sunpy.map.Map(file_fits)
    if m.meta['INSTRUME'][:3].lower() == 'aia' :
        m_registered = register(m)
        m_normalized = normalize_exposure(m_registered)

    elif m.meta['INSTRUME'][:3].lower() == 'hmi' :
        data = m.data
        meta = m.meta
        w = np.where(np.isnan(data))
        data[w] = 0.
        m = sunpy.map.Map(data, meta)
        m_registered = register(m)
        meta = m_registered.meta
        data = m_registered.data
        psize = (4096 - data.shape[0])//2
        print(psize)
        data = np.pad(data, psize)
        m_normalized = sunpy.map.Map(data, meta)

    print(m_normalized.meta['WAVELNTH'], m.meta['CDELT1'], m_normalized.meta['CDELT1'], m_normalized.data.shape)
    return m_normalized

def get_colormap(m):
    if m.meta['INSTRUME'][:3].lower() == 'aia' :
        wavelnth = m.meta['WAVELNTH']
        cmap = ct.aia_color_table(wavelnth*U.angstrom)
    elif m.meta['INSTRUME'][:3].lower() == 'hmi' :
        cmap = matplotlib.cm.get_cmap('afmhot')
    return cmap

def get_image(file_fits):
    m = sunpy.map.Map(file_fits)
    cmap = get_colormap(m)
    data = m.data
    w = np.where(np.isnan(data))
    data[w] = 0.
    print(data.min(), data.max())
    data_new = aia_intscale() (data, m.meta['wavelnth'])
    image = cmap(data_new)
    return image

class aia_intscale():
    def aia_rescale(self, data, wave):
        self.wavelnth = str(wave)
        if self.wavelnth == '94':
            data = np.sqrt((data*4.99803).clip(1.5, 50.))
        elif self.wavelnth == '131':
            data = np.log10((data*6.99685).clip(7.0, 1200.))
        elif self.wavelnth == '171':
            data = np.sqrt((data*4.99803).clip(10., 6000.))
        elif self.wavelnth == '193':
            data = np.log10((data*2.99950).clip(120., 6000.))
        elif self.wavelnth == '211':
            data = np.log10((data*4.99801).clip(30., 13000.))
        elif self.wavelnth == '304':
            data = np.log10((data*4.99941).clip(15., 600.))
        elif self.wavelnth == '335':
            data = np.log10((data*6.99734).clip(3.5, 1000.))
        elif self.wavelnth == '1600':
            data = (data*2.99911).clip(0., 1000.)
        elif self.wavelnth == '1700':
            data = (data*1.00026).clip(0., 2500.)
        elif self.wavelnth == '4500':
            data = (data*1.00026).clip(0., 26000.)
        elif self.wavelnth == '6173' :
            data = data.clip(0, 65535)
        data = bytescale(data)
        return data
    def __call__(self, data, wave):
        data = self.aia_rescale(data, wave)
        return data



if __name__ == '__main__' :

    from glob import glob
    import os
    from sunpy.map import Map

    start = '2013-11-05T00:00:00.000'
    end = '2013-11-05T00:00:59.999'

    start = T.Time(start) - 90/86400.
    end = T.Time(end) - 45/86400.

    TimeRange = attrs.Time(start=start, end=end, near=start)
    Provider = attrs.Provider('JSOC')
    Instrument = attrs.Instrument('HMI')

    Q = Fido.search(TimeRange, Provider, Instrument)
    F = Fido.fetch(Q, progress=False)
    E = F.errors
    while len(E) > 0 :
        F = Fido.fetch(F, progress=False)
        E = F.errors



    # waves = [94, 131, 171, 193, 211, 304, 335, 1600, 1700, 4500]
    # for wave in waves :
    #     down_aia(start, end, wave)

    # down_hmi(start, end, wave)