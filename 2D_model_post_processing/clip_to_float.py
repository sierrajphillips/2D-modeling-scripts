# Clips float files from TUFLOW results with a shapefile and saved clipped float files to results folder with
# '_clip.flt' added to the end of the filename
# Created by SJP, last modified on 04/09/2021

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

# SET THE RESULT FOLDER HERE
# example: 'E:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_3_MRYFR\\results\\110'
results_folder = 'FOLDER PATH HERE'

# SET CLIPPING SHAPEFILE HERE
clip_shapefile = 'SHAPEFILE HERE'


def clip_to_float(flt_filename, run_dir, *args, **kwargs):
    logging.info(f'Clipping {flt_filename}...')
    flt_raster = arcpy.Raster(flt_filename)
    extent = f'{flt_raster.extent.XMin} {flt_raster.extent.YMin} {flt_raster.extent.XMax} {flt_raster.extent.YMax}'
    tif_file = os.path.basename(flt_filename).replace('.flt', '.tif')
    tif_filename = os.path.join(run_dir, tif_file)
    clipped_flt_filename = tif_filename.replace('.tif', '_clip.flt')
    # clip and output as tif
    arcpy.Clip_management(flt_raster,
                          extent,
                          tif_filename,
                          clip_shapefile,
                          clipping_geometry='ClippingGeometry',
                          maintain_clipping_extent='NO_MAINTAIN_EXTENT')
    # convert to .flt
    arcpy.RasterToFloat_conversion(tif_filename, clipped_flt_filename)
    logging.info(f'Saved clipped file to: {clipped_flt_filename}')
    return clipped_flt_filename

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
    # get top-level subdirs of results folder for each run
    run_dirs = [os.path.join(results_folder, run_dir) for run_dir in next(os.walk(results_folder))[1]]
    # iterate over runs
    for run_dir in run_dirs:
        # make list of float files ending in 00.flt
        flt_files = []
        for dir, subdirs, files in os.walk(run_dir):
            for flt_file in files:
                if flt_file.endswith('00.flt'):
                        flt_filename = os.path.join(dir, flt_file)  # path of float file in results folder
                        flt_files.append(flt_filename)
        grids_folder = os.path.join(run_dir, 'grids')

        # get last raster output time as string
        max_time = time_final_output(flt_files)
        # list of all float rasters at final time for the run
        end_files = [f for f in flt_files if f.endswith(f'{max_time}.flt')]

        # run clip to float
        for end_file in end_files:
            clip_to_float(end_file, grids_folder)