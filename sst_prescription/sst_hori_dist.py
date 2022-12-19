# sst_hori_dist.py
#
# This script visualizes horizontal distributions of SST and relevant errors
# in a selected SST dataset (i.e. GHRSST, MUR, OISST, and OSTIA).
#
# Requirements:
#   - Python 3.x
#   - NumPy
#   - SciPy
#   - netCDF4
#   - Matplotlib
#   - Cartopy

import numpy as np
import netCDF4 as nc
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import datetime as pydt
import glob

#----------------------------------------------------------------------#

# SST dataset.
dataset = "OISST"
# Available options:
#   1. OSTIA
#   2. OSTIAdiu
#   3. OISST
#   4. GHRSST_JPL_4.1
#   5. GHRSST_JPL_4.2
#   6. GHRSST_NCEI
#   7. GHRSST_UKMO

# Whether to draw SST and its errors.
to_draw_sst = True
to_draw_err = True

# Visualization time.
start_date = "2016-01-22 00:00"
end_date   = "2016-01-23 00:00"
timedelta  = 24    # [hr]

# Latitude/Longitude bounds for the image(s).
lat_bound = [30, 45]
lon_bound = [120, 135]

# Location of the original SST files in NetCDF format.
# In "loc_sst", a directory in which SST files for each type should be
# located.
# e.g.
#   $ ls -x ${loc_sst}/OISST
#     oisst-avhrr-v02r01.20160122.nc
#     oisst-avhrr-v02r01.20210907.nc
#     ...
loc_sst = "."

# Contour levels of SST and its error.
cnlevels_sst = np.arange(0, 20+1, 1) + 273.15
cnlevels_err = np.linspace(0, 1, 31)

# Ticks of the label bars for each contour plot.
ticks_sst = cnlevels_sst
ticks_err = cnlevels_err

# -------------------------------------------------------------------- #

def load_data(dataset, time):
  if dataset == "OSTIA":
    # Foundation SST (daily frequency) archived in Copernicus Marine Service.
    # It is highly likely that this is equal to that archived in JPL PO.DAAC.
    fil = glob.glob("%s/OSTIA/%s*-OSTIA-*.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil)
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][0,:,:]      # [K]
    err  = ncdf.variables["analysis_error"][0,:,:]    # [K]
    ncdf.close()
  elif dataset == "OSTIAdiu":
    # Skin SST (hourly frequency) archived in Copernicus Marine Service.
    fil = glob.glob("%s/OSTIA/%s*-OSTIAdiu-*.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil)
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][time.hour,:,:]      # [K]
    err  = None    # Error is not provided in this dataset.
    ncdf.close()
  elif dataset == "OISST":
    # NOAA OI SST V2 high resolution data (daily frequency) archived in NOAA FTP server.
    # It is highly likely that this is foundation SST.
    # Reference: <https://www.ncei.noaa.gov/products/optimum-interpolation-sst>.
    fil = glob.glob("%s/OISST/oisst-*.%s.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil)
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    print(lon)
    sst  = ncdf.variables["sst"][0,0,:,:] + 273.15    # [K]
    err  = ncdf.variables["err"][0,0,:,:]             # [C] (= [K] in terms of error)
    ncdf.close()
  elif dataset == "GHRSST_JPL_4.1":
    # GHRSST Level 4 MUR Global Foundation Sea Surface Temperature Analysis (v4.1)
    # Foundation SST (daily frequency) produced by NASA JPL and archived in JPL PO.DAAC.
    # Reference: <https://www.doi.org/10.5067/GHGMR-4FJ04>.
    fil  = glob.glob("%s/GHRSST/%s*-JPL-*-MUR-*-fv04.1.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil, "r")
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][0,:,:]      # [K]
    err  = ncdf.variables["analysis_error"][0,:,:]    # [K]
    ncdf.close()
  elif dataset == "GHRSST_JPL_4.2":
    # GHRSST Level 4 MUR 0.25deg Global Foundation Sea Surface Temperature Analysis (v4.2)
    # 0.25 DEG Foundation SST (daily frequency) produced by NASA JPL and archived in JPL PO.DAAC.
    # Reference: <https://www.doi.org/10.5067/GHM25-4FJ42>.
    fil  = glob.glob("%s/GHRSST/%s*-JPL-*-MUR25-*-fv04.2.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil, "r")
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][0,:,:]      # [K]
    err  = ncdf.variables["analysis_error"][0,:,:]    # [K]
    ncdf.close()
  elif dataset == "GHRSST_NCEI":
    # GHRSST Level 4 AVHRR_OI Global Blended Sea Surface Temperature Analysis (GDS2) from NCEI (v2.1)
    # It is highly likely that this is foundation SST, but blended with other sources of SST.
    # Reference: <https://www.doi.org/10.5067/GHAAO-4BC21>.
    fil  = glob.glob("%s/GHRSST/%s*-NCEI-*-AVHRR_OI-*-fv02.1.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil, "r")
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][0,:,:]      # [K]
    err  = ncdf.variables["analysis_error"][0,:,:]    # [K]
    ncdf.close()
  elif dataset == "GHRSST_UKMO":
    # GHRSST Level 4 OSTIA Global Foundation Sea Surface Temperature Analysis (GDS version 2)
    # Foundation SST (daily frequency) produced by UKMO and archived in JPL PO.DAAC.
    # Reference: <https://www.doi.org/10.5067/GHOST-4FK02>.
    fil  = glob.glob("%s/GHRSST/%s*-UKMO-*-OSTIA-*-fv02.0.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil, "r")
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][0,:,:]      # [K]
    err  = ncdf.variables["analysis_error"][0,:,:]    # [K]
    ncdf.close()

  lat = np.array(lat)
  lon = np.array(lon)
  sst = np.array(sst)
  sst[sst < 0] = np.nan    # Set NaN value.
  if err is not None:
    err = np.array(err)
    err[err < 0] = np.nan    # Set NaN value.

  # Convert W to E.
  if np.any(np.array(lon) > 180) & np.any(np.array(lon_bound) < 0):
    lon_bound[0], lon_bound[1] = 360+lon_bound[0], 360+lon_bound[1]
  
  # Slice the arrays by the predefined lat/lon ranges with padding.
  padding = 10    # Padding with 10 more indices.
  mask_lat = (lat >= lat_bound[0]) & (lat <= lat_bound[1])
  mask_lon = (lon >= lon_bound[0]) & (lon <= lon_bound[1])
  ind_lat = np.arange(lat.size)[mask_lat]
  ind_lon = np.arange(lon.size)[mask_lon]

  i1 = np.max([0, ind_lat[0]-padding])
  i2 = np.min([lat.size, ind_lat[-1]+padding])
  j1 = np.max([0, ind_lon[0]-padding])
  j2 = np.min([lon.size, ind_lon[-1]+padding])

  lat = lat[i1:i2+1]
  lon = lon[j1:j2+1]
  sst = sst[i1:i2+1, j1:j2+1]
  if err is not None:
    err = err[i1:i2+1, j1:j2+1]

  return lat, lon, sst, err

# -------------------------------------------------------------------- #

def visualize_sst(lat, lon, sst, time, label_fig, label_fil):
  X, Y = np.meshgrid(lon, lat)

  fig = plt.figure(dpi=200)
  ax = plt.axes(projection=ccrs.PlateCarree())

  cont = ax.contourf(X, Y, sst, cnlevels_sst, transform=ccrs.PlateCarree(), cmap="coolwarm", extend="both")
  cbar = fig.colorbar(cont, pad=0.02, shrink=0.6, ticks=ticks_sst)
  cbar.ax.tick_params(labelsize=6)
  
  gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, color="black", linestyle="--", linewidth=0.5)
  gl.top_labels   = False
  gl.right_labels = False
  gl.xlabel_style = { "size" : 5 }
  gl.ylabel_style = { "size" : 5 }
  ax.set_title("%s [°C]" % (label_fig), loc="left", fontsize=7)
  ax.set_title("%s" % (time.strftime("%Y-%m-%d %H:%M UTC")), loc="right", fontsize=7)
  ax.set_extent([lon_bound[0], lon_bound[1], lat_bound[0], lat_bound[1]], crs=ccrs.PlateCarree())
  ax.coastlines("10m", linewidth=0.5, color="gray")
  plt.draw()
  plt.savefig("./sst_%s_%s.png" % (label_fil, time.strftime("%Y%m%d_%H%M")), bbox_inches="tight")
  plt.close("all")

  return


