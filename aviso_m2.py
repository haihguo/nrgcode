"""This script generates the AVISO surface velocity time series at the M2 location used in the manuscript."""

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as si
import scipy.signal as sg
import xarray as xr
from band.lineartrend import callt
from pathlib import Path

aviso_path = r'D:\Data\data\NRG\aviso\monthly\*.nc'
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)
colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 'k']

dss = xr.open_mfdataset(aviso_path)
window = sg.windows.hann(12)
window = window / np.sum(window)
ds1 = dss.interp(longitude=150, latitude=39)
time = ds1.time
data = ds1.ugos.values
data1 = si.convolve(data, window, mode='mirror')

fig, ax = plt.subplots(1, 1, figsize=(7, 4))
ax.plot(time, data1, color='k', lw=1.5)
t1 = 120
mean1 = np.mean(data1[:t1])
mean2 = np.mean(data1[t1:])
ax.plot(time[:t1], mean1 * np.ones(t1), color=colors[0], lw=2)
ax.plot(time[t1:], mean2 * np.ones(len(time) - t1), color=colors[1], lw=2)
ax.set_xlabel('Time(year)')
ax.set_ylabel('u(m/s)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xlim(np.datetime64('1993-01-01'), np.datetime64('2025-04-30'))
tr, pv, od, co = callt(np.arange(len(data1)), data1)
ax.plot(time, od, color='#4daf4a')

plt.savefig(outdir / 'aviso_m2.pdf', bbox_inches='tight')
plt.savefig(outdir / 'aviso_m2.jpg', dpi=300, bbox_inches='tight')
plt.show()
