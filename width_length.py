"""This script generates the KE width-length figure used in the manuscript."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as si
import scipy.signal as sg
import xarray as xr
from cartopy.mpl.ticker import LatitudeFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pathlib import Path

plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'axes.linewidth': 1.2,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'font.family': 'sans-serif',
})

aviso_path = r'D:\Data\data\NRG\aviso\monthly\*.nc'
length_path = r'D:\Data\data\NRG\length.nc'
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

dss = xr.open_mfdataset(aviso_path)
lat_formatter = LatitudeFormatter()

window1 = sg.windows.hann(36)
window1 = window1 / np.sum(window1)
ugos = dss.ugos[:, :, 32:40].mean('longitude')
nt, ny = ugos.shape
data1 = ugos.values
data2 = data1.copy()
ugosm = ugos.copy()
for iy in range(ny):
    data2[:, iy] = si.convolve(data1[:, iy], window1, mode='mirror')
ugosm.values = data2

plt.figure()
cs = plt.contour(ugosm.time, ugosm.latitude, ugosm.T, levels=[0.1])
segments = cs.allsegs[0]
plt.close()
sorted_segments = sorted(segments, key=len, reverse=True)
if len(sorted_segments) < 3:
    raise ValueError('Fewer than three contour segments were found.')
second_longest = sorted_segments[1]
third_longest = sorted_segments[2]
xn = second_longest[:, 0]
yn = second_longest[:, 1]
xs = third_longest[:, 0]
ys = third_longest[:, 1]

dsl = xr.open_dataset(length_path)

fig, axes = plt.subplots(2, 1, figsize=(8, 7.5), sharex=True, gridspec_kw={'hspace': 0.12})
ax = axes[0]
im = ugosm.plot.contourf(
    ax=ax,
    levels=np.arange(-1.2, 1.201, 0.1),
    y='latitude',
    cmap='RdBu_r',
    extend='both',
    add_colorbar=False,
)
ax.plot(xn, yn, color='k', lw=1.5, ls='--')
ax.plot(xs, ys, color='k', lw=1.5, ls='--')
ax.set_ylabel('Latitude', fontweight='bold')
ax.set_xlabel('')
ax.yaxis.set_major_formatter(lat_formatter)
ax.set_title('a', loc='left', fontweight='bold', fontsize=16)
ax.set_title('', loc='center')
ax.set_title('', loc='right')
axins = inset_axes(ax, width='2.5%', height='100%', loc='lower left', bbox_to_anchor=(1.02, 0.0, 1, 1), bbox_transform=ax.transAxes, borderpad=0)
cbar = fig.colorbar(im, cax=axins, orientation='vertical')
cbar.set_ticks(np.arange(-1.2, 1.3, 0.4))
cbar.set_label('$u$ (m s$^{-1}$)', fontweight='bold')

ax = axes[1]
dsl.length.plot(ax=ax, color='#4575b4', lw=2, label='Path Length')
dsl.od.plot(ax=ax, color='#d73027', lw=2.5, label='Long-term Trend')
ax.set_ylabel('Distance (km)', fontweight='bold')
ax.set_xlabel('Year', fontweight='bold')
ax.set_title('b', loc='left', fontweight='bold', fontsize=16)
ax.set_title('', loc='center')
ax.legend(frameon=False, loc='upper right')
ax.xaxis.set_major_locator(mdates.YearLocator(4))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.grid(axis='y', ls='--', alpha=0.4)

plt.savefig(outdir / 'width_length.pdf', bbox_inches='tight')
plt.savefig(outdir / 'width_length.jpg', dpi=300, bbox_inches='tight')
plt.show()
