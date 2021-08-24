# Create wetted area polygons from the merged rasters in the Hydraulics folder
# Created by SJP, last updated 08/24/21

import os
import arcpy
from arcpy.sa import *
import logging


# DO NOT CHANGE SCRIPT BELOW UNLESS YOU KNOW WHAT YOU ARE DOING
# Set workspace file for ArcGIS, enable overwriting, and retrieve Spatial Analyst extension license
arcpy.env.workspace = os.path.abspath('')
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
arcpy.env.snapRaster = 'Z:\\LYR\\LYR_2017studies\\LYR17_Topo\\LYR17_DEM\\09-Final_2017_DEM\\With_Structures\\LYR17_Final_DEM_with_str_adjusted.tif'

# logging format
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# mannings/resolution dictionary
mannings_res_dict = {1: "Globaln_10ft", 2: "Globaln_3ft", 3: "Spatialn_10ft",
                     4: "Spatialn_3ft", 5: "Combinedn_10ft", 6:"Combinedn_3ft"}

source_folder = 'Z:\\LYR\\LYR_2017studies\\LYR17_Hydraulics\\LYR17_Depth\\0_Merged'
wettedarea_folder = 'Z:\\LYR\\LYR_2017studies\\LYR17_Hydraulics\\LYR17_WettedArea\\0_Merged'

# if 0_Merged subfolder in wetted area folder doesn't exist, create one
if not os.path.exists(wettedarea_folder):
    os.makedirs(wettedarea_folder)
    logging.info(f'Created 0_Merged subfolder...')

def wetted_polygons(merged_filename):
    # defining wetted area polygon and dissolved wetted area polygon shapefile names and locations
    q = source_file.split('d')[-1].split('.tif')[0]
    wp_file = f'wp{q}.shp'
    dissolved_file = f'wp{q}_dissolved.shp'
    wp_subfolder = f'{wettedarea_folder}\\{mannings_res_dict[mr]}'
    wp_filename = os.path.join(wp_subfolder, wp_file)
    dissolved_filename = os.path.join(wp_subfolder, dissolved_file)

    # if mannings-resolution subfolder (wp_subfolder) doesn't exist, create one
    if not os.path.exists(wp_subfolder):
        os.makedirs(wp_subfolder)
        logging.info(f'Created: {wp_subfolder}')

    # if temp subfolder doesn't exist, create one
    if not os.path.exists(f'{wp_subfolder}\\temp'):
        os.makedirs(f'{wp_subfolder}\\temp')
        logging.info(f'Created temp folder...')

    # if dissolved wetted polygon file exists, will skip and move on to the next discharge
    if os.path.exists(dissolved_filename):
        logging.info(f'Dissolved wetted area polygon exists, skipping {dissolved_file}...\n')
        return
    else:
        integer_file = f'w{q}_integer.tif'
        integer_filename = f'{wp_subfolder}\\temp\\{integer_file}'
        try:
            # Convert depth raster to integer raster
            logging.info(f'Converting depth raster ({source_file}) to integer raster...')
            integer_ras = Con(Raster(merged_filename), 1)
            integer_ras.save(integer_filename)
            try:
                # Process: Raster to Polygon (conversion)
                logging.info(f'Converting integer raster ({integer_file}) to polygon shapefile...')
                arcpy.RasterToPolygon_conversion(integer_filename, wp_filename, 'NO_SIMPLIFY', 'VALUE')
                try:
                    # Process: Dissolve (management)
                    logging.info(f'Combining all wetted area polygons into a single polygon...\n')
                    arcpy.Dissolve_management(wp_filename, dissolved_filename, dissolve_field='gridcode',
                                              multi_part='MULTI_PART', unsplit_lines='DISSOLVE_LINES')
                except:
                    logging.info(f'Failed to combine wetted area polygons ({dissolved_file}), skipping to next discharge...\n')
                    return -1
            except:
                logging.info(f'Failed to convert integer raster ({integer_file}) to wetted area polygon shapefile, skipping to next discharge...\n')
                return -1
        except:
            logging.info(f'Failed to convert depth raster ({source_file}) to integer raster, skipping to next discharge...\n')
            return -1


if __name__ == '__main__':
    # iterate through mannings-resolution subfolders in the 0_Merged folder
    for mr in mannings_res_dict:
        mr_subfolder = f'{source_folder}\\{mannings_res_dict[mr]}'
        depth_files = []

        for dirs, subdirs, files in os.walk(mr_subfolder):
            for tif_file in files:
                if tif_file.endswith('.tif'):
                    depth_files.append(tif_file)
            for source_file in depth_files:
                merged_filename = os.path.join(mr_subfolder, source_file)
                try:
                    wetted_polygons(merged_filename)
                except:
                    logging.info(f'Missing depth hydraulic TIFF file, skipping {source_file} cfs wetted area polygon creation.\n')
                    pass
