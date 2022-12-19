# interp_sst.py
# Jeonghoe Kim <jeonghoekim.14@snu.ac.kr>
#
# This script conducts nearest interpolation or linear interpolation
# to fill missing values in SST datasets.
# It is noted that nearest interpolation method is preferred here.
#
# Requirements:
#   - Python 3.x
#   - NumPy
#   - SciPy
#   - netCDF4

import numpy as np
import netCDF4 as nc
import datetime as pydt
import glob

from scipy.interpolate import NearestNDInterpolator, LinearNDInterpolator

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

# Latitude/Longitude bounds (Set them to cover the WRF domain reasonably).
lat_bound = [30, 45]
lon_bound = [120, 135]

# WRF integration time.
start_date = "2021-09-07 18:00"
end_date   = "2021-09-07 23:00"

# Location of the original SST files in NetCDF format.
# In "loc_sst", a directory in which SST files for each type should be
# located.
# e.g.
#   $ ls -x ${loc_sst}/OISST
#     oisst-avhrr-v02r01.20160122.nc
#     oisst-avhrr-v02r01.20210907.nc
#     ...
loc_sst = "."

# Location of the interpolated NetCDF files.
loc_out = "./interp"

#----------------------------------------------------------------------#

def load_data(dataset, time):
  if dataset == "OSTIA":
    # Foundation SST (daily frequency) archived in Copernicus Marine Service.
    # It is highly likely that this is equal to that archived in JPL PO.DAAC.
    fil = glob.glob("%s/OSTIA/%s*-OSTIA-*.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil)
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][0,:,:]      # [K]
    ncdf.close()
  elif dataset == "OSTIAdiu":
    # Skin SST (hourly frequency) archived in Copernicus Marine Service.
    fil = glob.glob("%s/OSTIA/%s*-OSTIAdiu-*.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil)
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["analysed_sst"][time.hour,:,:]      # [K]
    ncdf.close()
  elif dataset == "OISST":
    # NOAA OI SST V2 high resolution data (daily frequency) archived in NOAA FTP server.
    # It is highly likely that this is foundation SST.
    # Reference: <https://www.ncei.noaa.gov/products/optimum-interpolation-sst>.
    fil = glob.glob("%s/OISST/oisst-*.%s.nc" % (loc_sst, time.strftime("%Y%m%d")))[0]
    ncdf = nc.Dataset(fil)
    lat  = ncdf.variables["lat"][:]
    lon  = ncdf.variables["lon"][:]
    sst  = ncdf.variables["sst"][0,0,:,:] + 273.15    # [C] -> [K]
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
    ncdf.close()

  lat = np.array(lat)
  lon = np.array(lon)
  sst = np.array(sst)
  sst[sst < 0] = np.nan    # Set NaN value.

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

  return lon, lat, sst

# -------------------------------------------------------------------- #

def to_netcdf(loc_out, dataset, lon, lat, sst, time, use_interp):
  # The inputs should be consistent with the following units.
  time_unit = "seconds since 1981-01-01 00:00:00"
  lat_unit  = "degrees_north"
  lon_unit  = "degrees_east"
  sst_unit  = "K"

  nt = 1
  nx = lon.size
  ny = lat.size

  fil = "%s/%s_%s_interp.nc" % (loc_out, dataset, time.strftime("%Y%m%d_%H"))

  ncdf = nc.Dataset(fil, "w")

  ncdf.createDimension("time", nt)
  ncdf.createDimension("lat" , ny)
  ncdf.createDimension("lon" , nx)

  time_out = ncdf.createVariable("time", "i4", "time")
  lat_out  = ncdf.createVariable("lat" , "f4", "lat")
  lon_out  = ncdf.createVariable("lon" , "f4", "lon")
  sst_out  = ncdf.createVariable("sst" , "f4", ("lat", "lon"))
  
  if use_interp == False:
    msk_out  = ncdf.createVariable("msk" , "i4", ("lat", "lon"))

  time_out[0]  = int(nc.date2num([time], time_unit))
  lat_out[:]   = lat[:]
  lon_out[:]   = lon[:]
  sst_out[:,:] = sst[:,:]
  msk_out[:,:] = np.isnan(sst)

  time_out.units = time_unit
  lat_out.units  = lat_unit
  lon_out.units  = lon_unit
  sst_out.units  = sst_unit
  msk_out.units  = ""

  ncdf.close()

# -------------------------------------------------------------------- #

start_date = pydt.datetime.strptime(start_date, "%Y-%m-%d %H:%M")
end_date = pydt.datetime.strptime(end_date, "%Y-%m-%d %H:%M")

times = []
time_now = start_date
while time_now <= end_date:
  times.append(time_now)
  time_now += pydt.timedelta(hours=1)

for time in times:
  print("Processing %s ..." % (time.strftime("%Y-%m-%d %H:00 ...")))
  print("\tLoading ...")
  lon, lat, sst = load_data(dataset, time)
  
  print("\tConducting nearest interpolation ...")
  mask = np.where(~np.isnan(sst))
  interp = NearestNDInterpolator(np.transpose(mask), sst[mask])
  sst = interp(*np.indices(sst.shape))

  print("\tWriting to a new NetCDF file ...")
  to_netcdf(loc_out, dataset, lon, lat, sst, time, use_interp)

print("Finished.")
