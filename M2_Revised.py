"""This script generates the revised M2 mooring time-series figure used in the manuscript."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.ndimage as si
import scipy.signal as sg
import xarray as xr
from correlation.correlation import corr
from matplotlib.lines import Line2D
from pathlib import Path

plt.rcParams.update({'font.size': 11, 'axes.linewidth': 1.2})
colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 'k']
outdir = Path('Figure')
outdir.mkdir(exist_ok=True)

dsargo = xr.open_dataset(r'D:\Data\data\NRG\Argo\ke_143-159_mon.nc')
filepath = r'D:\Data\data\KEMS\Mooring_update2025'
dsa = xr.open_dataset(filepath + r'\M2\ALL_ADCP_201604_202505.nc')
dsc = xr.open_dataset(filepath + r'\M2\ALL_CM_1500_3500_5500_201604_202505.nc')
dss0 = xr.open_mfdataset(r'D:\Data\data\NRG\aviso\daily1\*.nc')

start_time = pd.to_datetime('2016-04-14 23:59:00')
end_time = pd.to_datetime('2025-04-30 23:59:00')
dss = dss0.interp(longitude=150, latitude=39).where((dss0.time >= start_time) & (dss0.time <= end_time), drop=True)
dsa = dsa.where((dsa.time >= start_time) & (dsa.time <= end_time), drop=True)
dsc = dsc.where((dsc.time >= start_time) & (dsc.time <= end_time), drop=True)

us0 = dsa.u[:, :21].mean('depth')
us0 = us0.where(~np.isnan(us0), drop=True).interp(time=us0.time)
u150 = dsc.u1500.where(dsc.u1500 > -0.15).interp(time=dsc.time)
u150 = u150.where(~np.isnan(u150), drop=True).interp(time=u150.time)
u350 = dsc.u3500.where(dsc.u3500 > -0.15).interp(time=dsc.time)
u350 = u350.where(~np.isnan(u350), drop=True).interp(time=u350.time)
u550 = dsc.u5500.where(dsc.u5500 < 0.11).interp(time=dsc.time)
u550 = u550.where(~np.isnan(u550), drop=True).interp(time=u550.time)

window = sg.windows.hann(12)
window = window / np.sum(window)

fig, axes = plt.subplots(2, 1, figsize=(7.6, 6))

ax = axes[0]
bx = ax.twinx()
cx = ax.twinx()
data = us0
datam = data.resample(time='ME').mean()
time = datam.time
datam1 = si.convolve(datam, window, mode='mirror')
ax.plot(time, datam1, color=colors[0], linewidth=1.8, label='upper 200 m')
ds = datam1.copy()

data = u150
datam = data.resample(time='ME').mean()
datam1 = si.convolve(datam, window, mode='mirror')
bx.plot(time, datam1, color=colors[1], linewidth=1.8, label='1500 m')
d15 = datam1.copy()

cx.spines['right'].set_position(('outward', 60))
cx.scatter(dsargo.time + np.timedelta64(15, 'D'), dsargo.uu / 100, color='k', s=40, alpha=0.8, zorder=5, label='Argo 1000m')

ax.set_ylabel('Velocity ($m\ s^{-1}$)', color=colors[0], fontweight='bold')
ax.tick_params(axis='y', colors=colors[0], labelsize=10)
ax.spines['left'].set_color(colors[0])
ax.spines['left'].set_linewidth(1.5)

bx.set_ylabel('Velocity ($m\ s^{-1}$)', color=colors[1], fontweight='bold')
bx.tick_params(axis='y', colors=colors[1], labelsize=10)
bx.spines['right'].set_color(colors[1])
bx.spines['right'].set_linewidth(1.5)

cx.set_ylabel('Argo ($m\ s^{-1}$)', color='k', fontweight='bold')
cx.tick_params(axis='y', colors='k', labelsize=10)
cx.spines['right'].set_color('k')
cx.spines['right'].set_linewidth(1.5)

ax.plot([], [], color=colors[1], linewidth=1.8, label='1500 m')
ax.scatter([], [], color='k', s=40, label='Argo 1000 m')
ax.set_title('a', loc='left', fontweight='bold', fontsize=13)

ax = axes[1]
data = u150
datam = data.resample(time='ME').mean()
datam1 = si.convolve(datam, window, mode='mirror')
ax.plot(time, datam1, color=colors[1], linewidth=1.8, label='1500 m')

data = u350
datam = data.resample(time='ME').mean()
datam1 = si.convolve(datam, window, mode='mirror')
ax.plot(time, datam1, color=colors[3], linewidth=1.8, label='3500 m')
d35 = datam1.copy()

data = u550
datam = data.resample(time='ME').mean()
datam1 = si.convolve(datam, window, mode='mirror')
ax.plot(time, datam1, color=colors[2], linewidth=1.8, label='5500 m')
d55 = datam1.copy()

ax.set_xlabel('Year', fontweight='bold', fontsize=12)
ax.set_ylabel('Velocity ($m\ s^{-1}$)', fontweight='bold', fontsize=12)
ax.tick_params(axis='both', labelsize=10)
ax.set_title('b', loc='left', fontweight='bold', fontsize=13)

r_200_1500, p_200_1500 = corr(ds, d15)
r_1500_3500, p_1500_3500 = corr(d15, d35)
r_3500_5500, p_3500_5500 = corr(d35, d55)

def format_p_value(p):
    if p < 0.01:
        return 'p < 0.01'
    if p == 1:
        return 'p < 0.05'
    return f'p = {p:.2f}'

custom_lines = [
    Line2D([0], [0], color=colors[0], lw=1.8, label='upper 200 m'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='k', markersize=8, label='Argo 1000 m'),
    Line2D([0], [0], color=colors[1], lw=1.8, label='1500 m'),
    Line2D([0], [0], color=colors[3], lw=1.8, label='3500 m'),
    Line2D([0], [0], color=colors[2], lw=1.8, label='5500 m'),
]
ax.legend(handles=custom_lines, loc='upper left', bbox_to_anchor=(1.05, 1.04), frameon=True, facecolor='#F8F9FA', edgecolor='#AAAAAA', fontsize=10)

corr_text = (
    f'r(  200 m, 1500 m)={r_200_1500:.2f} \n ({format_p_value(p_200_1500)})\n'
    f'r(1500 m, 3500 m)={r_1500_3500:.2f} \n ({format_p_value(p_1500_3500)})\n'
    f'r(3500 m, 5500 m)={r_3500_5500:.2f} \n ({format_p_value(p_3500_5500)})'
)
ax.text(1.03, -0.02, corr_text, transform=ax.transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='left', bbox=dict(boxstyle='round,pad=0.6', facecolor='#F8F9FA', alpha=0.95, edgecolor='#AAAAAA', linewidth=0.8))

plt.tight_layout(pad=1.5)
plt.savefig(outdir / 'M2_Revised.pdf', bbox_inches='tight')
plt.savefig(outdir / 'M2_Revised.jpg', dpi=300, bbox_inches='tight')
plt.show()
