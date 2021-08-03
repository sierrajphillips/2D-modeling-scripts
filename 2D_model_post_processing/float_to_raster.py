# Converts float files from TUFLOW model results to TIF rasters (in separate folder)
# Created by SJP, last edited 02/01/2021

import os
import arcpy
import logging

# Set workspace file for ArcGIS, enable overwriting, and retrieve Spatial Analyst extension license
arcpy.env.workspace = os.path.abspath('')
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')

# logging format
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# SET THE FOLDERS HERE
# example: 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_3_MRYFR\\results\\110'
results_folder = 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_2_DPRMRY\\results\\143'
# example: 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_3_MRYFR\\review'
raster_folder = 'D:\\LYR_Restore\\baseline_rasters'

def float_to_raster(flt_filename, *args, **kwargs):
    logging.info(f'Converting from float to TIFF: {flt_filename}...')
    flt_raster = arcpy.Raster(flt_filename)
    tif_file = os.path.basename(flt_filename).replace('.flt', '.tif')
    tif_filename = os.path.join(discharge_folder, tif_file)
    arcpy.FloatToRaster_conversion(flt_raster, tif_filename)
    logging.info(f'Saved TIFF file to: {tif_filename}')
    return tif_filename

def make_discharge_folder(run_dir):
    # creates discharge subdir within raster_folder (global var)
    run_id = run_dir.split('\\')[-2]
    run_id_folder = os.path.join(raster_folder, run_id)
    discharge = run_dir.split('\\')[-1]
    discharge_folder = os.path.join(run_id_folder, discharge)

    # create new folder for run ID and subfolder for discharge, if doesn't exist
    if not os.path.exists(discharge_folder):
        logging.info('Creating discharge folder for {0}'.format(discharge))
        os.makedirs(discharge_folder)
    return discharge_folder

# Return the highest domain time among float files
def time_final_output(files):
    # get time part from file strings
    time_strs = [f.replace('.flt', '').split('_')[-2:] for f in files]
    # convert to float
    times = [float(t[0] + '.' + t[1]) for t in time_strs]
    max_time = max(times)
    max_str = ('%06.2f' % max_time).replace('.', '_')
    return max_str

if __name__ == "__main__":
    for dir, subdirs, files in os.walk(results_folder):
        # iterate over runs
        for flt_file in files:
            if flt_file.endswith('00.flt'):
                flt_filename = os.path.join(dir, flt_file)  # path of float file in results folder
                flt_files.append(flt_filename)

            # get last raster output time as string
            max_time = time_final_output(flt_files)
            # list of all float rasters at final time for the run
            end_files = [f for f in flt_files if f.endswith(f'{max_time}.flt')]

            # make discharge folder in run_id folder
            discharge_folder = make_discharge_folder(run_dir)

            # run float to raster conversion
            for end_file in end_files:
               float_to_raster(end_file, discharge_folder)