# Created wetted area shapefiles from WSE TIFF rasters in LYR17_Hydraulics folder and saves LYR17_Wetted_Polygon folder
# Created by SJP, last updated 06/24/21

import os
import arcpy
from arcpy.sa import *
import logging

# ****VARIABLES - MAKE CHANGES HERE****
discharges = [1000, 1250, 1500]
# Dictionary Key: 1: "Globaln_10ft", 2: "Globaln_3ft", 3: "Spatialn_10ft",
#                 4: "Spatialn_3ft", 5: "Combinedn_10ft", 6:"Combinedn_3ft"
mr = 1
# Reaches that will be iterated through, if you don't want all reaches to be included in calc - omit from list
# Full list: reaches = ["EDDPD", "DPDMRY", "MRYFR"]
reaches = ["EDDPD", "DPDMRY", "MRYFR"]


# DO NOT CHANGE SCRIPT BELOW UNLESS YOU KNOW WHAT YOU ARE DOING
# Set workspace file for ArcGIS, enable overwriting, and retrieve Spatial Analyst extension license
arcpy.env.workspace = os.path.abspath('')
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')

# logging format
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# dictionaries
reach_dict = {"EDDPD": 1, "DPDMRY": 2, "MRYFR": 3}
mannings_res_dict = {1: "Globaln_10ft", 2: "Globaln_3ft", 3: "Spatialn_10ft",
                     4: "Spatialn_3ft", 5: "Combinedn_10ft", 6:"Combinedn_3ft"}
par_folder_dict = {"u": "Velocity", "d": "Depth", "h": "WSE", "t": "BSS"}
par_ras_dict = {"V": "u", "d": "d", "h": "h", "BSS": "t"}

source_folder = "Z:\\LYR\\LYR_2017studies\\LYR17_Hydraulics"


def wetted_polygons():

    # call TIFF files from LYR17_Hydraulics\\LYR17_WSE folder
    hyd_file = f'h{q:06d}.tif'
    ras_path = f'{source_folder}\\LYR17_WSE\\{reach_dict[reach]}_{reach}\\{mannings_res_dict[mr]}'
    hyd_filename = os.path.join(ras_path, hyd_file)

    # if WSE TIFF file does not exist, will pass and move on to next discharge in list
    if not os.path.exists(hyd_filename):
        logging.info(f'ERROR: {hyd_filename} does not exist, skipping to next discharge...\n')
        return None

    else:
        # define temp folder for integer raster to be saved in
        temp_folder = f'{source_folder}\\LYR17_Wetted_Polygon\\{reach_dict[reach]}_{reach}\\{mannings_res_dict[mr]}\\temp'
        # if temp folder doesn't exist, creates one
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
            logging.info(f'Created temp folder: {temp_folder} \n')

        # define integer raster filename and location
        int_file = f'w{q:06d}_integer.tif'
        int_filename = os.path.join(temp_folder, int_file)

        # define wetted area and dissolved wetted area shapefile name and location
        wp_file = f'w{q:06d}_wettedarea.shp'
        wp_path = f'{source_folder}\\LYR17_Wetted_Polygon\\{reach_dict[reach]}_{reach}\\{mannings_res_dict[mr]}'
        wp_dissolved_file = f'w{q:06d}_wettedarea_dissolved.shp'
        wp_shpfile = os.path.join(wp_path, wp_file)
        wp_dissolved_shpfile = os.path.join(wp_path, wp_dissolved_file)

        # check if wetted area dissolved shapefile exists
        if os.path.exists(wp_dissolved_shpfile):
            logging.info(f'Wetted area dissolved shapefile exists, skipping to next discharge...\n')
            return None
        else:
            # if subfolder doesn't exist, creates one
            if not os.path.exists(wp_path):
                os.makedirs(wp_path)
                logging.info(f'Created {wp_path} folder.\n')

            logging.info(f'Creating wetted area shapefiles from: ..\\{reach_dict[reach]}_{reach}\\{mannings_res_dict[mr]}\\h{q:06d}.tif\n')

            logging.info(f'Creating integer raster...')
            int_raster = Con(Raster(hyd_filename), 1)
            int_raster.save(int_filename)
            logging.info(f'Integer raster created: {int_filename}\n')

            logging.info(f'Converting integer raster to wetted area polygon shapefile... ')
            arcpy.RasterToPolygon_conversion(int_filename, wp_shpfile, 'NO_SIMPLIFY', 'VALUE')
            logging.info(f'Wetted area polygon shapefile created: {wp_shpfile}\n')

            logging.info(f'Aggregating features of GRIDCODE field and dissolving lines into single feature...')
            arcpy.Dissolve_management(wp_shpfile, wp_dissolved_shpfile, ['GRIDCODE'], None, 'MULTI_PART', 'DISSOLVE_LINES')
            logging.info(f'Wetted area dissolved shapefile created: {wp_dissolved_shpfile}\n')

if __name__ == '__main__':
    for q in discharges:
        for reach in reaches:
            try:
                wetted_polygons()
            except:
                pass