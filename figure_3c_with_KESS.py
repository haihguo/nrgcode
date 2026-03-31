"""This script generates the AVISO map with KESS station overlays used in the manuscript."""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from pathlib import Path

lon1 = 143
lon2 = 153
lat1 = 30
lat2 = 43

aviso_path = r'D:\Data\data\NRG\aviso\monthly\*.nc'
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

dss = xr.open_mfdataset(aviso_path)
tt = -112
lon = dss.longitude
lat = dss.latitude
myproj = ccrs.PlateCarree(central_longitude=(lon1 + lon2) / 2)
lon_formatter = LongitudeFormatter(zero_direction_label=False)
lat_formatter = LatitudeFormatter()

kess_sites = {'A2': (37.81, 147.87)}
kess_lats = [pos[0] for pos in kess_sites.values()]
kess_lons = [pos[1] for pos in kess_sites.values()]

ugos = dss.ugos[tt:, :, :].mean('time')
vgos = dss.vgos[tt:, :, :].mean('time')

fig = plt.figure(figsize=(7, 5))
ax = plt.subplot(1, 1, 1, projection=myproj)
Lon, Lat = np.meshgrid(lon, lat)
im = ax.contourf(
    Lon,
    Lat,
    ugos,
    cmap=plt.cm.RdBu_r,
    levels=np.arange(-0.5, 0.501, 0.1),
    extend='both',
    transform=ccrs.PlateCarree(),
)
ax.set_extent([lon1, lon2, lat1, lat2])
xx = 4
ax.quiver(
    Lon[::xx, ::xx],
    Lat[::xx, ::xx],
    ugos.values[::xx, ::xx],
    vgos.values[::xx, ::xx],
    zorder=10,
    transform=ccrs.PlateCarree(),
)
ax.scatter(kess_lons, kess_lats, color='#ccff00', edgecolor='k', marker='^', s=40, transform=ccrs.PlateCarree(), zorder=15, label='KESS Array')
for site in ['A2']:
    lat_s, lon_s = kess_sites[site]
    ax.text(lon_s + 0.2, lat_s, site, transform=ccrs.PlateCarree(), fontsize=10, fontweight='bold', color='black', zorder=16)
ax.coastlines('50m')
ax.add_feature(cfeature.LAND, color='gray')
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)
ax.set_xticks(np.arange(143, 154, 3), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(30, 43, 2), crs=ccrs.PlateCarree())
ax.legend(loc='lower right', fontsize=9)

cbar = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.4, pad=0.08)
cbar.ax.tick_params(axis='x', rotation=45)
cbar.ax.set_xlabel('m s$^{-1}$')

plt.savefig(outdir / 'Figure_3c_with_KESS.png', dpi=300, bbox_inches='tight')
plt.savefig(outdir / 'Figure_3c_with_KESS.pdf', bbox_inches='tight')
plt.show()
