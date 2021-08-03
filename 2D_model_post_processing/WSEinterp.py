# Python script to interpolate water surface elevation using River Architect's cWaterLevel module

import arcpy
from arcpy.sa import *
import sys
import os
import shutil
sys.path.append('D:\\LYR_Restore\\RiverArchitect\\GetStarted\\')
import cWaterLevel as cWL

# set folders
results_folder = 'Z:\\LYR\\LYR_Restore\\Long_Bar\\WSE_interpolated\\results'
dem_tif = 'Z:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_1_EDDPD\\model\\grid\\tif\\lyr17_eddpd_final_dem_with_str_revised_clip.tif'
wse_interp_folder = 'Z:\\LYR\\LYR_Restore\\Long_Bar\\WSE_interpolated'

# create folders for each discharge, if they do not already exist
for dir, subdirs, files in os.walk(results_folder):
    for f in files:
        var_code = f.split('_')[-3]  # code for the tuflow output variable (e.g. h, d, BSS, V)
        if var_code in ['h', 'd']:
            if var_code == 'h':
                run_id = f.split('_h_')[0]
                var_name = 'WSE'
            else:
                run_id = f.split('_d_')[0]
                var_name = 'depth'

            # creates new folder for given discharge/runID (if doesn't exist)
            discharge_folder = os.path.join(wse_interp_folder, run_id)
            if not os.path.exists(discharge_folder):
                print('Creating folder for {0}...'.format(run_id))
                os.makedirs(discharge_folder)

            # defines the WSE float file and moves to the corresponding discharge folder
            print('Copying {0} file: {1}\n\tfrom: {2}\n\tto: {3}...\n'.format(var_name, f, dir, discharge_folder))
            filename = os.path.join(dir, f)
            shutil.copy(filename, discharge_folder)
        else:
            continue

for dir, subdirs, files in os.walk(wse_interp_folder):
    for f in files:
        if f.endswith('flt') and f.split('_')[-3] == 'h':
            run_id = f.split('_h')[0]
            wse_flt = os.path.join(dir, f)
            depth_flt = wse_flt.replace('_h_', '_d_')
            discharge_folder = os.path.join(wse_interp_folder, f.split('_h')[0])

            print('Adding rasters for {0}...'.format(run_id))
            wse = Raster(wse_flt)
            depth = Raster(depth_flt)
            dem = Raster(dem_tif)

            print('Setting snap raster and enabling overwrite for {0}...'.format(run_id))
            arcpy.env.snapRaster = wse
            arcpy.env.overwriteOutput = True

            print('Calculating alternative DEM for {0}...'.format(run_id))
            alt_dem = Con(~IsNull(wse), wse - depth, dem)

            print('Calculating interpolated water level for {0}...'.format(run_id))
            cwl = cWL.WLE(depth_flt, alt_dem, discharge_folder, method='IDW')
            cwl.out_h_interp = '{0}_h_interp.tif'.format(run_id)
            cwl.out_wle = '{0}_wle.tif'.format(run_id)
            cwl.calculate_h()
        else:
            continue