"""This script generates the four-panel BC and shear figure used in the manuscript."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from band.lineartrend import callt
from cartopy.mpl.ticker import LatitudeFormatter
from pathlib import Path

plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 1.2,
})

colors = ['#d73027', '#4575b4', '#313695', '#f46d43']
lat_formatter = LatitudeFormatter()
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

ds = xr.open_dataset(r'D:\Data\data\NRG\aviso\highpass\ck.nc')
ds = ds.where((ds.lon >= 140) & (ds.lon <= 180), drop=True)
ds = ds.where(ds.time <= np.datetime64('2025-01-01'), drop=True)
ck = -(ds.u1a + ds.u2a + ds.u3a + ds.u4a)
ds1 = xr.open_dataset(r'D:\Data\data\NRG\aviso\highpass\uyear.nc')

yy1 = 36.6
yy2 = 38
c2 = ck
cta = c2.where((c2.lat > yy1) & (c2.lat < yy2)).mean('lon').mean('lat')
cte = ds.u20.where((ds.u20.lat > yy1) & (ds.u20.lat < yy2)).mean('lon').mean('lat')
ctd = ds.udy.where((ds.udy.lat > yy1) & (ds.udy.lat < yy2)).mean('lon').mean('lat')

fig, axes = plt.subplots(2, 2, figsize=(10, 7), gridspec_kw={'hspace': 0.3, 'wspace': 0.3})

ax = axes[0, 0]
c2[:11, :, :].mean('time').mean('lon').plot(ax=ax, color=colors[1], lw=2, label='1993-2003')
c2[-10:, :, :].mean('time').mean('lon').plot(ax=ax, color=colors[0], lw=2, label='2016-2025')
ax.axes.ticklabel_format(style='sci', axis='y', useMathText=True, scilimits=(-2, 4))
ax.set_ylabel(r'$BC$ ($m^2 s^{-3}$)', fontweight='bold')
ax.set_xlabel('Latitude', fontweight='bold')
ax.set_ylim(-1.5e-8, 2.5e-8)
ax.set_xlim(28, 43)
ax.axhline(0, color='k', ls=':', lw=1.2)
ax.axvspan(36.6, 38.0, color='gray', alpha=0.15, zorder=0)
ax.axvline(36.6, color='k', ls='--', lw=1)
ax.axvline(38.0, color='k', ls='--', lw=1)
ax.set_title('a', loc='left', fontweight='bold')
ax.xaxis.set_major_formatter(lat_formatter)
ax.legend(frameon=False, loc='upper left')

ax = axes[0, 1]
bx = ax.twinx()
time = np.arange(len(ds.time))
cc_cta = cta
cc_cta.plot(ax=ax, color=colors[0], lw=1.2, alpha=0.8)
params, pvalues, outdata, conf_int = callt(time, cc_cta.values, alpha=0.05)
ax.plot(ds.time, outdata, color=colors[0], lw=2)
ax.set_ylabel(r'$BC$ ($m^2 s^{-3}$)', color=colors[0], fontweight='bold')
ax.axes.ticklabel_format(style='sci', axis='y', useMathText=True, scilimits=(-2, 4))
cc_u = ds1.ugos
cc_u.plot(ax=bx, color=colors[1], lw=1.2, alpha=0.8)
params, pvalues, outdata, conf_int = callt(time, cc_u.values, alpha=0.05)
bx.plot(ds.time, outdata, color=colors[1], lw=2)
bx.set_ylabel(r'$u$ ($m s^{-1}$)', color=colors[1], fontweight='bold')
ax.spines['left'].set_color(colors[0])
ax.spines['left'].set_linewidth(1.5)
bx.spines['right'].set_color(colors[1])
bx.spines['right'].set_linewidth(1.5)
ax.tick_params(axis='y', colors=colors[0])
bx.tick_params(axis='y', colors=colors[1])
ax.set_title('b', loc='left', fontweight='bold')
ax.set_xlabel('Year', fontweight='bold')

ax = axes[1, 0]
cc_cte = cte
cc_cte.plot(ax=ax, color=colors[3], lw=1.2, alpha=0.8)
params, pvalues, outdata, conf_int = callt(time, cc_cte.values, alpha=0.05)
ax.plot(ds.time, outdata, color=colors[3], lw=2.5, ls='--')
ax.axes.ticklabel_format(style='sci', axis='y', useMathText=True, scilimits=(-2, 4))
ax.set_ylabel(r"$\overline{u'v'}$ ($m^2 s^{-2}$)", fontweight='bold')
ax.set_xlabel('Year', fontweight='bold')
ax.set_title('c', loc='left', fontweight='bold')

ax = axes[1, 1]
cc_ctd = ctd
cc_ctd.plot(ax=ax, color=colors[2], lw=1.2, alpha=0.8)
params, pvalues, outdata, conf_int = callt(time, cc_ctd.values, alpha=0.05)
ax.plot(ds.time, outdata, color=colors[2], lw=2.5)
ax.axes.ticklabel_format(style='sci', axis='y', useMathText=True, scilimits=(-2, 4))
ax.set_ylabel(r'$\partial \bar{u} / \partial y$ ($s^{-1}$)', fontweight='bold')
ax.set_xlabel('Year', fontweight='bold')
ax.set_title('d', loc='left', fontweight='bold')

date_ticks = pd.date_range('1995-01', '2026-05', freq='5YS')
for ax_idx in [axes[0, 1], axes[1, 0], axes[1, 1]]:
    ax_idx.set_xticks(date_ticks)
    ax_idx.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_idx.grid(ls='--', alpha=0.3)

plt.tight_layout()
plt.savefig(outdir / 'ck_1993_2024.jpg', dpi=300, bbox_inches='tight')
plt.savefig(outdir / 'ck_1993_2024.pdf', bbox_inches='tight')
plt.show()
