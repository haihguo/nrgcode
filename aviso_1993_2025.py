"""This script generates the multi-panel AVISO map and M2 time-series figure used in the manuscript."""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as si
import scipy.signal as sg
import xarray as xr
from band.lineartrend import callt
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
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

lon1 = 143
lon2 = 153
lat1 = 30
lat2 = 43
colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 'k']

aviso_path = r'D:\Data\data\NRG\aviso\monthly\*.nc'
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

dss = xr.open_mfdataset(aviso_path)
lon = dss.longitude
lat = dss.latitude
lon_formatter = LongitudeFormatter(zero_direction_label=False)
lat_formatter = LatitudeFormatter()
myproj = ccrs.PlateCarree(central_longitude=(lon1 + lon2) / 2)

window = sg.windows.hann(12)
window = window / np.sum(window)
ds1 = dss.interp(longitude=150, latitude=39)
time = ds1.time
data = ds1.ugos.values
data1 = si.convolve(data, window, mode='mirror')
tr, pv, od, co = callt(np.arange(len(data1)), data1)

fig = plt.figure(figsize=(8, 8.5))
gs = gridspec.GridSpec(5, 2, hspace=0.8, wspace=0.3)

Lon, Lat = np.meshgrid(lon, lat)
levels_map = np.arange(-0.5, 0.501, 0.05)

tt = 132
ax1 = plt.subplot(gs[:3, 0], projection=myproj)
ugos1 = dss.ugos[:tt, :, :].mean('time')
vgos1 = dss.vgos[:tt, :, :].mean('time')
im1 = ax1.contourf(
    Lon,
    Lat,
    ugos1,
    cmap=plt.cm.RdBu_r,
    levels=levels_map,
    extend='both',
    transform=ccrs.PlateCarree(),
    antialiased=True,
)
ax1.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
xx = 4
q1 = ax1.quiver(
    Lon[::xx, ::xx],
    Lat[::xx, ::xx],
    ugos1.values[::xx, ::xx],
    vgos1.values[::xx, ::xx],
    zorder=10,
    transform=ccrs.PlateCarree(),
    scale=5,
    width=0.004,
    headwidth=3.5,
    alpha=0.85,
    color='k',
)
ax1.quiverkey(q1, X=0.85, Y=1.05, U=0.5, label='0.5 m s$^{-1}$', labelpos='E', fontproperties={'size': 11})
ax1.coastlines('50m', linewidth=0.8)
ax1.add_feature(cfeature.LAND, facecolor='#d3d3d3', edgecolor='k', zorder=5)
ax1.xaxis.set_major_formatter(lon_formatter)
ax1.yaxis.set_major_formatter(lat_formatter)
ax1.set_title('a', loc='left', fontweight='bold', fontsize=16)
ax1.set_xticks(np.arange(144, 154, 3), crs=ccrs.PlateCarree())
ax1.set_yticks(np.arange(30, 43, 2), crs=ccrs.PlateCarree())

ax2 = plt.subplot(gs[:3, 1], projection=myproj)
ugos2 = dss.ugos[tt:, :, :].mean('time')
vgos2 = dss.vgos[tt:, :, :].mean('time')
im2 = ax2.contourf(
    Lon,
    Lat,
    ugos2,
    cmap=plt.cm.RdBu_r,
    levels=levels_map,
    extend='both',
    transform=ccrs.PlateCarree(),
    antialiased=True,
)
ax2.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
q2 = ax2.quiver(
    Lon[::xx, ::xx],
    Lat[::xx, ::xx],
    ugos2.values[::xx, ::xx],
    vgos2.values[::xx, ::xx],
    zorder=10,
    transform=ccrs.PlateCarree(),
    scale=5,
    width=0.004,
    headwidth=3.5,
    alpha=0.85,
    color='k',
)
ax2.quiverkey(q2, X=0.85, Y=1.05, U=0.5, label='0.5 m s$^{-1}$', labelpos='E', fontproperties={'size': 11})
ax2.coastlines('50m', linewidth=0.8)
ax2.add_feature(cfeature.LAND, facecolor='#d3d3d3', edgecolor='k', zorder=5)
ax2.xaxis.set_major_formatter(lon_formatter)
ax2.yaxis.set_major_formatter(lat_formatter)
ax2.set_title('b', loc='left', fontweight='bold', fontsize=16)
ax2.set_xticks(np.arange(144, 154, 3), crs=ccrs.PlateCarree())
ax2.set_yticks(np.arange(30, 43, 2), crs=ccrs.PlateCarree())

cax = inset_axes(ax2, width='4%', height='100%', loc='lower left', bbox_to_anchor=(1.05, 0.0, 1, 1), bbox_transform=ax2.transAxes, borderpad=0)
cbar = fig.colorbar(im2, cax=cax)
cbar.set_ticks(np.arange(-0.5, 0.6, 0.25))
cbar.set_label('m s$^{-1}$', fontsize=12, fontweight='bold')

ax3 = plt.subplot(gs[3:, :])
ax3.plot(time, data1, color='k', lw=1.2, alpha=0.85)
mean1 = np.mean(data1[:tt])
mean2 = np.mean(data1[tt:])
ax3.plot(time[:tt], mean1 * np.ones(tt), color=colors[0], lw=2.5)
ax3.plot(time[tt:], mean2 * np.ones(len(time) - tt), color=colors[1], lw=2.5)
ax3.plot(time, od, color='#4daf4a', lw=2, ls='--')
ax3.axhline(0, color='gray', ls=':', lw=1.5)
ax3.set_title('c', loc='left', fontweight='bold', fontsize=16)
ax3.set_ylabel('u (m s$^{-1}$)', fontweight='bold')
ax3.set_xlabel('Year', fontweight='bold')
ax3.xaxis.set_major_locator(mdates.YearLocator(4))
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax3.set_xlim(np.datetime64('1993-01-01'), np.datetime64('2025-04-30'))
ax3.grid(ls='--', alpha=0.3)

plt.tight_layout()
plt.savefig(outdir / 'aviso_1993_2025.pdf', bbox_inches='tight')
plt.savefig(outdir / 'aviso_1993_2025.jpg', dpi=300, bbox_inches='tight')
plt.show()
