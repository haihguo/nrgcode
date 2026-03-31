"""This script generates the surface geostrophic current difference map used in the manuscript."""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from pathlib import Path

lon1 = 140
lon2 = 155
lat1 = 30
lat2 = 43

aviso_path = r'D:\Data\data\NRG\aviso\monthly\*.nc'
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

dss = xr.open_mfdataset(aviso_path)
u1 = dss.ugos[-112:, :, :].mean('time') - dss.ugos[:120, :, :].mean('time')
v1 = dss.vgos[-112:, :, :].mean('time') - dss.vgos[:120, :, :].mean('time')
lon = u1.longitude
lat = u1.latitude
myproj = ccrs.PlateCarree(central_longitude=(lon1 + lon2) / 2)

fig = plt.figure(figsize=(6, 4))
ax = plt.subplot(1, 1, 1, projection=myproj)
Lon, Lat = np.meshgrid(lon, lat)
im = ax.contourf(
    Lon,
    Lat,
    u1,
    cmap=plt.cm.RdBu_r,
    levels=np.arange(-0.3, 0.301, 0.05),
    extend='both',
    transform=ccrs.PlateCarree(),
)
ax.set_extent([lon1, lon2, lat1, lat2])
xx = 4
q = ax.quiver(
    Lon[::xx, ::xx],
    Lat[::xx, ::xx],
    u1.values[::xx, ::xx],
    v1.values[::xx, ::xx],
    zorder=10,
    transform=ccrs.PlateCarree(),
)
ax.quiverkey(
    q,
    1.2,
    0.95,
    0.3,
    '0.3 m s$^{-1}$',
    labelpos='W',
    transform=ccrs.PlateCarree(),
)
ax.coastlines('50m')
ax.add_feature(cfeature.LAND, color='gray')
ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=False))
ax.yaxis.set_major_formatter(LatitudeFormatter())
ax.set_xticks(np.arange(143, 161, 3), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(30, 43, 2), crs=ccrs.PlateCarree())

cbar = plt.colorbar(im, ax=ax, orientation='vertical', shrink=0.8, pad=0.01)
cbar.ax.set_ylabel('m s$^{-1}$')

plt.savefig(outdir / 'diff.jpg', dpi=300, bbox_inches='tight')
plt.savefig(outdir / 'diff.pdf', bbox_inches='tight')
plt.show()
