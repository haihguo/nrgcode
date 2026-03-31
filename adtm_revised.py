"""This script generates the revised mean dynamic topography map used in the manuscript."""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmocean
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from pathlib import Path

lon1 = 140
lon2 = 155
lat1 = 30
lat2 = 43

aviso_path = r'D:\Data\data\NRG\aviso\dailylarge1\mon_adt.nc'
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

ds = xr.open_mfdataset(aviso_path)
adtm = ds.adt.mean('time')
lon = adtm.longitude
lat = adtm.latitude

fig = plt.figure(figsize=(7, 6))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
Lon, Lat = np.meshgrid(lon, lat)

im = ax.contourf(
    Lon,
    Lat,
    adtm,
    cmap=cmocean.cm.haline,
    levels=np.arange(0, 1.801, 0.1),
    transform=ccrs.PlateCarree(),
)
ax.contour(
    Lon,
    Lat,
    adtm,
    levels=[1.1],
    colors='black',
    linewidths=2.0,
    transform=ccrs.PlateCarree(),
)
ax.scatter(
    150,
    39,
    transform=ccrs.PlateCarree(),
    marker='*',
    s=150,
    color='black',
    edgecolor='white',
    zorder=5,
)
ax.text(
    150.4,
    38.8,
    'M2',
    transform=ccrs.PlateCarree(),
    color='black',
    fontsize=12,
    fontweight='bold',
    zorder=5,
)
ax.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
ax.coastlines('50m', linewidth=0.8)
ax.add_feature(cfeature.LAND, facecolor='#d3d3d3', edgecolor='k', zorder=5)
ax.set_xticks(np.arange(lon1, lon2 + 0.1, 5), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(lat1, lat2 + 0.1, 3), crs=ccrs.PlateCarree())
ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=False))
ax.yaxis.set_major_formatter(LatitudeFormatter())

cbar = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.7, pad=0.08)
cbar.ax.set_xlabel('m')

plt.savefig(outdir / 'adtm_revised.pdf', bbox_inches='tight')
plt.savefig(outdir / 'adtm_revised.jpg', dpi=300, bbox_inches='tight')
plt.show()
