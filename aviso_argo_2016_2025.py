"""This script generates the AVISO and Argo circulation comparison figure used in the manuscript."""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from pathlib import Path

plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'axes.linewidth': 1.2,
    'font.family': 'sans-serif',
})

lon1 = 143
lon2 = 153
lat1 = 30
lat2 = 43

time1 = np.datetime64('2005-08-23T14:19:40.800000256')
time2 = np.datetime64('2022-12-30T12:25:12.000000256')

aviso_path = r'D:\Data\data\NRG\aviso\monthly\*.nc'
argo_path = r'D:\Data\data\NRG\Argo\ke_143-159_allPERIOD.nc'
etopo_path = r'D:\Data\data\NRG\etopo\etopo.nc'
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

dss = xr.open_mfdataset(aviso_path)
dsm = xr.open_mfdataset(argo_path)
dse = xr.open_mfdataset(etopo_path)

etopo = dse.z.interp(lon=dsm.lon, lat=dsm.lat).T
u = dsm.u.values / 100
u[etopo >= -1000] = np.nan
dsm.u.values = u
v = dsm.v.values / 100
v[etopo >= -1000] = np.nan
dsm.v.values = v

ugos = dss.ugos.where((dss.time >= time1) & (dss.time <= time2), drop=True).mean('time')
vgos = dss.vgos.where((dss.time >= time1) & (dss.time <= time2), drop=True).mean('time')
lon = dss.longitude
lat = dss.latitude
myproj = ccrs.PlateCarree(central_longitude=(lon1 + lon2) / 2)

fig, axes = plt.subplots(1, 2, figsize=(8, 5.5), subplot_kw={'projection': myproj})
plt.subplots_adjust(wspace=0.15)

lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
lons = np.arange(143, 154, 3)
lats = np.arange(30, 43, 2)

ax1 = axes[0]
Lon, Lat = np.meshgrid(lon, lat)
levels_a = np.arange(-0.5, 0.501, 0.05)
im1 = ax1.contourf(
    Lon,
    Lat,
    ugos,
    cmap=plt.cm.RdBu_r,
    levels=levels_a,
    extend='both',
    transform=ccrs.PlateCarree(),
    antialiased=True,
)
ax1.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
xx = 4
q1 = ax1.quiver(
    Lon[::xx, ::xx],
    Lat[::xx, ::xx],
    ugos.values[::xx, ::xx],
    vgos.values[::xx, ::xx],
    zorder=10,
    transform=ccrs.PlateCarree(),
    scale=5,
    width=0.004,
    headwidth=3.5,
    alpha=0.85,
    color='k',
)
ax1.quiverkey(q1, X=0.65, Y=1.05, U=0.5, label='0.5 m s$^{-1}$', labelpos='E', fontproperties={'size': 11})
ax1.coastlines('50m', linewidth=0.8)
ax1.add_feature(cfeature.LAND, facecolor='#d3d3d3', edgecolor='k', zorder=5)
ax1.set_xticks(lons, crs=ccrs.PlateCarree())
ax1.set_yticks(lats, crs=ccrs.PlateCarree())
ax1.xaxis.set_major_formatter(lon_formatter)
ax1.yaxis.set_major_formatter(lat_formatter)
ax1.set_title('a', loc='left', fontweight='bold', fontsize=16)
cbar1 = plt.colorbar(im1, ax=ax1, orientation='horizontal', shrink=0.7, pad=0.08, aspect=30)
cbar1.set_ticks(np.arange(-0.5, 0.6, 0.25))
cbar1.ax.tick_params(axis='x', rotation=0, labelsize=11)
cbar1.set_label('m s$^{-1}$', fontsize=12, fontweight='bold')

ax2 = axes[1]
Lon_m, Lat_m = np.meshgrid(dsm.lon, dsm.lat)
levels_b = np.arange(-0.15, 0.1501, 0.015)
im2 = ax2.contourf(
    Lon_m,
    Lat_m,
    dsm.u.T,
    cmap=plt.cm.RdBu_r,
    levels=levels_b,
    extend='both',
    transform=ccrs.PlateCarree(),
    antialiased=True,
)
ax2.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
xx = 2
q2 = ax2.quiver(
    Lon_m[::xx, ::xx],
    Lat_m[::xx, ::xx],
    dsm.u.T.values[::xx, ::xx],
    dsm.v.T.values[::xx, ::xx],
    zorder=10,
    transform=ccrs.PlateCarree(),
    scale=1.5,
    width=0.004,
    headwidth=3.5,
    alpha=0.85,
    color='k',
)
ax2.quiverkey(q2, X=0.65, Y=1.05, U=0.1, label='0.1 m s$^{-1}$', labelpos='E', fontproperties={'size': 11})
ax2.coastlines('50m', linewidth=0.8)
ax2.add_feature(cfeature.LAND, facecolor='#d3d3d3', edgecolor='k', zorder=5)
ax2.set_xticks(lons, crs=ccrs.PlateCarree())
ax2.set_yticks(lats, crs=ccrs.PlateCarree())
ax2.xaxis.set_major_formatter(lon_formatter)
ax2.yaxis.set_major_formatter(lat_formatter)
ax2.set_title('b', loc='left', fontweight='bold', fontsize=16)
cbar2 = plt.colorbar(im2, ax=ax2, orientation='horizontal', shrink=0.7, pad=0.08, aspect=30)
cbar2.set_ticks(np.arange(-0.15, 0.16, 0.05))
cbar2.ax.tick_params(axis='x', rotation=45, labelsize=11)
cbar2.set_label('m s$^{-1}$', fontsize=12, fontweight='bold')

plt.savefig(outdir / 'aviso_argo_2016_2025.pdf', bbox_inches='tight')
plt.savefig(outdir / 'aviso_argo_2016_2025.jpg', dpi=300, bbox_inches='tight')
plt.show()
