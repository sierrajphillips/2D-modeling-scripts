# Converts and transfers float files from TUFLOW model results to TIF rasters in Hydraulics folder
# Created by SJP, last updated 06/24/21

import os
import arcpy
import logging

# SET THE TUFLOW RESULTS FOLDER HERE
# example: 'Z:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_3_MRYFR\\results\\110'
source_folder = 'Z:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_3_MRYFR\\results\\171'


# DO NOT CHANGE SCRIPT BELOW UNLESS YOU KNOW WHAT YOU ARE DOING
# Set workspace file for ArcGIS, enable overwriting, and retrieve Spatial Analyst extension license
arcpy.env.workspace = os.path.abspath('')
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
arcpy.env.snapRaster = 'Z:\\LYR\\LYR_2017studies\\LYR17_Topo\\LYR17_DEM\\09-Final_2017_DEM\\With_Structures\\LYR17_Final_DEM_with_str_adjusted.tif'

# logging format
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# hydraulics folder on server
target_folder = 'Z:\\LYR\\LYR_2017studies\\LYR17_Hydraulics\\'

# VARIABLES - script internal - do not modify
reach_dict = {"EDDPD": 1, "DPDMRY": 2, "MRYFR": 3}
par_folder_dict = {"V": "Velocity", "d": "Depth", "h": "WSE", "BSS": "BSS"}
par_ras_dict = {"V": "u", "d": "d", "h": "h", "BSS": "t"}


def get_dest(flt_filename):
    """Get destination for given float filename"""
    basename = os.path.basename(flt_filename).replace('.flt', '')
    reach, discharge, run_id, res, par, hrs, mins = basename.split('_')
    drive, river, study, modelling, river_reach, results, run_id, mannings_res_flow, grids, basename = flt_filename.split('\\')
    mannings, resolution, flow = mannings_res_flow.split('_')

    # create hydraulics subfolder based on mannings n distribution and resolution
    mannings_res = mannings + '_' + resolution

    # skip if not in chosen parameters to transfer (velocity, depth, WSE, shear stress)
    if par not in par_ras_dict.keys():
        return None
    else:
        dest_folder = f'{target_folder}\\LYR17_{par_folder_dict[par]}\\{reach_dict[reach]}_{reach}\\{mannings_res}'
        # if subfolder in reach folder does not exist, creates one
        if not os.path.exists(dest_folder):
            logging.info('Creating subfolder for {0}'.format(mannings_res))
            os.makedirs(dest_folder)
        dest_tif = f'{par_ras_dict[par]}{int(discharge):06d}.tif'
        return os.path.join(dest_folder, dest_tif)


def float_to_raster(flt_filename, *args, **kwargs):
    """Converts input float raster to geoTIFF"""
    flt_raster = arcpy.Raster(flt_filename)
    tif_filename = get_dest(flt_filename)
    if tif_filename is None:
        logging.info(f'Skipping {flt_filename}...\n')
        return None
    if os.path.exists(tif_filename):
        logging.info(f'TIFF file exists, skipping {flt_filename}...\n')
        return None
    else:
        logging.info(f'Converting from float to TIFF: \n>>> {flt_filename}...')
        arcpy.FloatToRaster_conversion(flt_raster, tif_filename)
        logging.info(f'Saved TIFF file to: \n>>> {tif_filename}\n')
        return tif_filename


def time_final_output(files):
    """Returns the highest domain time among float files"""
    # get time part from file strings
    time_strs = [f.replace('.flt', '').split('_')[-2:] for f in files]
    # convert to float
    times = [float(t[0] + '.' + t[1]) for t in time_strs]
    max_time = max(times)
    max_str = ('%06.2f' % max_time).replace('.', '_')
    return max_str


if __name__ == "__main__":

    # get top-level subdirs of results folder for each run
    run_dirs = [os.path.join(source_folder, subdir) for subdir in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, subdir))]
    # iterate over runs
    for run_dir in run_dirs:
        # make list of float files ending in 00.flt
        flt_files = []
        for dir, subdirs, files in os.walk(run_dir):
            for flt_file in files:
                if flt_file.endswith('00.flt'):
                    flt_filename = os.path.join(dir, flt_file)  # path of float file in results folder
                    flt_files.append(flt_filename)

        # get last raster output time as string
        max_time = time_final_output(flt_files)
        # list of all float rasters at final time for the run
        end_files = [f for f in flt_files if f.endswith(f'{max_time}.flt')]

        # transfer .flt in source folder to .tif in target folder
        for end_file in end_files:
            float_to_raster(end_file)
