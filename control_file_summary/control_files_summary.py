# Python script for summarizing control file information into CSV tables for recording in the modeling log
# Last updated on 01/24/21 by SJP

# Step 1 - copy this script for use into your review folder
# Step 2 - set the ..\\DOMAIN\\model folder, the ..\\DOMAIN\\run folder, and the ..\\DOMAIN\\review folder
# Step 3 - check the CSV files created in the review folder and copy to the modeling log worksheet


import os
import pandas as pd

import logging
FORMAT = ">>> %(filename)s, ln %(lineno)s - %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# VARIABLES - MAKE CHANGES HERE (set folders)
# example: 'Z:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_1_EDDPD\\model'
model_folder = 'FILE PATH'
# example: 'Z:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_1_EDDPD\\runs'
runs_folder = 'FILE PATH'
# example: 'Z:\\LYR\\LYR_2017studies\\LYR17_2Dmodelling\\LYR17_1_EDDPD\\review'
review_folder = 'FILE PATH'

# Define paths of output files
tgc_summary = 'tgc_summary_review.csv'
tgc_log_path = os.path.join(review_folder, tgc_summary)
tbc_summary = 'tbc_summary_review.csv'
tbc_log_path = os.path.join(review_folder, tbc_summary)
tcf_summary = 'tcf_summary_review.csv'
tcf_log_path = os.path.join(review_folder, tcf_summary)


# handles adding entries to each log file
def add_log(log_path, df):
    log_type = os.path.basename(log_path)[:3]
    if not add_log.has_been_called[log_type]:
        if os.path.exists(log_path):
            os.remove(log_path)
        df.to_csv(log_path, index=False, header=True, mode='w')
    else:
        df.to_csv(log_path, index=False, header=False, mode='a')
    add_log.has_been_called[log_type] = True
add_log.has_been_called = {'tgc': False, 'tbc': False, 'tcf': False}


# read .tgc and record information to csv
def log_tgc(tgc_filename, *args, **kwargs):
    get_strs = {'READ GIS LOCATION': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'Read GRID Zpts': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'Read GIS Code': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'Read GIS Mat': lambda line, get_str: line.split(get_str)[1].replace('\n', '')
                }
    out_dict = {get_str: '' for get_str in get_strs.keys()}
    with open(tgc_filename) as f:
        lines = f.readlines()
        for line in lines:
            for get_str in get_strs.keys():
                if get_str in line:
                    data = get_strs[get_str](line, get_str + ' ==')
                    out_dict[get_str] = [data]
                    logging.info(f'Got {get_str} = {data}')

    log_df = pd.DataFrame.from_dict(out_dict)
    log_df = log_df.reindex(['READ GIS LOCATION', 'Read GRID Zpts', 'Read GIS Code', 'Read GIS Mat'], axis='columns')

    # add column with the run ID
    run_id = tgc_filename.split('_')[-2]
    log_df.insert(loc=0, column='Run ID', value=[run_id])

    add_log(tgc_log_path, log_df)
    logging.info('\nsaved tgc GIS files table: %s\n' % tgc_log_path)


# read .tbc and record information to csv
def log_tbc(tbc_filename, *args, **kwargs):
    get_strs = {'Read GIS BC': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'Read GIS SA': lambda line, get_str: line.split(get_str)[1].replace('\n', '')
                }
    out_dict = {get_str: '' for get_str in get_strs.keys()}
    with open(tbc_filename) as f:
        lines = f.readlines()
        for line in lines:
            for get_str in get_strs.keys():
                if get_str in line:
                        data = get_strs[get_str](line, get_str + ' ==')
                        out_dict[get_str] = [data]
                        logging.info(f'Got {get_str} = {data}')

    log_df = pd.DataFrame.from_dict(out_dict)
    log_df = log_df.reindex(['Read GIS BC', 'Read GIS SA'], axis='columns')

    # add column with the run ID
    run_id = tbc_filename.split('_')[-2]
    log_df.insert(loc=0, column='Run ID', value=[run_id])

    add_log(tbc_log_path, log_df)
    logging.info('\nsaved tbc GIS files table: %s\n' % tbc_log_path)


# read .tcf and record information to csv
def log_tcf(tcf_filename, *args, **kwargs):
    get_strs = {'Read GIS PO': lambda line, get_str: line.split(get_str)[1].split(' !')[0],
                'Viscosity Formulation': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'Viscosity Coefficients': lambda line, get_str: line.split(get_str)[1].replace('\n', ''),
                'Cell Wet/Dry Depth': lambda line, get_str: line.split(get_str)[1].split(' !')[0]
                }
    out_dict = {get_str: '' for get_str in get_strs.keys()}
    with open(tcf_filename) as f:
        lines = f.readlines()
        for line in lines:
            for get_str in get_strs.keys():
                if get_str in line:
                        data = get_strs[get_str](line, get_str + ' ==')
                        if out_dict[get_str] != '':
                            # if get_str occurs twice (Read GIS PO), make second column
                            out_dict[get_str + '_2'] = [data]
                        else:
                            out_dict[get_str] = [data]
                        logging.info(f'Got {get_str} = {data}')

    log_df = pd.DataFrame.from_dict(out_dict)
    log_df = log_df.reindex(['Read GIS PO', 'Read GIS PO_2', 'Viscosity Formulation', 'Viscosity Coefficients', 'Cell Wet/Dry Depth'], axis='columns')

    # add column with the run ID
    run_id = tcf_filename.split('_')[-2]
    log_df.insert(loc=0, column='Run ID', value=[run_id])

    add_log(tcf_log_path, log_df)
    logging.info('\nsaved tcf GIS files table: %s\n' % tcf_log_path)


if __name__ == "__main__":
    for dir, subdirs, files in os.walk(model_folder):
        for control_file in files:
            control_filename = os.path.join(dir, control_file)  # path of control file in the model or run folder
            # for .tgc file
            if control_file.endswith('.tgc'):
                logging.info('Collecting GIS file information from TGC file...')
                log_tgc(tgc_filename=control_filename)
            # for .tbc file
            if control_file.endswith('.tbc'):
                logging.info('Collecting GIS file information from TBC file...')
                log_tbc(tbc_filename=control_filename)

    for dir, subdirs, files in os.walk(runs_folder):
        for control_file in files:
            control_filename = os.path.join(dir, control_file)  # path of control file in the model or run folder
            # for .tcf file
            if control_file.endswith('.tcf'):
                logging.info('Collecting information from TCF file...')
                log_tcf(tcf_filename=control_filename)
