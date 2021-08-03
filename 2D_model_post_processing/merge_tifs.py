# Combines TIFF rasters in LYR17_Hydraulics folder and saves merged TIFF raster in 0_Merged subfolder
# Created by SJP, last updated 06/24/21

import os
import arcpy
import logging

# ****VARIABLES - MAKE CHANGES HERE****
discharges = [42200, 47166, 62550, 74445, 84400, 87100, 92591, 106445, 110400]
# Dictionary Key: 1: "Globaln_10ft", 2: "Globaln_3ft", 3: "Spatialn_10ft",
#                 4: "Spatialn_3ft", 5: "Combinedn_10ft", 6:"Combinedn_3ft"
mr = 5


# DO NOT CHANGE SCRIPT BELOW UNLESS YOU KNOW WHAT YOU ARE DOING
# Set workspace file for ArcGIS, enable overwriting, and retrieve Spatial Analyst extension license
arcpy.env.workspace = os.path.abspath('')
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
arcpy.env.snapRaster = 'Z:\\LYR\\LYR_2017studies\\LYR17_Topo\\LYR17_DEM\\09-Final_2017_DEM\\With_Structures\\LYR17_Final_DEM_with_str_adjusted.tif'

# logging format
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# dictionaries
mannings_res_dict = {1: "Globaln_10ft", 2: "Globaln_3ft", 3: "Spatialn_10ft",
                     4: "Spatialn_3ft", 5: "Combinedn_10ft", 6:"Combinedn_3ft"}
par_folder_dict = {"u": "Velocity", "d": "Depth", "h": "WSE", "t": "BSS"}
par_ras_dict = {"V": "u", "d": "d", "h": "h", "BSS": "t"}

source_folder = "Z:\\LYR\\LYR_2017studies\\LYR17_Hydraulics"


def merge_hydraulic_rasters():
    # hydraulic raster filename and merged raster filename
    filename = f'{par}{q:06d}.tif'
    merged = f'{source_folder}\\LYR17_{par_folder_dict[par]}\\0_Merged\\{mannings_res_dict[mr]}'
    merged_filename = os.path.join(merged, filename)

    # if merged file exists, will skip and move on to the next discharge
    if os.path.exists(merged_filename):
        logging.info(f'Merged TIFF file exists, skipping {merged_filename}...\n')
        return None
    else:
        # define hydraulic rasters for discharge for each reach
        logging.info(f'Loading {filename} for each reach...')
        eddpd = f'{source_folder}\\LYR17_{par_folder_dict[par]}\\1_EDDPD\\{mannings_res_dict[mr]}\\{filename}'
        dpdmry = f'{source_folder}\\LYR17_{par_folder_dict[par]}\\2_DPDMRY\\{mannings_res_dict[mr]}\\{filename}'
        mryfr = f'{source_folder}\\LYR17_{par_folder_dict[par]}\\3_MRYFR\\{mannings_res_dict[mr]}\\{filename}'

        # if subfolder doesn't exist, creates one
        if not os.path.exists(merged):
            os.makedirs(merged)
            logging.info(f'Created {merged} folder.')

        # set cell size for Mosaic To New Raster
        logging.info(f'Determining cell size for raster merge...')
        res_10ft = (1, 3, 5)
        if mr in res_10ft:
            cellsize = 10
            logging.info(f'Cell size set to {cellsize} ft\n')
        else:
            cellsize = 3
            logging.info(f'Cell size set to {cellsize} ft\n')

        # Process: Mosaic To New Raster (Mosaic To New Raster) (management)
        logging.info(f'Merging: {eddpd} \n'
                     f'                                                             {dpdmry}\n'
                     f'                                                             {mryfr}\n')
        merged_ras = arcpy.management.MosaicToNewRaster(input_rasters=[eddpd, dpdmry, mryfr],
                                                        output_location=merged,
                                                        raster_dataset_name_with_extension=filename,
                                                        coordinate_system_for_the_raster="",
                                                        pixel_type="32_BIT_FLOAT", cellsize=cellsize,
                                                        number_of_bands=1, mosaic_method="FIRST",
                                                        mosaic_colormap_mode="FIRST")[0]
        merged_ras = arcpy.Raster(merged_ras)
        logging.info(f'Merged {par_folder_dict[par]} rasters: {merged_ras}\n')

if __name__ == '__main__':
    # iterate through parameters (velocity, depth, WSE, BSS)
    for par in par_ras_dict.values():
        # iterate through discharge list
        for q in discharges:
            try:
                merge_hydraulic_rasters()
            except:
                logging.info(f'Missing hydraulic TIFF files, skipping {q} cfs merge.\n')
                pass