def visualize_err(lat, lon, err, time, label_fig, label_fil):
  X, Y = np.meshgrid(lon, lat)

  fig = plt.figure(dpi=200)
  ax = plt.axes(projection=ccrs.PlateCarree())

  cont = ax.contourf(X, Y, err, cnlevels_err, transform=ccrs.PlateCarree(), cmap="brg", extend="max")
  cbar = fig.colorbar(cont, pad=0.02, shrink=0.6, ticks=cnlevels_err)
  cbar.ax.tick_params(labelsize=6)
  
  gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, color="black", linestyle="--", linewidth=0.5)
  gl.top_labels   = False
  gl.right_labels = False
  gl.xlabel_style = { "size" : 5 }
  gl.ylabel_style = { "size" : 5 }
  ax.set_title("Error of %s [°C]" % (label_fig), loc="left", fontsize=7)
  ax.set_title("%s" % (time.strftime("%Y-%m-%d %H:%M UTC")), loc="right", fontsize=7)
  ax.set_extent([lon_bound[0], lon_bound[1], lat_bound[0], lat_bound[1]], crs=ccrs.PlateCarree())
  ax.coastlines("10m", linewidth=0.5, color="gray")
  plt.draw()
  plt.savefig("./err_%s_%s.png" % (label_fil, time.strftime("%Y%m%d_%H%M")), bbox_inches="tight")
  plt.close("all")

  return

# -------------------------------------------------------------------- #

start_date = pydt.datetime.strptime(start_date, "%Y-%m-%d %H:%M")
end_date = pydt.datetime.strptime(end_date, "%Y-%m-%d %H:%M")

times = []
time_now = start_date
while time_now <= end_date:
  times.append(time_now)
  time_now += pydt.timedelta(hours=timedelta)

for time in times:
  print("Processing %s ..." % (time.strftime("%Y-%m-%d %H:%M")))

  lat, lon, sst, err = load_data(dataset, time)

  if to_draw_sst:
    print("\tMax =", np.nanmax(sst))
    print("\tMin =", np.nanmin(sst))
    visualize_sst(lat, lon, sst, time, dataset, dataset.lower())
  if (to_draw_err) & (err is not None):
    print("\tMax =", np.nanmax(err))
    print("\tMin =", np.nanmin(err))
    visualize_err(lat, lon, err, time, dataset, dataset.lower())
