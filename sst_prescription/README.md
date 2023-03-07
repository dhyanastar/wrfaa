# SST Prescription

**Jeonghoe Kim**

These scripts are designed to conduct preprocess sea surface temperature (SST) data such that they can be used as inputs of the WRF Preprocessing System (WPS).

## How to Use

1. Modify each script first to be consistent with your SST data.
2. Execute the scripts as follows.
```tcsh
python extract_sst.py
ncl netcdf-to-intermediate.ncl
```
3. Then, the WRF intermediate files will be generated in the location that you have assigned in the `netcdf-to-intermediate.ncl` script.
4. Link the attached `METGRID.TBL.ARW.sst` to `WPS/metgrid/METGRIB.TBL`.

Check the list of compatible SST data in `extract_sst.py` script. 